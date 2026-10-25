import os
from pathlib import Path
from dotenv import load_dotenv

DIRETORIO_BASE     = Path(__file__).resolve().parents[2]
DIRETORIO_DADOS     = DIRETORIO_BASE / "data"
CAMINHO_PDF_FAQ_SOLICITANTE = DIRETORIO_DADOS / "Questionário_Modelos_classicos.pdf"
CAMINHO_PDF_FAQ_TECNICO = DIRETORIO_DADOS / "Questionário_Modelos_classicos.pdf"
CAMINHO_PDF_FAQ_GESTOR = DIRETORIO_DADOS / "Questionário_Modelos_classicos.pdf"


load_dotenv(DIRETORIO_BASE / ".env")

GEMINI_CHAVE_API = os.getenv("GEMINI_API_KEY")
OPENAI_CHAVE_API = os.getenv("OPENAI_API_KEY")
FIXA_URL_BASE_API = os.getenv("FIXA_API_BASE_URL")

# ==================== CONFIGURAÇÕES DO POSTGRES ====================
BANCO_URL_SOLICITANTE = os.getenv("DATABASE_URL_SOLICITANTE")
BANCO_URL_TECNICO = os.getenv("DATABASE_URL_TECNICO")
BANCO_URL_GESTOR = os.getenv("DATABASE_URL_GESTOR")
# ================== FIM DAS CONFIGURAÇÕES DO POSTGRES ==================

# ==================== CONFIGURAÇÕES DO QDRANT ====================
QDRANT_CHAVE_API = os.getenv("QDRANT_API_KEY")
QDRANT_URL = os.getenv("QDRANT_URL")
QDRANT_TIMEOUT_SECONDS = float(os.getenv("QDRANT_TIMEOUT_SECONDS", "30"))
QDRANT_COLECAO_CATEGORIA = "categoria_equipamento"
QDRANT_COLECAO_LOCAL = "local_unidade"
QDRANT_COLECOES_OPERACIONAIS = frozenset({
    "problema", "ocorrencia", "ordem_servico", "tarefa",
    "observacao_conclusao", "evento", "equipamento", "modelo_equipamento",
    "categoria_equipamento", "marca_equipamento", QDRANT_COLECAO_LOCAL,
})
QDRANT_COLECAO_FAQ = "faq_fixa"
QDRANT_COLECAO_HISTORICO = "resumo_historico"
QDRANT_CAMPO_UNIDADE = "unidade_id"
QDRANT_CAMPO_ENTIDADE_ID = "entidade_id"
QDRANT_CAMPO_TEXTO = "texto"
QDRANT_CAMPO_ATIVO = "esta_ativo"
QDRANT_NOME_VETOR = None
QDRANT_ESPACO_NOMES_PONTOS = "6ba7b811-9dad-11d1-80b4-00c04fd430c8"
MODELO_VETORIZACAO = "gemini-embedding-2-preview"
MODELO_VETORIZACAO_OPERACIONAL = "text-embedding-3-small"
DIMENSOES_VETORIZACAO_OPERACIONAL = 768
DIMENSOES_VETORIZACAO_FAQ = 768
LIMITE_BUSCA_VETORIAL = 4
LIMIAR_PONTUACAO_VETORIAL = 0.20
# ================== FIM DAS CONFIGURAÇÕES DO QDRANT ==================

# ==================== CONFIGURAÇÕES DO MONGO ====================
MONGODB_URI = os.getenv("MONGO_URI")
MONGO_COLECAO_SESSOES = "sessoes"
MONGO_BANCO_DADOS = "fixa_inteligencia_artificial"
# ================== FIM DAS CONFIGURAÇÕES DO MONGO ==================

# ==================== OBSERVABILIDADE ====================
OBSERVABILIDADE_MENSAGENS_SEMANAIS_USUARIO = float(
    os.getenv("OBSERVABILITY_WEEKLY_MESSAGES_PER_USER", "4")
)
OBSERVABILIDADE_TOKENS_ESTIMADOS_ENTRADA_MENSAGEM = int(
    os.getenv("OBSERVABILITY_ESTIMATED_INPUT_TOKENS_PER_MESSAGE", "6000")
)
OBSERVABILIDADE_TOKENS_ESTIMADOS_SAIDA_MENSAGEM = int(
    os.getenv("OBSERVABILITY_ESTIMATED_OUTPUT_TOKENS_PER_MESSAGE", "1600")
)
OBSERVABILIDADE_OPENAI_ENTRADA_USD_MILHAO = float(
    os.getenv("OBSERVABILITY_OPENAI_INPUT_USD_PER_MILLION", "0.10")
)
OBSERVABILIDADE_OPENAI_SAIDA_USD_MILHAO = float(
    os.getenv("OBSERVABILITY_OPENAI_OUTPUT_USD_PER_MILLION", "0.50")
)
OBSERVABILIDADE_GROQ_ENTRADA_USD_MILHAO = float(
    os.getenv("OBSERVABILITY_GROQ_INPUT_USD_PER_MILLION", "0")
)
OBSERVABILIDADE_GROQ_SAIDA_USD_MILHAO = float(
    os.getenv("OBSERVABILITY_GROQ_OUTPUT_USD_PER_MILLION", "0")
)
# Deixe vazio até definir quanto vale financeiramente uma resolução.
OBSERVABILIDADE_VALOR_RESOLUCAO_BRL = os.getenv(
    "OBSERVABILITY_VALUE_PER_RESOLUTION_BRL", ""
).strip()
OBSERVABILIDADE_REAIS_DOLAR = float(os.getenv("OBSERVABILITY_BRL_PER_USD") or "0")
# ================== FIM DAS CONFIGURAÇÕES DE OBSERVABILIDADE ==================

# =================== CONFIGURAÇÕES DO JUIZ ====================
TYPESAFE_API_KEY = os.getenv("TYPESAFE_API_KEY")
JEV_URL = "https://api.typesafe.ai/v1/systemone"
JEV_MODELO = os.getenv("JEV_MODEL", "jev-latest")
LIMIAR = 0.20
# ================= FIM DAS CONFIGURAÇÕES DO JUIZ ==================

OBRIGATORIAS = {
    "GEMINI_API_KEY": GEMINI_CHAVE_API,
    "OPENAI_API_KEY": OPENAI_CHAVE_API,
    "TYPESAFE_API_KEY": TYPESAFE_API_KEY,
    "DATABASE_URL_SOLICITANTE": BANCO_URL_SOLICITANTE,
    "DATABASE_URL_TECNICO": BANCO_URL_TECNICO,
    "DATABASE_URL_GESTOR": BANCO_URL_GESTOR,
    "MONGODB_URI":    MONGODB_URI,
    "QDRANT_API_KEY": QDRANT_CHAVE_API,
    "QDRANT_URL":     QDRANT_URL,
}


def validar_configuracao() -> list[str]:
    """Devolve a lista de problemas de configuração (vazia = tudo certo)."""
    problemas = []
    for nome, valor in OBRIGATORIAS.items():
        if not valor:
            problemas.append(f"Variável ausente no .env: {nome}")
    return problemas
