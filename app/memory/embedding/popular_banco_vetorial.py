"""
Script de ingestão do FAQ no Qdrant.

Lê o PDF, faz split em chunks, gera embeddings e insere na collection
configurada no Qdrant, separando os trechos por perfil. Para atualizar os três PDFs:

    python -m app.main

Cada ingestão substitui somente os pontos do perfil informado.
"""

import uuid
from pathlib import Path
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from qdrant_client import models

from app.memory.embedding.config import gerar_embeddings_documentos
from app.core.clients.qdrant import abrir_cliente_qdrant
from app.core.config import QDRANT_FAQ_COLLECTION

CHUNK_SIZE    = 700
CHUNK_OVERLAP = 150
BATCH_SIZE    = 50


async def ingerir_faq(pdf_path: str | Path, perfil: str) -> int:
    """Indexa o PDF de um perfil, preservando os pontos dos outros perfis."""
    perfil = perfil.lower()

    if perfil not in {"solicitante", "tecnico", "gestor"}:
        raise ValueError("Perfil de FAQ inválido.")
    
    pdf_path = Path(pdf_path)

    async with abrir_cliente_qdrant() as qdrant:
        print(f"[ingest] Carregando PDF de {perfil}: {pdf_path}")
        loader = PyPDFLoader(str(pdf_path))
        docs = loader.load()
        print(f"[ingest] {len(docs)} página(s) carregada(s)")

        splitter = RecursiveCharacterTextSplitter(
            chunk_size=CHUNK_SIZE,
            chunk_overlap=CHUNK_OVERLAP,
        )
        chunks = splitter.split_documents(docs)
        print(f"[ingest] {len(chunks)} chunk(s) gerado(s)")

        if not chunks:
            raise ValueError("O PDF não contém trechos para indexar; os dados existentes foram preservados.")
        
        await qdrant.create_payload_index(
            collection_name=QDRANT_FAQ_COLLECTION,
            field_name="perfil",
            field_schema=models.PayloadSchemaType.KEYWORD,
            wait=True,
        )
        
        print(f"[ingest] Substituindo pontos do perfil {perfil}...")
        await qdrant.delete(
            collection_name=QDRANT_FAQ_COLLECTION,
            points_selector=models.FilterSelector(
                filter=models.Filter(must=[models.FieldCondition(
                    key="perfil", match=models.MatchValue(value=perfil),
                )])
            ),
            wait=True,
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
                        "perfil": perfil,
                        "page_number":  chunk.metadata.get("page", 0),
                        "source":       pdf_path.name,
                    },
                )
                for vetor, chunk in zip(vetores, lote_chunks)
            ]

            await qdrant.upsert(collection_name=QDRANT_FAQ_COLLECTION, points=pontos, wait=True)

        print(f"[ingest] Concluído! {len(chunks)} chunk(s) indexado(s) no Qdrant.")
        return len(chunks)


