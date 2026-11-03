import os
from pathlib import Path
from dotenv import load_dotenv
from app.observability import configurar_somente_metricas

# DIRETORIO_BASE: Local de recurso usado pela configuração e pelos comandos operacionais.
DIRETORIO_BASE     = Path(__file__).resolve().parents[2]
# DIRETORIO_DADOS: Local de recurso usado pela configuração e pelos comandos operacionais.
DIRETORIO_DADOS     = DIRETORIO_BASE / "data"
# CAMINHO_PDF_FAQ_SOLICITANTE: Local de recurso usado pela configuração e pelos comandos operacionais.
CAMINHO_PDF_FAQ_SOLICITANTE = DIRETORIO_DADOS / "Questionário_Modelos_classicos.pdf"
# CAMINHO_PDF_FAQ_TECNICO: Local de recurso usado pela configuração e pelos comandos operacionais.
CAMINHO_PDF_FAQ_TECNICO = DIRETORIO_DADOS / "Questionário_Modelos_classicos.pdf"
# CAMINHO_PDF_FAQ_GESTOR: Local de recurso usado pela configuração e pelos comandos operacionais.
CAMINHO_PDF_FAQ_GESTOR = DIRETORIO_DADOS / "Questionário_Modelos_classicos.pdf"


load_dotenv(DIRETORIO_BASE / ".env")


configurar_somente_metricas()

# OPENAI_CHAVE_API: Recurso compartilhado de openai chave api usado pelas funções deste módulo e pela interface pública.
OPENAI_CHAVE_API = os.getenv("OPENAI_API_KEY")
# FIXA_URL_BASE_API: Recurso compartilhado de fixa url base api usado pelas funções deste módulo e pela interface pública.
FIXA_URL_BASE_API = os.getenv("FIXA_API_BASE_URL")

# ==================== CONFIGURAÇÕES DO DATABRICKS ====================
DATABRICKS_HOST = os.getenv("DATABRICKS_HOST")
# DATABRICKS_TOKEN: Recurso compartilhado de databricks token usado pelas funções deste módulo e pela interface pública.
DATABRICKS_TOKEN = os.getenv("DATABRICKS_TOKEN")
# DATABRICKS_WAREHOUSE_ID: Recurso compartilhado de databricks warehouse id usado pelas funções deste módulo e pela interface pública.
DATABRICKS_WAREHOUSE_ID = os.getenv("DATABRICKS_WAREHOUSE_ID")
# ================== FIM DAS CONFIGURAÇÕES DO DATABRICKS ==================

# ==================== CONFIGURAÇÕES DO POSTGRES ====================
BANCO_URL_SOLICITANTE = os.getenv("DATABASE_URL_SOLICITANTE")
# BANCO_URL_TECNICO: Recurso compartilhado de banco url tecnico usado pelas funções deste módulo e pela interface pública.
BANCO_URL_TECNICO = os.getenv("DATABASE_URL_TECNICO")
# BANCO_URL_GESTOR: Recurso compartilhado de banco url gestor usado pelas funções deste módulo e pela interface pública.
BANCO_URL_GESTOR = os.getenv("DATABASE_URL_GESTOR")
# ================== FIM DAS CONFIGURAÇÕES DO POSTGRES ==================

# ==================== CONFIGURAÇÕES DO QDRANT ====================
QDRANT_CHAVE_API = os.getenv("QDRANT_API_KEY")
# QDRANT_URL: Recurso compartilhado de qdrant url usado pelas funções deste módulo e pela interface pública.
QDRANT_URL = os.getenv("QDRANT_URL")
# QDRANT_COLECAO_CATEGORIA: Valor de referência de qdrant colecao categoria usado neste módulo e por seus consumidores.
QDRANT_COLECAO_CATEGORIA = "categoria_equipamento"
# QDRANT_COLECAO_LOCAL: Valor de referência de qdrant colecao local usado neste módulo e por seus consumidores.
QDRANT_COLECAO_LOCAL = "local_unidade"
# QDRANT_COLECOES_OPERACIONAIS: Recurso compartilhado de qdrant colecoes operacionais usado pelas funções deste módulo e pela interface pública.
QDRANT_COLECOES_OPERACIONAIS = frozenset({
    "problema", "ocorrencia", "ordem_servico", "tarefa",
    "observacao_conclusao", "evento", "equipamento", "modelo_equipamento",
    "categoria_equipamento", "marca_equipamento", QDRANT_COLECAO_LOCAL,
})
# QDRANT_COLECAO_FAQ: Valor de referência de qdrant colecao faq usado neste módulo e por seus consumidores.
QDRANT_COLECAO_FAQ = "faq_fixa"
# QDRANT_COLECAO_HISTORICO: Valor de referência de qdrant colecao historico usado neste módulo e por seus consumidores.
QDRANT_COLECAO_HISTORICO = "resumo_historico"
# QDRANT_CAMPO_UNIDADE: Valor de referência de qdrant campo unidade usado neste módulo e por seus consumidores.
QDRANT_CAMPO_UNIDADE = "unidade_id"
# QDRANT_CAMPO_ENTIDADE_ID: Valor de referência de qdrant campo entidade id usado neste módulo e por seus consumidores.
QDRANT_CAMPO_ENTIDADE_ID = "entidade_id"
# QDRANT_CAMPO_TEXTO: Valor de referência de qdrant campo texto usado neste módulo e por seus consumidores.
QDRANT_CAMPO_TEXTO = "texto"
# QDRANT_CAMPO_ATIVO: Valor de referência de qdrant campo ativo usado neste módulo e por seus consumidores.
QDRANT_CAMPO_ATIVO = "esta_ativo"
# QDRANT_NOME_VETOR: Recurso compartilhado de qdrant nome vetor usado pelas funções deste módulo e pela interface pública.
QDRANT_NOME_VETOR = None
# QDRANT_ESPACO_NOMES_PONTOS: Valor de referência de qdrant espaco nomes pontos usado neste módulo e por seus consumidores.
QDRANT_ESPACO_NOMES_PONTOS = "6ba7b811-9dad-11d1-80b4-00c04fd430c8"
# DIMENSOES_VETORIZACAO_OPERACIONAL: Recurso compartilhado de dimensoes vetorizacao operacional usado pelas funções deste módulo e pela interface pública.
DIMENSOES_VETORIZACAO_OPERACIONAL = 768
# DIMENSOES_VETORIZACAO_FAQ: Recurso compartilhado de dimensoes vetorizacao faq usado pelas funções deste módulo e pela interface pública.
DIMENSOES_VETORIZACAO_FAQ = 768
# LIMITE_BUSCA_VETORIAL: Limite operacional/contratual usado pela validação e pelo processamento deste módulo.
LIMITE_BUSCA_VETORIAL = 4
# LIMIAR_PONTUACAO_VETORIAL: Recurso compartilhado de limiar pontuacao vetorial usado pelas funções deste módulo e pela interface pública.
LIMIAR_PONTUACAO_VETORIAL = 0.20
# ================== FIM DAS CONFIGURAÇÕES DO QDRANT ==================

# ==================== CONFIGURAÇÕES DO MONGO ====================
MONGODB_URI = os.getenv("MONGO_URI")
# MONGO_COLECAO_SESSOES: Valor de referência de mongo colecao sessoes usado neste módulo e por seus consumidores.
MONGO_COLECAO_SESSOES = "sessoes"
# MONGO_BANCO_DADOS: Valor de referência de mongo banco dados usado neste módulo e por seus consumidores.
MONGO_BANCO_DADOS = "fixa_inteligencia_artificial"
# ================== FIM DAS CONFIGURAÇÕES DO MONGO ==================

# ==================== OBSERVABILIDADE ====================
OBSERVABILIDADE_MENSAGENS_SEMANAIS_USUARIO = float(
    os.getenv("OBSERVABILITY_WEEKLY_MESSAGES_PER_USER", "4")
)
# OBSERVABILIDADE_TOKENS_ESTIMADOS_ENTRADA_MENSAGEM: Recurso compartilhado de observabilidade tokens estimados entrada mensagem usado pelas funções deste módulo e pela interface pública.
OBSERVABILIDADE_TOKENS_ESTIMADOS_ENTRADA_MENSAGEM = int(
    os.getenv("OBSERVABILITY_ESTIMATED_INPUT_TOKENS_PER_MESSAGE", "6000")
)
# OBSERVABILIDADE_TOKENS_ESTIMADOS_SAIDA_MENSAGEM: Recurso compartilhado de observabilidade tokens estimados saida mensagem usado pelas funções deste módulo e pela interface pública.
OBSERVABILIDADE_TOKENS_ESTIMADOS_SAIDA_MENSAGEM = int(
    os.getenv("OBSERVABILITY_ESTIMATED_OUTPUT_TOKENS_PER_MESSAGE", "1600")
)
# OBSERVABILIDADE_OPENAI_ENTRADA_USD_MILHAO: Recurso compartilhado de observabilidade openai entrada usd milhao usado pelas funções deste módulo e pela interface pública.
OBSERVABILIDADE_OPENAI_ENTRADA_USD_MILHAO = float(
    os.getenv("OBSERVABILITY_OPENAI_INPUT_USD_PER_MILLION", "0.10")
)
# OBSERVABILIDADE_OPENAI_SAIDA_USD_MILHAO: Recurso compartilhado de observabilidade openai saida usd milhao usado pelas funções deste módulo e pela interface pública.
OBSERVABILIDADE_OPENAI_SAIDA_USD_MILHAO = float(
    os.getenv("OBSERVABILITY_OPENAI_OUTPUT_USD_PER_MILLION", "0.50")
)
# OBSERVABILIDADE_GROQ_ENTRADA_USD_MILHAO: Recurso compartilhado de observabilidade groq entrada usd milhao usado pelas funções deste módulo e pela interface pública.
OBSERVABILIDADE_GROQ_ENTRADA_USD_MILHAO = float(
    os.getenv("OBSERVABILITY_GROQ_INPUT_USD_PER_MILLION", "0")
)
# OBSERVABILIDADE_GROQ_SAIDA_USD_MILHAO: Recurso compartilhado de observabilidade groq saida usd milhao usado pelas funções deste módulo e pela interface pública.
OBSERVABILIDADE_GROQ_SAIDA_USD_MILHAO = float(
    os.getenv("OBSERVABILITY_GROQ_OUTPUT_USD_PER_MILLION", "0")
)
# Deixe vazio até definir quanto vale financeiramente uma resolução.
OBSERVABILIDADE_VALOR_RESOLUCAO_BRL = os.getenv(
    "OBSERVABILITY_VALUE_PER_RESOLUTION_BRL", ""
).strip()
# OBSERVABILIDADE_REAIS_DOLAR: Recurso compartilhado de observabilidade reais dolar usado pelas funções deste módulo e pela interface pública.
OBSERVABILIDADE_REAIS_DOLAR = float(os.getenv("OBSERVABILITY_BRL_PER_USD") or "0")
# ================== FIM DAS CONFIGURAÇÕES DE OBSERVABILIDADE ==================

# =================== CONFIGURAÇÕES DO JUIZ ====================
TYPESAFE_API_KEY = os.getenv("TYPESAFE_API_KEY")
# JEV_URL: Valor de referência de jev url usado neste módulo e por seus consumidores.
JEV_URL = "https://api.typesafe.ai/v1/systemone"
# JEV_MODELO: Recurso compartilhado de jev modelo usado pelas funções deste módulo e pela interface pública.
JEV_MODELO = os.getenv("JEV_MODEL", "jev-latest")
# LIMIAR: Recurso compartilhado de limiar usado pelas funções deste módulo e pela interface pública.
LIMIAR = 0.20
# ================= FIM DAS CONFIGURAÇÕES DO JUIZ ==================

# ================== CONFIGURAÇÕES DO PECHINCHA ====================
URL_PECHINCHA = "https://pechincha.ai/mcp"
# VERSAO_PROTOCOLO: Valor de referência de versao protocolo usado neste módulo e por seus consumidores.
VERSAO_PROTOCOLO = "2025-03-26"
# ================= FIM DAS CONFIGURAÇÕES DO PECHINCHA ==================

# OBRIGATORIAS: Recurso compartilhado de obrigatorias usado pelas funções deste módulo e pela interface pública.
OBRIGATORIAS = {
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
