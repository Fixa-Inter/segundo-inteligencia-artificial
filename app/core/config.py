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
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
FIXA_API_BASE_URL = os.getenv("FIXA_API_BASE_URL")

# ==================== CONFIGURAÇÕES DO POSTGRES ====================
DATABASE_URL_SOLICITANTE = os.getenv("DATABASE_URL_SOLICITANTE")
DATABASE_URL_TECNICO = os.getenv("DATABASE_URL_TECNICO")
DATABASE_URL_GESTOR = os.getenv("DATABASE_URL_GESTOR")
# ================== FIM DAS CONFIGURAÇÕES DO POSTGRES ==================

# ==================== CONFIGURAÇÕES DO QDRANT ====================
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")
QDRANT_URL = os.getenv("QDRANT_URL")
QDRANT_CATEGORIA_COLLECTION = "categoria_equipamento"
QDRANT_LOCAL_COLLECTION = "local_endereco"
QDRANT_FAQ_COLLECTION = "faq_fixa"
QDRANT_HISTORICO_COLLECTION = "resumo_historico"
QDRANT_TENANT_FIELD = "cnpj_endereco"
QDRANT_CATEGORIA_ID_FIELD = "categoria_equipamento_id"
QDRANT_LOCAL_ID_FIELD = "local_endereco_id"
QDRANT_DESCRIPTION_FIELD = "descricao"
QDRANT_VECTOR_NAME = None
QDRANT_POINT_NAMESPACE = "6ba7b811-9dad-11d1-80b4-00c04fd430c8"
EMBEDDING_MODEL = "gemini-embedding-2-preview"
EMBEDDING_DIMENSIONS_EQUIPAMENTO_LOCAL = 768
EMBEDDING_DIMENSIONS_FAQ = 768
VECTOR_SEARCH_LIMIT = 4
VECTOR_SCORE_THRESHOLD = 0.20
# ================== FIM DAS CONFIGURAÇÕES DO QDRANT ==================

# ==================== CONFIGURAÇÕES DO MONGO ====================
MONGODB_URI = os.getenv("MONGO_URI")
MONGO_COLLECTION_SESSOES = "sessoes"
MONGO_BANCO_DADOS = "fixa_inteligencia_artificial"
# ================== FIM DAS CONFIGURAÇÕES DO MONGO ==================

# ==================== OBSERVABILIDADE ====================
OBSERVABILITY_WEEKLY_MESSAGES_PER_USER = float(
    os.getenv("OBSERVABILITY_WEEKLY_MESSAGES_PER_USER", "4")
)
OBSERVABILITY_ESTIMATED_INPUT_TOKENS_PER_MESSAGE = int(
    os.getenv("OBSERVABILITY_ESTIMATED_INPUT_TOKENS_PER_MESSAGE", "6000")
)
OBSERVABILITY_ESTIMATED_OUTPUT_TOKENS_PER_MESSAGE = int(
    os.getenv("OBSERVABILITY_ESTIMATED_OUTPUT_TOKENS_PER_MESSAGE", "1600")
)
OBSERVABILITY_OPENAI_INPUT_USD_PER_MILLION = float(
    os.getenv("OBSERVABILITY_OPENAI_INPUT_USD_PER_MILLION", "0.10")
)
OBSERVABILITY_OPENAI_OUTPUT_USD_PER_MILLION = float(
    os.getenv("OBSERVABILITY_OPENAI_OUTPUT_USD_PER_MILLION", "0.50")
)
OBSERVABILITY_GROQ_INPUT_USD_PER_MILLION = float(
    os.getenv("OBSERVABILITY_GROQ_INPUT_USD_PER_MILLION", "0")
)
OBSERVABILITY_GROQ_OUTPUT_USD_PER_MILLION = float(
    os.getenv("OBSERVABILITY_GROQ_OUTPUT_USD_PER_MILLION", "0")
)
# Deixe vazio até definir quanto vale financeiramente uma resolução.
OBSERVABILITY_VALUE_PER_RESOLUTION_BRL = os.getenv(
    "OBSERVABILITY_VALUE_PER_RESOLUTION_BRL", ""
).strip()
OBSERVABILITY_BRL_PER_USD = float(os.getenv("OBSERVABILITY_BRL_PER_USD") or "0")
# ================== FIM DAS CONFIGURAÇÕES DE OBSERVABILIDADE ==================


OBRIGATORIAS = {
    "GEMINI_API_KEY": GEMINI_API_KEY,
    "GROQ_API_KEY":   GROQ_API_KEY,
    "OPENAI_API_KEY": OPENAI_API_KEY,
    "DATABASE_URL_SOLICITANTE": DATABASE_URL_SOLICITANTE,
    "DATABASE_URL_TECNICO": DATABASE_URL_TECNICO,
    "DATABASE_URL_GESTOR": DATABASE_URL_GESTOR,
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
