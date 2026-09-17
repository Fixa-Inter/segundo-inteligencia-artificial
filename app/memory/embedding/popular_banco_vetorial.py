"""
Script de ingestão do FAQ no Qdrant.

Lê o PDF, faz split em chunks, gera embeddings e insere na collection
"faq_chunks" do Qdrant. Deve ser executado UMA VEZ (ou sempre que o PDF mudar):

    python -m app.ingest_faq

Ele limpa a collection antes de reinserir, então é seguro rodar várias vezes.
"""

import uuid
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from qdrant_client import models

from app.core.config import FAQ_PDF_PATH
from app.memory.embedding.config import gerar_embeddings_documentos
from app.memory.vectorSearch.cliente import abrir_cliente_qdrant
from app.core.config import QDRANT_FAQ_COLLECTION

CHUNK_SIZE    = 700
CHUNK_OVERLAP = 150
BATCH_SIZE    = 50


async def ingerir_faq() -> int:
    """Indexa o PDF do FAQ no Qdrant. Retorna o número de chunks inseridos."""
    async with abrir_cliente_qdrant() as qdrant:
        print(f"[ingest] Carregando PDF: {FAQ_PDF_PATH}")
        loader = PyPDFLoader(str(FAQ_PDF_PATH))
        docs = loader.load()
        print(f"[ingest] {len(docs)} página(s) carregada(s)")

        splitter = RecursiveCharacterTextSplitter(
            chunk_size=CHUNK_SIZE,
            chunk_overlap=CHUNK_OVERLAP,
        )
        chunks = splitter.split_documents(docs)
        print(f"[ingest] {len(chunks)} chunk(s) gerado(s)")

        info = await qdrant.get_collection(QDRANT_FAQ_COLLECTION)
        if info.points_count > 0:
            print(f"[ingest] Limpando {info.points_count} ponto(s) existente(s)...")
            await qdrant.delete(
                collection_name=QDRANT_FAQ_COLLECTION,
                points_selector=models.FilterSelector(
                    filter=models.Filter(must=[])
                ),
            )

        textos = [chunk.page_content for chunk in chunks]

        for i in range(0, len(textos), BATCH_SIZE):
            lote_textos = textos[i : i + BATCH_SIZE]
            lote_chunks = chunks[i : i + BATCH_SIZE]

            print(f"[ingest] Gerando embeddings para chunk {i+1}–{i+len(lote_textos)}...")
            vetores = await gerar_embeddings_documentos(lote_textos)

            pontos = [
                models.PointStruct(
                    id=str(uuid.uuid4()),
                    vector=vetor,
                    payload={
                        "page_content": chunk.page_content,
                        "page_number":  chunk.metadata.get("page", 0),
                        "source":       str(chunk.metadata.get("source", "")),
                    },
                )
                for vetor, chunk in zip(vetores, lote_chunks)
            ]

            await qdrant.upsert(collection_name=QDRANT_FAQ_COLLECTION, points=pontos)

        print(f"[ingest] Concluído! {len(chunks)} chunk(s) indexado(s) no Qdrant.")
        return len(chunks)


if __name__ == "__main__":
    ingerir_faq()