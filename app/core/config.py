import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR     = Path(__file__).resolve().parents[2]
DATA_DIR     = BASE_DIR / "data"
FAQ_PDF_SOLICITANTE_PATH = DATA_DIR / "Questionário_Modelos_classicos.pdf"
FAQ_PDF_TECNICO_PATH = DATA_DIR / "Questionário_Modelos_classicos.pdf"
FAQ_PDF_GESTOR_PATH = DATA_DIR / "Questionário_Modelos_classicos.pdf"


load_dotenv(BASE_DIR / ".env")

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GROQ_API_KEY   = os.getenv("GROQ_API_KEY")
DATABASE_URL   = os.getenv("DATABASE_URL")
MONGODB_URI    = os.getenv("MONGODB_URI", "mongodb://localhost:27017")

FIXA_API_BASE_URL = os.getenv("FIXA_API_BASE_URL")

# ==================== CONFIGURAÇÕES DO QDRANT ====================
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")
QDRANT_URL = os.getenv("QDRANT_URL")
QDRANT_CATEGORIA_COLLECTION = "categoria_equipamento"
QDRANT_LOCAL_COLLECTION = "local_endereco"
QDRANT_FAQ_COLLECTION = "faq_fixa"
QDRANT_TENANT_FIELD = "cnpj_endereco"
QDRANT_CATEGORIA_ID_FIELD = "categoria_equipamento_id"
QDRANT_LOCAL_ID_FIELD = "local_endereco_id"
QDRANT_DESCRIPTION_FIELD = "descricao"
QDRANT_VECTOR_NAME = None
QDRANT_POINT_NAMESPACE = "6ba7b811-9dad-11d1-80b4-00c04fd430c8"
EMBEDDING_MODEL = "gemini-embedding-2-preview"
EMBEDDING_DIMENSIONS_EQUIPAMENTO_LOCAL = 768
EMBEDDING_DIMENSIONS_FAQ = 768
VECTOR_SEARCH_LIMIT = 3
VECTOR_SCORE_THRESHOLD = 0.80
# ================== FIM DAS CONFIGURAÇÕES DO QDRANT ==================

OBRIGATORIAS = {
    "GEMINI_API_KEY": GEMINI_API_KEY,
    "GROQ_API_KEY":   GROQ_API_KEY,
    "DATABASE_URL":   DATABASE_URL,
    "MONGODB_URI":    MONGODB_URI,
    "QDRANT_API_KEY": QDRANT_API_KEY,
    "QDRANT_URL":     QDRANT_URL,
}


def validar_config() -> list[str]:
    """Devolve a lista de problemas de configuração (vazia = tudo certo)."""
    problemas = []
    for nome, valor in OBRIGATORIAS.items():
        if not valor:
            problemas.append(f"Variável ausente no .env: {nome}")
    return problemas
