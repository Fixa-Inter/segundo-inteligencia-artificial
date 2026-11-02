"""Busca semântica própria e atualização transacional de solicitações pendentes."""

from sqlalchemy import text
from qdrant_client import models

from app.core import configuracao
from app.core.clients.postgres import executar_consulta, obter_motor
from app.core.clients.qdrant import abrir_cliente_qdrant
from app.core.respostas import MENSAGENS
from app.memory.embedding import gerar_vetor_operacional
from app.memory.vectorSearch.busca import _filtro, _registro
from app.services.ajuda_geral.edicoes import _sql_alvo, localizar_opcao
from app.services.gerais import obter_unidade_id
from app.schemas.imagem import validar_url_imagem


CAMPOS = {"titulo": 100, "descricao_problema": 255, "descricao_local": 255,
          "local_unidade_id": None, "categoria_equipamento_id": None}


def validar_alteracoes(alteracoes: dict) -> dict:
    if set(alteracoes) - CAMPOS.keys():
        raise ValueError(MENSAGENS["campo_nao_permitido_para_edicao"])
    for campo, valor in alteracoes.items():
        limite = CAMPOS[campo]
        if limite is None:
            if type(valor) is not int or valor <= 0:
                raise ValueError(MENSAGENS["o_id_do_registro_deve_ser_um_inteiro_positivo"])
        elif not isinstance(valor, str) or not valor.strip() or len(valor.strip()) > limite:
            raise ValueError(MENSAGENS["o_novo_valor_esta_vazio_ou_excede_o_limite_do_campo"])
    return {campo: valor.strip() if isinstance(valor, str) else valor for campo, valor in alteracoes.items()}


async def buscar_proprias_pendentes(usuario, descricao: str) -> list[dict]:
    if not descricao.strip() or len(descricao) > 500:
        raise ValueError(MENSAGENS["atualizacao_descricao_busca"])
    unidade = await obter_unidade_id(usuario)
    registros = await executar_consulta(usuario.tipo_acesso, """
        SELECT p.id, p.titulo, p.descricao_problema
        FROM problema p JOIN local_unidade local ON local.id = p.local_unidade_id
        WHERE p.usuario_id = :usuario_id AND p.status = 0 AND p.esta_ativo IS TRUE
          AND local.unidade_id = :unidade_id AND local.esta_ativo IS TRUE
    """, {"usuario_id": usuario.usuario_id, "unidade_id": unidade})
    por_id = {registro["id"]: registro for registro in registros}
    if not por_id:
        return []
    filtro = _filtro(unidade)
    filtro.must.append(models.FieldCondition(
        key=configuracao.QDRANT_CAMPO_ENTIDADE_ID, match=models.MatchAny(any=list(por_id)),
    ))
    async with abrir_cliente_qdrant() as cliente:
        resposta = await cliente.query_points(
            collection_name="problema", query=await gerar_vetor_operacional(descricao.strip()),
            using=configuracao.QDRANT_NOME_VETOR, query_filter=filtro, limit=5,
            score_threshold=configuracao.LIMIAR_PONTUACAO_VETORIAL,
            with_payload=True, with_vectors=False,
        )
    encontrados = {}
    for ponto in resposta.points:
        registro_id, _ = _registro(ponto, unidade)
        if registro_id not in por_id:
            raise PermissionError(MENSAGENS["registro_nao_encontrado_indisponivel_ou_sem_autorizacao"])
        encontrados[registro_id] = por_id[registro_id]
    return list(encontrados.values())


async def _ler(conexao, usuario, parametros, *, travar=False):
    sql = _sql_alvo("solicitacao", usuario)
    if travar:
        sql += " FOR UPDATE OF p"
    resultado = await conexao.execute(text(sql), parametros)
    linha = resultado.mappings().first()
    if linha is None:
        return None
    registro = dict(linha)
    fotos = await conexao.execute(text("""
        SELECT id, url FROM foto
        WHERE problema_id = :registro_id AND esta_ativo IS TRUE ORDER BY id
    """), parametros)
    registro["fotos"] = [dict(foto) for foto in fotos.mappings().all()]
    return registro


async def consultar_propria_pendente(usuario, registro_id: int) -> dict | None:
    unidade = await obter_unidade_id(usuario)
    async with obter_motor(usuario.tipo_acesso).connect() as conexao:
        return await _ler(conexao, usuario, {"registro_id": registro_id,
                         "usuario_id": usuario.usuario_id, "unidade_id": unidade})


def snapshot(registro: dict) -> dict:
    return {**{campo: registro[campo] for campo in CAMPOS}, "fotos": registro.get("fotos", [])}


async def atualizar_propria_pendente(usuario, dados: dict) -> dict | None:
    alteracoes = validar_alteracoes(dados["alteracoes"])
    imagens = list(dict.fromkeys(validar_url_imagem(url) for url in dados["imagens"]))
    acao = dados["acao_fotos"]
    if acao not in {"manter", "adicionar", "substituir"} or (imagens and acao == "manter") or (not imagens and acao != "manter"):
        raise ValueError(MENSAGENS["atualizacao_escolher_fotos"])
    unidade = await obter_unidade_id(usuario)
    parametros = {"registro_id": dados["registro_id"], "usuario_id": usuario.usuario_id, "unidade_id": unidade}
    # A trava e a comparação impedem sobrescrever uma proposta que ficou desatualizada.
    # Campos e vínculos de fotos são gravados ou revertidos juntos.
    async with obter_motor(usuario.tipo_acesso).begin() as conexao:
        atual = await _ler(conexao, usuario, parametros, travar=True)
        if atual is None or snapshot(atual) != dados["original"]:
            return None
        for campo in ("local_unidade_id", "categoria_equipamento_id"):
            if campo in alteracoes:
                destino = await localizar_opcao(usuario, campo, alteracoes[campo], conexao=conexao)
                if destino is None:
                    return None
        # Nomes de colunas vêm exclusivamente da lista fixa CAMPOS.
        atribuicoes = [f"{campo} = :novo_{campo}" for campo in alteracoes]
        atribuicoes.append("data_atualizacao = NOW()")
        parametros.update({f"novo_{campo}": valor for campo, valor in alteracoes.items()})
        await conexao.execute(text(
            "UPDATE problema SET " + ", ".join(atribuicoes)
            + " WHERE id = :registro_id AND usuario_id = :usuario_id AND status = 0"
        ), parametros)
        if acao == "substituir":
            # Somente os vínculos no banco; nenhum arquivo é removido do Cloudinary.
            await conexao.execute(text("DELETE FROM foto WHERE problema_id = :registro_id"), parametros)
        if acao in {"adicionar", "substituir"}:
            existentes = {foto["url"] for foto in atual["fotos"]} if acao == "adicionar" else set()
            for url in imagens:
                if url not in existentes:
                    await conexao.execute(text(
                        "INSERT INTO foto (problema_id, url) VALUES (:registro_id, :url)"
                    ), {"registro_id": dados["registro_id"], "url": url})
        return {"id": dados["registro_id"], "titulo": alteracoes.get("titulo", atual["titulo"])}
