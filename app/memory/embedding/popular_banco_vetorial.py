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

from app.memory.embedding.configuracao import gerar_vetores_documentos
from app.core.clients.qdrant import abrir_cliente_qdrant
from app.core.configuracao import QDRANT_COLECAO_FAQ

TAMANHO_TRECHO    = 700
SOBREPOSICAO_TRECHOS = 150
TAMANHO_LOTE    = 50


async def ingerir_faq(caminho_pdf: str | Path, perfil: str) -> int:
    """Indexa o PDF de um perfil, preservando os pontos dos outros perfis."""
    perfil = perfil.lower()

    if perfil not in {"solicitante", "tecnico", "gestor"}:
        raise ValueError("Perfil de FAQ inválido.")
    
    caminho_pdf = Path(caminho_pdf)

    async with abrir_cliente_qdrant() as qdrant:
        print(f"[ingest] Carregando PDF de {perfil}: {caminho_pdf}")
        carregador = PyPDFLoader(str(caminho_pdf))
        documentos = carregador.load()
        print(f"[ingest] {len(documentos)} página(s) carregada(s)")

        divisor = RecursiveCharacterTextSplitter(
            chunk_size=TAMANHO_TRECHO,
            chunk_overlap=SOBREPOSICAO_TRECHOS,
        )
        trechos = divisor.split_documents(documentos)
        print(f"[ingest] {len(trechos)} chunk(s) gerado(s)")

        if not trechos:
            raise ValueError("O PDF não contém trechos para indexar; os dados existentes foram preservados.")
        
        await qdrant.create_payload_index(
            collection_name=QDRANT_COLECAO_FAQ,
            field_name="perfil",
            field_schema=models.PayloadSchemaType.KEYWORD,
            wait=True,
        )
        
        print(f"[ingest] Substituindo pontos do perfil {perfil}...")
        await qdrant.delete(
            collection_name=QDRANT_COLECAO_FAQ,
            points_selector=models.FilterSelector(
                filter=models.Filter(must=[models.FieldCondition(
                    key="perfil", match=models.MatchValue(value=perfil),
                )])
            ),
            wait=True,
        )

        textos = [trecho.page_content for trecho in trechos]

        for i in range(0, len(textos), TAMANHO_LOTE):
            lote_textos = textos[i : i + TAMANHO_LOTE]
            lote_trechos = trechos[i : i + TAMANHO_LOTE]

            print(f"[ingest] Gerando embeddings para chunk {i+1}–{i+len(lote_textos)}...")
            vetores = await gerar_vetores_documentos(lote_textos)

            pontos = [
                models.PointStruct(
                    id=str(uuid.uuid4()),
                    vector=vetor,
                    payload={
                        "page_content": trecho.page_content,
                        "perfil": perfil,
                        "page_number":  trecho.metadata.get("page", 0),
                        "source":       caminho_pdf.name,
                    },
                )
                for vetor, trecho in zip(vetores, lote_trechos)
            ]

            await qdrant.upsert(collection_name=QDRANT_COLECAO_FAQ, points=pontos, wait=True)

        print(f"[ingest] Concluído! {len(trechos)} chunk(s) indexado(s) no Qdrant.")
        return len(trechos)


