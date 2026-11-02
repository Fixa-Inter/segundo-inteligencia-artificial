"""Busca registros do Qdrant dentro da unidade autenticada."""


import base64
import binascii
import json
import logging
from uuid import UUID

from qdrant_client import models

from app.core import configuracao
from app.core.clients.qdrant import abrir_cliente_qdrant
from app.core.clients.postgres import executar_consulta
from app.memory.embedding import gerar_vetor_operacional
from app.schemas import UsuarioContexto
from app.services.gerais import obter_unidade_id

from app.core.respostas import MENSAGENS
from app.graph.respostas_padrao import formatar_resposta


registrador = logging.getLogger(__name__)

COLECOES_PERMITIDAS = configuracao.QDRANT_COLECOES_OPERACIONAIS
COLECOES_SOLICITANTE = frozenset({
    "problema", configuracao.QDRANT_COLECAO_LOCAL, "modelo_equipamento",
    "categoria_equipamento", "marca_equipamento",
})
COLECAO_GLOBAL = "marca_equipamento"
LIMITE_SEMANTICO = 10
LIMITE_MULTIPLAS_COLECOES = 5
LIMITE_POR_COLECAO = 5
LIMITE_LISTAGEM = 20
LIMITE_LITERAL = 20
LIMITE_SEMELHANTES = 10
_CAMPOS_PAYLOAD = [
    configuracao.QDRANT_CAMPO_ENTIDADE_ID,
    configuracao.QDRANT_CAMPO_TEXTO,
    configuracao.QDRANT_CAMPO_ATIVO,
    configuracao.QDRANT_CAMPO_UNIDADE,
]


def _validar_colecao(usuario: UsuarioContexto, colecao: str) -> None:
    if type(colecao) is not str or colecao not in COLECOES_PERMITIDAS:
        raise ValueError(MENSAGENS['collection_nao_permitida'])
    if usuario.tipo_acesso == "solicitante" and colecao not in COLECOES_SOLICITANTE:
        raise PermissionError(MENSAGENS['seu_perfil_nao_pode_consultar_esta_collection'])


async def _filtro_usuario(usuario: UsuarioContexto, colecao: str, unidade_id: int):
    """Restringe problemas do solicitante aos registros criados por ele."""
    if usuario.tipo_acesso != "solicitante" or colecao != "problema":
        return None
    linhas = await executar_consulta(
        usuario.tipo_acesso,
        """
        SELECT p.id FROM problema AS p
        JOIN local_unidade AS local ON local.id = p.local_unidade_id
        WHERE p.usuario_id = :usuario_id AND local.unidade_id = :unidade_id
          AND p.esta_ativo IS TRUE AND local.esta_ativo IS TRUE
        """,
        {"usuario_id": usuario.usuario_id, "unidade_id": unidade_id},
    )
    ids = [linha["id"] for linha in linhas]
    if not ids:
        return []
    return models.FieldCondition(
        key=configuracao.QDRANT_CAMPO_ENTIDADE_ID,
        match=models.MatchAny(any=ids),
    )


def _validar_limite(limite: int, maximo: int) -> None:
    if type(limite) is not int or not 1 <= limite <= maximo:
        raise ValueError(formatar_resposta('limite_deve_estar_entre_1_e_valor_1', valor_1=maximo))


def _validar_texto(texto: str, maximo: int = 500) -> str:
    if type(texto) is not str or not 1 <= len(texto.strip()) <= maximo:
        raise ValueError(formatar_resposta('informe_texto_entre_1_e_valor_1_caracteres', valor_1=maximo))
    return texto.strip()


def _validar_usuario(usuario: UsuarioContexto) -> None:
    if not isinstance(usuario, UsuarioContexto) or usuario.tipo_acesso not in {
        "solicitante", "tecnico", "gestor", "administrador",
    }:
        raise PermissionError(MENSAGENS['contexto_de_autenticacao_invalido'])


def _filtro(colecao: str, unidade_id: int, *adicionais) -> models.Filter:
    condicoes = [models.FieldCondition(
        key=configuracao.QDRANT_CAMPO_ATIVO,
        match=models.MatchValue(value=True),
    )]
    if colecao != COLECAO_GLOBAL:
        condicoes.append(models.FieldCondition(
            key=configuracao.QDRANT_CAMPO_UNIDADE,
            match=models.MatchValue(value=unidade_id),
        ))
    condicoes.extend(condicao for condicao in adicionais if condicao is not None)
    return models.Filter(must=condicoes)


def _registro(colecao: str, ponto, unidade_id: int) -> dict:
    conteudo = ponto.payload or {}
    if conteudo.get(configuracao.QDRANT_CAMPO_ATIVO) is not True:
        raise RuntimeError(MENSAGENS['qdrant_retornou_um_registro_inativo'])
    if colecao != COLECAO_GLOBAL:
        valor_unidade = conteudo.get(configuracao.QDRANT_CAMPO_UNIDADE)
        if type(valor_unidade) is not int or valor_unidade != unidade_id:
            raise RuntimeError(MENSAGENS['qdrant_retornou_um_registro_fora_da_unidade'])
    entidade_id = conteudo.get(configuracao.QDRANT_CAMPO_ENTIDADE_ID)
    texto = conteudo.get(configuracao.QDRANT_CAMPO_TEXTO)
    if type(entidade_id) is not int or entidade_id <= 0:
        raise RuntimeError(MENSAGENS['qdrant_retornou_entidade_id_invalido'])
    if type(texto) is not str or not texto.strip():
        raise RuntimeError(MENSAGENS['qdrant_retornou_texto_vazio'])
    registro = {
        "collection": colecao,
        "entidade_id": entidade_id,
        "texto": texto.strip(),
    }
    pontuacao = getattr(ponto, "score", None)
    if pontuacao is not None:
        registro["pontuacao"] = float(pontuacao)
    return registro


def _resultado(registros: list[dict], *, cursor: str | None = None) -> dict:
    return {
        "status": "SUCESSO" if registros else "SEM_RESULTADO",
        "resultados": registros,
        "cursor_paginacao": cursor,
    }


def _erro(erro: Exception) -> dict:
    if isinstance(erro, PermissionError):
        status, mensagem = "ACESSO_NEGADO", str(erro)
    elif isinstance(erro, ValueError):
        status, mensagem = "ERRO_VALIDACAO", str(erro)
    else:
        registrador.exception("Falha ao consultar Qdrant no ajuda_geral")
        status, mensagem = "ERRO_FERRAMENTA", MENSAGENS['nao_foi_possivel_consultar_os_registros_agora']
    return {"status": status, "resultados": [], "cursor_paginacao": None, "mensagem": mensagem}


def _codificar_cursor(colecao: str, unidade_id: int, deslocamento) -> str | None:
    if deslocamento is None:
        return None
    if type(deslocamento) is not int:
        deslocamento = str(deslocamento)
    dados = {"c": colecao, "u": unidade_id, "o": deslocamento}
    return base64.urlsafe_b64encode(json.dumps(dados).encode()).decode().rstrip("=")


def _decodificar_cursor(cursor: str | None, colecao: str, unidade_id: int):
    if cursor is None:
        return None
    if type(cursor) is not str or not 1 <= len(cursor) <= 512:
        raise ValueError(MENSAGENS['cursor_de_paginacao_invalido'])
    try:
        dados = json.loads(base64.urlsafe_b64decode(cursor + "=" * (-len(cursor) % 4)))
        if (type(dados) is not dict or dados.get("c") != colecao
                or type(dados.get("u")) is not int or dados["u"] != unidade_id):
            raise ValueError
        deslocamento = dados.get("o")
        if type(deslocamento) is int and deslocamento >= 0:
            return deslocamento
        if type(deslocamento) is str:
            return str(UUID(deslocamento))
    except (ValueError, TypeError, UnicodeError, binascii.Error):
        pass
    raise ValueError(MENSAGENS['cursor_de_paginacao_invalido_para_esta_collection_e_unidade'])


async def buscar_semanticamente(
    usuario: UsuarioContexto, colecao: str, pergunta: str, limite: int,
) -> dict:
    try:
        _validar_usuario(usuario)
        _validar_colecao(usuario, colecao)
        _validar_limite(limite, LIMITE_SEMANTICO)
        pergunta = _validar_texto(pergunta)
        unidade_id = await obter_unidade_id(usuario)
        filtro_usuario = await _filtro_usuario(usuario, colecao, unidade_id)
        if filtro_usuario == []:
            return _resultado([])
        vetor = await gerar_vetor_operacional(pergunta)
        async with abrir_cliente_qdrant() as cliente:
            resposta = await cliente.query_points(
                collection_name=colecao,
                query=vetor,
                using=configuracao.QDRANT_NOME_VETOR,
                query_filter=_filtro(colecao, unidade_id, filtro_usuario),
                limit=limite,
                with_payload=_CAMPOS_PAYLOAD,
                with_vectors=False,
            )
        return _resultado([_registro(colecao, p, unidade_id) for p in resposta.points])
    except Exception as erro:
        return _erro(erro)


async def buscar_em_multiplas_colecoes(
    usuario: UsuarioContexto, colecoes: list[str], pergunta: str, limite_por_colecao: int,
) -> dict:
    try:
        _validar_usuario(usuario)
        if type(colecoes) is not list or not 1 <= len(colecoes) <= LIMITE_MULTIPLAS_COLECOES:
            raise ValueError(MENSAGENS['informe_entre_1_e_5_collections'])
        for colecao in colecoes:
            _validar_colecao(usuario, colecao)
        if len(set(colecoes)) != len(colecoes):
            raise ValueError(MENSAGENS['nao_repita_collections'])
        _validar_limite(limite_por_colecao, LIMITE_POR_COLECAO)
        pergunta = _validar_texto(pergunta)
        unidade_id = await obter_unidade_id(usuario)
        vetor = await gerar_vetor_operacional(pergunta)
        registros = []
        async with abrir_cliente_qdrant() as cliente:
            for colecao in colecoes:
                filtro_usuario = await _filtro_usuario(usuario, colecao, unidade_id)
                if filtro_usuario == []:
                    continue
                resposta = await cliente.query_points(
                    collection_name=colecao,
                    query=vetor,
                    using=configuracao.QDRANT_NOME_VETOR,
                    query_filter=_filtro(colecao, unidade_id, filtro_usuario),
                    limit=limite_por_colecao,
                    with_payload=_CAMPOS_PAYLOAD,
                    with_vectors=False,
                )
                registros.extend(_registro(colecao, p, unidade_id) for p in resposta.points)
        return _resultado(registros)
    except Exception as erro:
        return _erro(erro)


async def listar_registros(
    usuario: UsuarioContexto, colecao: str, cursor_paginacao: str | None, limite: int,
) -> dict:
    try:
        _validar_usuario(usuario)
        _validar_colecao(usuario, colecao)
        _validar_limite(limite, LIMITE_LISTAGEM)
        unidade_id = await obter_unidade_id(usuario)
        filtro_usuario = await _filtro_usuario(usuario, colecao, unidade_id)
        if filtro_usuario == []:
            return _resultado([])
        deslocamento = _decodificar_cursor(cursor_paginacao, colecao, unidade_id)
        async with abrir_cliente_qdrant() as cliente:
            pontos, proximo = await cliente.scroll(
                collection_name=colecao,
                scroll_filter=_filtro(colecao, unidade_id, filtro_usuario),
                offset=deslocamento,
                limit=limite,
                with_payload=_CAMPOS_PAYLOAD,
                with_vectors=False,
            )
        registros = [_registro(colecao, p, unidade_id) for p in pontos]
        return _resultado(registros, cursor=_codificar_cursor(colecao, unidade_id, proximo))
    except Exception as erro:
        return _erro(erro)


async def buscar_termo_literal(
    usuario: UsuarioContexto, colecao: str, termo: str, limite: int,
) -> dict:
    try:
        _validar_usuario(usuario)
        _validar_colecao(usuario, colecao)
        _validar_limite(limite, LIMITE_LITERAL)
        termo = _validar_texto(termo, 200)
        unidade_id = await obter_unidade_id(usuario)
        filtro_usuario = await _filtro_usuario(usuario, colecao, unidade_id)
        if filtro_usuario == []:
            return _resultado([])
        condicao = models.FieldCondition(
            key=configuracao.QDRANT_CAMPO_TEXTO,
            match=models.MatchPhrase(phrase=termo),
        )
        async with abrir_cliente_qdrant() as cliente:
            pontos, _ = await cliente.scroll(
                collection_name=colecao,
                scroll_filter=_filtro(colecao, unidade_id, condicao, filtro_usuario),
                limit=limite,
                with_payload=_CAMPOS_PAYLOAD,
                with_vectors=False,
            )
        return _resultado([_registro(colecao, p, unidade_id) for p in pontos])
    except Exception as erro:
        return _erro(erro)


async def buscar_textos_semelhantes(
    usuario: UsuarioContexto, colecao: str, entidade_id: int, limite: int,
) -> dict:
    try:
        _validar_usuario(usuario)
        _validar_colecao(usuario, colecao)
        if type(entidade_id) is not int or entidade_id <= 0:
            raise ValueError(MENSAGENS['entidade_id_deve_ser_um_inteiro_positivo'])
        _validar_limite(limite, LIMITE_SEMELHANTES)
        unidade_id = await obter_unidade_id(usuario)
        filtro_usuario = await _filtro_usuario(usuario, colecao, unidade_id)
        if filtro_usuario == []:
            return _resultado([])
        condicao_id = models.FieldCondition(
            key=configuracao.QDRANT_CAMPO_ENTIDADE_ID,
            match=models.MatchValue(value=entidade_id),
        )
        async with abrir_cliente_qdrant() as cliente:
            origem, _ = await cliente.scroll(
                collection_name=colecao,
                scroll_filter=_filtro(colecao, unidade_id, condicao_id, filtro_usuario),
                limit=2,
                with_payload=_CAMPOS_PAYLOAD,
                with_vectors=False,
            )
            if not origem:
                return _resultado([])
            if len(origem) != 1:
                raise RuntimeError(MENSAGENS['entidade_id_duplicado_nesta_collection'])
            _registro(colecao, origem[0], unidade_id)
            filtro = _filtro(colecao, unidade_id, filtro_usuario)
            resposta = await cliente.query_points(
                collection_name=colecao,
                query=origem[0].id,
                using=configuracao.QDRANT_NOME_VETOR,
                query_filter=models.Filter(
                    must=filtro.must,
                    must_not=[models.HasIdCondition(has_id=[origem[0].id])],
                ),
                limit=limite,
                with_payload=_CAMPOS_PAYLOAD,
                with_vectors=False,
            )
        return _resultado([_registro(colecao, p, unidade_id) for p in resposta.points])
    except Exception as erro:
        return _erro(erro)
