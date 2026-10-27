"""Métricas Prometheus da API e do fluxo multiagente."""

from __future__ import annotations

from contextvars import ContextVar

from prometheus_client import Counter, Gauge, Histogram, generate_latest

from app.core import configuracao


REQUISICOES_CONVERSA = Counter(
    "fixa_chat_requests_total", "Requisições de chat", ["outcome"]
)
DURACAO_RESPOSTA_CONVERSA = Histogram(
    "fixa_chat_response_seconds",
    "Tempo total de processamento do chat, em segundos",
    buckets=(0.1, 0.25, 0.5, 1, 2, 5, 10, 20, 30, 60, 120),
)
DURACAO_NO_GRAFO = Histogram(
    "fixa_graph_node_seconds",
    "Duração de cada nó do LangGraph, em segundos",
    ["node"],
    buckets=(0.01, 0.05, 0.1, 0.25, 0.5, 1, 2, 5, 10, 20, 60),
)
EXECUCOES_NO_GRAFO = Counter(
    "fixa_graph_node_runs_total", "Execuções de nós do LangGraph", ["node", "outcome"]
)
DURACAO_JEV = Histogram(
    "fixa_jev_request_seconds", "Duração das chamadas ao JEV", ["operation"],
    buckets=(0.05, 0.1, 0.25, 0.5, 1, 2, 5, 10, 30, 60),
)
REQUISICOES_JEV = Counter(
    "fixa_jev_requests_total", "Chamadas ao JEV", ["operation", "outcome"]
)
REQUISICOES_BUSCAZAP = Counter(
    "fixa_buscazap_requests_total", "Chamadas ao MCP BuscaZap", ["operation", "outcome"]
)
ACESSO_BUSCAZAP = Counter(
    "fixa_buscazap_access_total", "Sinais do tier usado pelo BuscaZap",
    ["credential_configured", "observed_tier"],
)
TOKENS_MODELO = Counter(
    "fixa_llm_tokens_total", "Tokens reportados pelos provedores de LLM", ["provider", "model", "kind"]
)
CUSTO_MODELO_USD = Counter(
    "fixa_llm_estimated_cost_usd_total", "Custo estimado das chamadas de LLM em USD", ["provider", "model"]
)
EXECUCOES_OPERACAO = Counter(
    "fixa_business_operations_total", "Resultado de operações de negócio", ["operation", "outcome"]
)
RESOLUCOES = Counter(
    "fixa_resolutions_total", "Ocorrências de manutenção registradas com sucesso"
)
CUSTO_RESOLUCAO_USD = Histogram(
    "fixa_resolution_request_cost_usd",
    "Custo de LLM da requisição que registrou uma ocorrência",
    buckets=(0.0001, 0.0005, 0.001, 0.0025, 0.005, 0.01, 0.025, 0.05, 0.1, 0.5, 1),
)
CUSTO_SEMANAL_ESTIMADO_USD = Gauge(
    "fixa_weekly_estimated_cost_usd",
    "Custo semanal projetado em USD para o cenário configurado",
    ["weekly_active_users"],
)
ROI_CONFIGURADO = Gauge(
    "fixa_roi_value_configured",
    "1 quando o valor financeiro por resolução está configurado; caso contrário 0",
)
VALOR_ROI_BRL = Gauge(
    "fixa_roi_value_per_resolution_brl",
    "Valor estimado em BRL atribuído a cada resolução",
)
REAIS_POR_DOLAR = Gauge("fixa_brl_per_usd", "Cotação BRL por USD usada no ROI")

# Cada chamada de chat mantém seu próprio custo, inclusive as chamadas do grafo.
_CUSTO_REQUISICAO_USD: ContextVar[float] = ContextVar("fixa_request_cost_usd", default=0.0)
_REQUISICAO_FALHOU: ContextVar[bool] = ContextVar("fixa_request_failed", default=False)
_RESOLUCOES_PENDENTES: ContextVar[int] = ContextVar("fixa_pending_resolutions", default=0)


def reiniciar_custo_requisicao() -> object:
    return _CUSTO_REQUISICAO_USD.set(0.0)


def restaurar_custo_requisicao(token: object) -> None:
    _CUSTO_REQUISICAO_USD.reset(token)  # type: ignore[arg-type]


def obter_custo_requisicao_usd() -> float:
    return _CUSTO_REQUISICAO_USD.get()


def reiniciar_resultado_requisicao() -> object:
    return _REQUISICAO_FALHOU.set(False)


def marcar_falha_requisicao() -> None:
    _REQUISICAO_FALHOU.set(True)


def requisicao_falhou() -> bool:
    return _REQUISICAO_FALHOU.get()


def restaurar_resultado_requisicao(token: object) -> None:
    _REQUISICAO_FALHOU.reset(token)  # type: ignore[arg-type]


def _preco_modelo(provedor: str, modelo: str) -> tuple[float, float]:
    if provedor == "openai" and modelo.startswith("gpt-6-luna"):
        return (
            configuracao.OBSERVABILIDADE_OPENAI_ENTRADA_USD_MILHAO,
            configuracao.OBSERVABILIDADE_OPENAI_SAIDA_USD_MILHAO,
        )
    if provedor == "groq":
        return (
            configuracao.OBSERVABILIDADE_GROQ_ENTRADA_USD_MILHAO,
            configuracao.OBSERVABILIDADE_GROQ_SAIDA_USD_MILHAO,
        )
    # Provedores/modelos sem tarifa configurada continuam com tokens medidos;
    # custo zero aqui significa "não precificado", não uso gratuito.
    return 0.0, 0.0


def registrar_uso_modelo(provedor: str, modelo: str, tokens_entrada: int, tokens_saida: int) -> None:
    provedor = (provedor or "unknown").lower()
    modelo = modelo or "unknown"
    tokens_entrada = max(0, int(tokens_entrada or 0))
    tokens_saida = max(0, int(tokens_saida or 0))
    if tokens_entrada:
        TOKENS_MODELO.labels(provedor, modelo, "input").inc(tokens_entrada)
    if tokens_saida:
        TOKENS_MODELO.labels(provedor, modelo, "output").inc(tokens_saida)
    tarifa_entrada, tarifa_saida = _preco_modelo(provedor, modelo)
    custo = (
        tokens_entrada * tarifa_entrada + tokens_saida * tarifa_saida
    ) / 1_000_000
    if custo:
        CUSTO_MODELO_USD.labels(provedor, modelo).inc(custo)
        _CUSTO_REQUISICAO_USD.set(_CUSTO_REQUISICAO_USD.get() + custo)


def registrar_resolucao() -> None:
    RESOLUCOES.inc()
    CUSTO_RESOLUCAO_USD.observe(obter_custo_requisicao_usd())


def reiniciar_resolucoes_pendentes() -> object:
    return _RESOLUCOES_PENDENTES.set(0)


def restaurar_resolucoes_pendentes(token: object) -> None:
    _RESOLUCOES_PENDENTES.reset(token)  # type: ignore[arg-type]


def adicionar_resolucao_pendente() -> None:
    _RESOLUCOES_PENDENTES.set(_RESOLUCOES_PENDENTES.get() + 1)


def finalizar_resolucoes() -> None:
    quantidade = _RESOLUCOES_PENDENTES.get()
    for _ in range(quantidade):
        registrar_resolucao()
    _RESOLUCOES_PENDENTES.set(0)


def registrar_operacao(operacao: str, resultado_operacao: str) -> None:
    EXECUCOES_OPERACAO.labels(operacao, resultado_operacao).inc()


def configurar_indicadores_cenarios() -> None:
    tarifa_entrada, tarifa_saida = _preco_modelo("openai", "gpt-6-luna")
    custo_mensagem = (
        configuracao.OBSERVABILIDADE_TOKENS_ESTIMADOS_ENTRADA_MENSAGEM * tarifa_entrada
        + configuracao.OBSERVABILIDADE_TOKENS_ESTIMADOS_SAIDA_MENSAGEM * tarifa_saida
    ) / 1_000_000
    for usuarios in (100, 1000):
        CUSTO_SEMANAL_ESTIMADO_USD.labels(str(usuarios)).set(
            usuarios * configuracao.OBSERVABILIDADE_MENSAGENS_SEMANAIS_USUARIO * custo_mensagem
        )

    try:
        valor_brl = float(configuracao.OBSERVABILIDADE_VALOR_RESOLUCAO_BRL)
    except (TypeError, ValueError):
        valor_brl = 0.0
    reais_por_dolar = configuracao.OBSERVABILIDADE_REAIS_DOLAR
    ROI_CONFIGURADO.set(1 if valor_brl > 0 and reais_por_dolar > 0 else 0)
    VALOR_ROI_BRL.set(valor_brl)
    REAIS_POR_DOLAR.set(reais_por_dolar)


def gerar_conteudo_prometheus() -> bytes:
    return generate_latest()


configurar_indicadores_cenarios()


try:
    from langchain_core.callbacks import BaseCallbackHandler

    class MonitorMetricas(BaseCallbackHandler):
        """Lê tokens devolvidos pelo modelo sem guardar prompts ou respostas."""
        run_inline = True

        def on_llm_end(self, response, **kwargs) -> None:
            resposta = response
            uso = {}
            provedor = "unknown"
            modelo = "unknown"
            saida_modelo = getattr(resposta, "llm_output", None) or {}
            if isinstance(saida_modelo, dict):
                uso = saida_modelo.get("token_usage") or saida_modelo.get("usage") or {}
                modelo = saida_modelo.get("model_name") or modelo
                provedor = saida_modelo.get("model_provider") or provedor

            for lista_geracoes in getattr(resposta, "generations", []) or []:
                for geracao in lista_geracoes:
                    mensagem = getattr(geracao, "message", None)
                    metadados = getattr(mensagem, "response_metadata", {}) or {}
                    provedor = metadados.get("model_provider") or provedor
                    modelo = metadados.get("model_name") or metadados.get("model") or modelo
                    uso = (
                        getattr(mensagem, "usage_metadata", None)
                        or metadados.get("token_usage")
                        or metadados.get("usage")
                        or uso
                    )
                    if uso:
                        break
                if uso:
                    break

            if not isinstance(uso, dict):
                return
            tokens_entrada = uso.get("input_tokens", uso.get("prompt_tokens", 0))
            tokens_saida = uso.get("output_tokens", uso.get("completion_tokens", 0))
            if provedor == "unknown":
                if modelo.startswith("gpt-"):
                    provedor = "openai"
                elif modelo.startswith("openai/gpt-oss-"):
                    provedor = "groq"
            registrar_uso_modelo(provedor, modelo, tokens_entrada, tokens_saida)

        def on_llm_error(self, error, **kwargs) -> None:
            # A chamada que falhou não tem token/custo reportado pelo provedor.
            return None

except ImportError:  # pragma: no cover - dependências da aplicação incluem LangChain.
    MonitorMetricas = None  # type: ignore[assignment,misc]
