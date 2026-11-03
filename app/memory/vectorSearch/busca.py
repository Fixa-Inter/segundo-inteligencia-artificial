from qdrant_client import AsyncQdrantClient, models
from app.core import configuracao
from app.memory.embedding import gerar_vetor_operacional

# _COLECOES_CADASTRO: Recurso compartilhado de colecoes cadastro usado pelas funções deste módulo e pela interface pública.
_COLECOES_CADASTRO = {
    configuracao.QDRANT_COLECAO_CATEGORIA,
    configuracao.QDRANT_COLECAO_LOCAL,
}


def _filtro(unidade_id: int, registro_id: int | None = None) -> models.Filter:
    """Compõe filtro de unidade/atividade e condições autorizadas da consulta. Usado por _buscar, validar_selecao."""
    if type(unidade_id) is not int or unidade_id <= 0:
        raise ValueError("Unidade autenticada inválida.")
    condicoes = [
        models.FieldCondition(
            key=configuracao.QDRANT_CAMPO_UNIDADE,
            match=models.MatchValue(value=unidade_id),
        ),
        models.FieldCondition(
            key=configuracao.QDRANT_CAMPO_ATIVO,
            match=models.MatchValue(value=True),
        ),
    ]
    if registro_id is not None:
        if type(registro_id) is not int or registro_id <= 0:
            raise ValueError("ID operacional inválido.")
        condicoes.append(models.FieldCondition(
            key=configuracao.QDRANT_CAMPO_ENTIDADE_ID,
            match=models.MatchValue(value=registro_id),
        ))
    return models.Filter(must=condicoes)


def _registro(ponto, unidade_id: int) -> tuple[int, str]:
    """Valida e projeta registro recuperado preservando escopo e campos esperados. Usado por _buscar, validar_selecao."""
    conteudo = ponto.payload or {}
    valor_unidade = conteudo.get(configuracao.QDRANT_CAMPO_UNIDADE)
    if type(valor_unidade) is not int or valor_unidade != unidade_id:
        raise ValueError("Resultado fora da unidade autenticada.")
    if conteudo.get(configuracao.QDRANT_CAMPO_ATIVO) is not True:
        raise ValueError("Resultado inativo.")
    registro_id = conteudo.get(configuracao.QDRANT_CAMPO_ENTIDADE_ID)
    texto = conteudo.get(configuracao.QDRANT_CAMPO_TEXTO)
    if type(registro_id) is not int or registro_id <= 0:
        raise ValueError("O payload deve conter entidade_id inteiro positivo.")
    if not isinstance(texto, str) or not texto.strip():
        raise ValueError("Texto ausente no payload.")
    return registro_id, texto.strip()


async def _buscar(
    colecao: str, texto: str, unidade_id: int, cliente: AsyncQdrantClient,
) -> dict[int, str]:
    """Executa a etapa buscar no escopo de busca. Usado por buscar_categoria_equipamento, buscar_local_endereco."""
    if colecao not in _COLECOES_CADASTRO:
        raise ValueError("Collection não permitida.")
    if not isinstance(texto, str) or not texto.strip() or not 1 <= configuracao.LIMITE_BUSCA_VETORIAL <= 20:
        raise ValueError("Informe uma descrição e um limite entre 1 e 20.")
    filtro = _filtro(unidade_id)
    vetor = await gerar_vetor_operacional(texto.strip())
    resultado = await cliente.query_points(
        collection_name=colecao,
        query=vetor,
        using=configuracao.QDRANT_NOME_VETOR,
        query_filter=filtro,
        limit=configuracao.LIMITE_BUSCA_VETORIAL,
        score_threshold=configuracao.LIMIAR_PONTUACAO_VETORIAL,
        with_payload=True,
        with_vectors=False,
    )
    registros = {}
    for ponto in resultado.points:
        registro_id, descricao = _registro(ponto, unidade_id)
        if registro_id in registros and registros[registro_id] != descricao:
            raise ValueError("ID operacional duplicado com textos diferentes.")
        registros[registro_id] = descricao
    return registros


async def buscar_categoria_equipamento(
    descricao: str, unidade_id: int, cliente: AsyncQdrantClient,
) -> dict[int, str]:
    """Pesquisa categorias ativas por significado dentro da unidade. Usado pelo fluxo de vectorSearch."""
    return await _buscar(configuracao.QDRANT_COLECAO_CATEGORIA, descricao, unidade_id, cliente)


async def buscar_local_endereco(
    descricao: str, unidade_id: int, cliente: AsyncQdrantClient,
) -> dict[int, str]:
    """Pesquisa locais ativos por significado dentro da unidade. Usado pelo fluxo de vectorSearch."""
    return await _buscar(configuracao.QDRANT_COLECAO_LOCAL, descricao, unidade_id, cliente)


async def validar_selecao(
    colecao: str, registro_id: int, unidade_id: int, cliente: AsyncQdrantClient,
) -> str:
    """Confere ID selecionado, unidade, atividade e descrição na coleção de cadastro. Usado pelo fluxo de vectorSearch."""
    if colecao not in _COLECOES_CADASTRO:
        raise ValueError("Collection não permitida.")
    pontos, _ = await cliente.scroll(
        collection_name=colecao,
        scroll_filter=_filtro(unidade_id, registro_id),
        limit=2,
        with_payload=True,
        with_vectors=False,
    )
    if len(pontos) != 1:
        raise ValueError("Cadastro indisponível. Consulte e confirme novamente.")
    return _registro(pontos[0], unidade_id)[1]
