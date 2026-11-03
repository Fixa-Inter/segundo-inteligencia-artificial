"""
Ingestão de um corpus Markdown/PDF por perfil no Qdrant.

Recebe todos os arquivos do perfil juntos para não substituir um documento por outro.
O comando python -m app.scripts.ingerir_faq seleciona as fontes de dados/.
"""

import uuid
from collections.abc import Iterable
from pathlib import Path
from langchain_core.documents import Document
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from qdrant_client import models
from app.memory.embedding import gerar_vetores_documentos
from app.core.clients import abrir_cliente_qdrant
from app.core import QDRANT_COLECAO_FAQ

# TAMANHO_TRECHO: Recurso compartilhado de tamanho trecho usado pelas funções deste módulo e pela interface pública.
TAMANHO_TRECHO    = 700
# SOBREPOSICAO_TRECHOS: Recurso compartilhado de sobreposicao trechos usado pelas funções deste módulo e pela interface pública.
SOBREPOSICAO_TRECHOS = 150
# TAMANHO_LOTE: Recurso compartilhado de tamanho lote usado pelas funções deste módulo e pela interface pública.
TAMANHO_LOTE    = 50


def carregar_documentos_faq(
    caminhos: str | Path | Iterable[str | Path],
) -> list[Document]:
    """Lê todas as fontes antes da gravação; aceita Markdown UTF-8 e mantém suporte a PDF."""
    entradas = [caminhos] if isinstance(caminhos, (str, Path)) else caminhos
    arquivos = tuple(dict.fromkeys(Path(caminho).resolve() for caminho in entradas))
    if not arquivos:
        raise ValueError("Informe ao menos um documento para indexar o FAQ.")

    documentos = []
    for caminho in arquivos:
        # Validação: uma fonte ausente, inválida ou vazia impede a substituição do corpus.
        if not caminho.is_file():
            raise FileNotFoundError(f"Documento de FAQ não encontrado: {caminho}")
        if caminho.suffix.lower() == ".md":
            paginas = [Document(page_content=caminho.read_text(encoding="utf-8-sig"))]
        elif caminho.suffix.lower() == ".pdf":
            paginas = PyPDFLoader(str(caminho)).load()
        else:
            raise ValueError(f"Formato de FAQ não suportado: {caminho.suffix}")
        if not any(pagina.page_content.strip() for pagina in paginas):
            raise ValueError(f"Documento de FAQ sem conteúdo: {caminho}")

        # Lógica: preserva a origem por arquivo e a página dos PDFs em cada trecho.
        for pagina in paginas:
            pagina.metadata["source"] = caminho.name
        documentos.extend(paginas)
    return documentos


async def ingerir_faq(
    caminho_pdf: str | Path | Iterable[str | Path], perfil: str,
) -> int:
    """Substitui o corpus completo do perfil; caminho_pdf mantém o nome legado, mas aceita vários arquivos."""
    perfil = perfil.strip().lower()

    # Validação: carrega o corpus e prepara todos os vetores antes de alterar o Qdrant.
    if perfil not in {"solicitante", "tecnico", "gestor"}:
        raise ValueError("Perfil de FAQ inválido.")
    documentos = carregar_documentos_faq(caminho_pdf)
    divisor = RecursiveCharacterTextSplitter(
        chunk_size=TAMANHO_TRECHO,
        chunk_overlap=SOBREPOSICAO_TRECHOS,
    )
    trechos = divisor.split_documents(documentos)
    if not trechos:
        raise ValueError("Os documentos não contêm trechos para indexar; os dados existentes foram preservados.")

    pontos = []
    for i in range(0, len(trechos), TAMANHO_LOTE):
        lote = trechos[i : i + TAMANHO_LOTE]
        print(f"[ingest] Gerando embeddings de {perfil}: {i + 1}–{i + len(lote)}...")
        vetores = await gerar_vetores_documentos([trecho.page_content for trecho in lote])
        if len(vetores) != len(lote):
            raise ValueError("Quantidade de embeddings incompatível com os trechos; o FAQ existente foi preservado.")
        pontos.extend(
            models.PointStruct(
                id=str(uuid.uuid4()),
                vector=vetor,
                payload={
                    "page_content": trecho.page_content,
                    "perfil": perfil,
                    "page_number": trecho.metadata.get("page", 0),
                    "source": trecho.metadata["source"],
                },
            )
            for vetor, trecho in zip(vetores, lote)
        )

    # Lógica: publica todos os lotes novos antes de remover os pontos antigos deste perfil.
    # Não é uma transação: uma falha de publicação/limpeza pode deixar versões coexistindo.
    async with abrir_cliente_qdrant() as qdrant:
        await qdrant.create_payload_index(
            collection_name=QDRANT_COLECAO_FAQ,
            field_name="perfil",
            field_schema=models.PayloadSchemaType.KEYWORD,
            wait=True,
        )
        for i in range(0, len(pontos), TAMANHO_LOTE):
            await qdrant.upsert(
                collection_name=QDRANT_COLECAO_FAQ,
                points=pontos[i : i + TAMANHO_LOTE],
                wait=True,
            )
        await qdrant.delete(
            collection_name=QDRANT_COLECAO_FAQ,
            points_selector=models.FilterSelector(filter=models.Filter(
                must=[models.FieldCondition(key="perfil", match=models.MatchValue(value=perfil))],
                must_not=[models.HasIdCondition(has_id=[ponto.id for ponto in pontos])],
            )),
            wait=True,
        )

    print(f"[ingest] Concluído! {len(trechos)} chunk(s) indexado(s) para {perfil}.")
    return len(trechos)
