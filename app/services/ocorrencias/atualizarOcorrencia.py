"""Busca e edição transacional de ocorrências próprias e ativas."""

from typing import get_args

from qdrant_client import models
from sqlalchemy import text

from app.core import configuracao
from app.core.clients.postgres import executar_consulta, obter_motor
from app.core.clients.qdrant import abrir_cliente_qdrant
from app.core.respostas import MENSAGENS
from app.memory.embedding import gerar_vetor_operacional
from app.memory.vectorSearch.busca import _filtro, _registro
from app.schemas import UsuarioContexto
from app.schemas.imagem import validar_url_imagem
from app.services.ajuda_geral.edicoes import _sql_alvo, localizar_opcao
from app.services.gerais import obter_unidade_id
from app.services.ordensServico.buscarOrdensServico import CATEGORIA_PROBLEMA_POR_ID, PRIORIDADE_POR_ID
from app.tools.toolsRequest.CriarOcorrenciaEntrada import CategoriaProblema, Prioridade


PERFIS = {"tecnico", "gestor", "administrador"}
CAMPOS = {"titulo": 100, "descricao_ocorrencia": 255, "descricao_local": 255,
          "local_unidade_id": None, "categoria_equipamento_id": None,
          "categoria_problema": None, "prioridade": None}
ENUMS = {"categoria_problema": {nome: indice for indice, nome in enumerate(get_args(CategoriaProblema), 1)},
         "prioridade": {nome: indice for indice, nome in enumerate(get_args(Prioridade))}}


def validar_usuario(usuario: UsuarioContexto) -> None:
    if usuario.tipo_acesso not in PERFIS:
        raise PermissionError(MENSAGENS["perfil_sem_permissao_para_ocorrencias"])


def validar_alteracoes(alteracoes: dict) -> dict:
    if set(alteracoes) - CAMPOS.keys():
        raise ValueError(MENSAGENS["campo_nao_permitido_para_edicao"])
    dados = {}
    for campo, valor in alteracoes.items():
        if campo in ENUMS:
            mapa = ENUMS[campo]
            if isinstance(valor, str):
                valor = mapa.get(valor)
            if type(valor) is not int or valor not in mapa.values():
                raise ValueError(MENSAGENS["ocorrencia_atualizacao_enum_invalido"])
        elif CAMPOS[campo] is None:
            if type(valor) is not int or valor <= 0:
                raise ValueError(MENSAGENS["o_id_do_registro_deve_ser_um_inteiro_positivo"])
        elif not isinstance(valor, str) or not valor.strip() or len(valor.strip()) > CAMPOS[campo]:
            raise ValueError(MENSAGENS["o_novo_valor_esta_vazio_ou_excede_o_limite_do_campo"])
        dados[campo] = valor.strip() if isinstance(valor, str) else valor
    return dados


def rotulos_enums(dados: dict) -> dict:
    return {"categoria_problema": CATEGORIA_PROBLEMA_POR_ID[dados["categoria_problema"]],
            "prioridade": PRIORIDADE_POR_ID[dados["prioridade"]]}


async def buscar_proprias_ativas(usuario: UsuarioContexto, descricao: str) -> list[dict]:
    validar_usuario(usuario)
    if not descricao.strip() or len(descricao) > 500:
        raise ValueError(MENSAGENS["ocorrencia_atualizacao_descricao_busca"])
    unidade = await obter_unidade_id(usuario)
    registros = await executar_consulta(usuario.tipo_acesso, """
        SELECT o.id, o.titulo, o.descricao_ocorrencia
        FROM ocorrencia o JOIN local_unidade local ON local.id = o.local_unidade_id
        WHERE o.usuario_id = :usuario_id AND o.esta_ativo IS TRUE
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
            collection_name="ocorrencia", query=await gerar_vetor_operacional(descricao.strip()),
            using=configuracao.QDRANT_NOME_VETOR, query_filter=filtro, limit=5,
            score_threshold=configuracao.LIMIAR_PONTUACAO_VETORIAL, with_payload=True, with_vectors=False,
        )
    encontrados = {}
    for ponto in resposta.points:
        identificador, _ = _registro(ponto, unidade)
        if identificador not in por_id:
            raise PermissionError(MENSAGENS["registro_nao_encontrado_indisponivel_ou_sem_autorizacao"])
        encontrados[identificador] = por_id[identificador]
    return list(encontrados.values())


async def _ler(conexao, usuario, parametros, *, travar=False):
    sql = _sql_alvo("ocorrencia", usuario)
    if travar:
        sql += " FOR UPDATE OF o"
    resultado = await conexao.execute(text(sql), parametros)
    linha = resultado.mappings().first()
    if linha is None:
        return None
    registro = dict(linha)
    fotos = await conexao.execute(text("""
        SELECT id, url FROM foto
        WHERE ocorrencia_id = :registro_id AND esta_ativo IS TRUE ORDER BY id
    """), parametros)
    registro["fotos"] = [dict(foto) for foto in fotos.mappings().all()]
    return registro


async def consultar_propria_ativa(usuario: UsuarioContexto, registro_id: int) -> dict | None:
    validar_usuario(usuario)
    unidade = await obter_unidade_id(usuario)
    async with obter_motor(usuario.tipo_acesso).connect() as conexao:
        return await _ler(conexao, usuario, {"registro_id": registro_id,
                         "usuario_id": usuario.usuario_id, "unidade_id": unidade})


def snapshot(registro: dict) -> dict:
    return {**{campo: registro[campo] for campo in CAMPOS}, "fotos": registro.get("fotos", [])}


async def atualizar_propria_ativa(usuario: UsuarioContexto, dados: dict) -> dict | None:
    validar_usuario(usuario)
    alteracoes = validar_alteracoes(dados["alteracoes"])
    imagens = list(dict.fromkeys(validar_url_imagem(url) for url in dados["imagens"]))
    acao = dados["acao_fotos"]
    if acao not in {"manter", "adicionar", "substituir"} or (imagens and acao == "manter") or (not imagens and acao != "manter"):
        raise ValueError(MENSAGENS["ocorrencia_atualizacao_escolher_fotos"])
    unidade = await obter_unidade_id(usuario)
    parametros = {"registro_id": dados["registro_id"], "usuario_id": usuario.usuario_id, "unidade_id": unidade}
    # A mesma trava protege a conferência, os campos e a troca dos vínculos de fotos.
    async with obter_motor(usuario.tipo_acesso).begin() as conexao:
        atual = await _ler(conexao, usuario, parametros, travar=True)
        if atual is None or snapshot(atual) != dados["original"]:
            return None
        for campo in ("local_unidade_id", "categoria_equipamento_id"):
            if campo in alteracoes and await localizar_opcao(usuario, campo, alteracoes[campo], conexao=conexao) is None:
                return None
        # Os nomes das colunas vêm da lista fixa CAMPOS; os valores são parâmetros.
        atribuicoes = [f"{campo} = :novo_{campo}" for campo in alteracoes] + ["data_atualizacao = NOW()"]
        parametros.update({f"novo_{campo}": valor for campo, valor in alteracoes.items()})
        resultado = await conexao.execute(text(
            "UPDATE ocorrencia SET " + ", ".join(atribuicoes)
            + " WHERE id = :registro_id AND usuario_id = :usuario_id AND esta_ativo IS TRUE RETURNING id"
        ), parametros)
        if resultado.first() is None:
            return None
        if acao == "substituir":
            # Exclusão dos vínculos no PostgreSQL, sem chamadas ao Cloudinary.
            await conexao.execute(text("DELETE FROM foto WHERE ocorrencia_id = :registro_id"), parametros)
        if acao in {"adicionar", "substituir"}:
            existentes = {foto["url"] for foto in atual["fotos"]} if acao == "adicionar" else set()
            for url in imagens:
                if url not in existentes:
                    await conexao.execute(text(
                        "INSERT INTO foto (ocorrencia_id, url) VALUES (:registro_id, :url)"
                    ), {"registro_id": dados["registro_id"], "url": url})
        return {"id": dados["registro_id"], "titulo": alteracoes.get("titulo", atual["titulo"])}
