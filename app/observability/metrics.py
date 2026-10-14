"""Métricas Prometheus da API e do fluxo multiagente."""

from __future__ import annotations

from contextvars import ContextVar

from prometheus_client import Counter, Gauge, Histogram, generate_latest

from app.core import config


CHAT_REQUESTS = Counter(
    "fixa_chat_requests_total", "Requisições de chat", ["outcome"]
)
CHAT_RESPONSE_SECONDS = Histogram(
    "fixa_chat_response_seconds",
    "Tempo total de processamento do chat, em segundos",
    buckets=(0.1, 0.25, 0.5, 1, 2, 5, 10, 20, 30, 60, 120),
)
GRAPH_NODE_SECONDS = Histogram(
    "fixa_graph_node_seconds",
    "Duração de cada nó do LangGraph, em segundos",
    ["node"],
    buckets=(0.01, 0.05, 0.1, 0.25, 0.5, 1, 2, 5, 10, 20, 60),
)
GRAPH_NODE_RUNS = Counter(
    "fixa_graph_node_runs_total", "Execuções de nós do LangGraph", ["node", "outcome"]
)
LLM_TOKENS = Counter(
    "fixa_llm_tokens_total", "Tokens reportados pelos provedores de LLM", ["provider", "model", "kind"]
)
LLM_COST_USD = Counter(
    "fixa_llm_estimated_cost_usd_total", "Custo estimado das chamadas de LLM em USD", ["provider", "model"]
)
OPERATION_RUNS = Counter(
    "fixa_business_operations_total", "Resultado de operações de negócio", ["operation", "outcome"]
)
RESOLUTIONS = Counter(
    "fixa_resolutions_total", "Ocorrências de manutenção registradas com sucesso"
)
RESOLUTION_COST_USD = Histogram(
    "fixa_resolution_request_cost_usd",
    "Custo de LLM da requisição que registrou uma ocorrência",
    buckets=(0.0001, 0.0005, 0.001, 0.0025, 0.005, 0.01, 0.025, 0.05, 0.1, 0.5, 1),
)
WEEKLY_ESTIMATED_COST_USD = Gauge(
    "fixa_weekly_estimated_cost_usd",
    "Custo semanal projetado em USD para o cenário configurado",
    ["weekly_active_users"],
)
ROI_CONFIGURED = Gauge(
    "fixa_roi_value_configured",
    "1 quando o valor financeiro por resolução está configurado; caso contrário 0",
)
ROI_VALUE_BRL = Gauge(
    "fixa_roi_value_per_resolution_brl",
    "Valor estimado em BRL atribuído a cada resolução",
)
BRL_PER_USD = Gauge("fixa_brl_per_usd", "Cotação BRL por USD usada no ROI")

# Cada chamada de chat mantém seu próprio custo, inclusive as chamadas do grafo.
_REQUEST_COST_USD: ContextVar[float] = ContextVar("fixa_request_cost_usd", default=0.0)
_REQUEST_FAILED: ContextVar[bool] = ContextVar("fixa_request_failed", default=False)
_PENDING_RESOLUTIONS: ContextVar[int] = ContextVar("fixa_pending_resolutions", default=0)


def reset_request_cost() -> object:
    return _REQUEST_COST_USD.set(0.0)


def restore_request_cost(token: object) -> None:
    _REQUEST_COST_USD.reset(token)  # type: ignore[arg-type]


def current_request_cost_usd() -> float:
    return _REQUEST_COST_USD.get()


def reset_request_outcome() -> object:
    return _REQUEST_FAILED.set(False)


def mark_request_failed() -> None:
    _REQUEST_FAILED.set(True)


def request_failed() -> bool:
    return _REQUEST_FAILED.get()


def restore_request_outcome(token: object) -> None:
    _REQUEST_FAILED.reset(token)  # type: ignore[arg-type]


def _model_price(provider: str, model: str) -> tuple[float, float]:
    if provider == "openai" and model.startswith("gpt-6-luna"):
        return (
            config.OBSERVABILITY_OPENAI_INPUT_USD_PER_MILLION,
            config.OBSERVABILITY_OPENAI_OUTPUT_USD_PER_MILLION,
        )
    if provider == "groq":
        return (
            config.OBSERVABILITY_GROQ_INPUT_USD_PER_MILLION,
            config.OBSERVABILITY_GROQ_OUTPUT_USD_PER_MILLION,
        )
    # Provedores/modelos sem tarifa configurada continuam com tokens medidos;
    # custo zero aqui significa "não precificado", não uso gratuito.
    return 0.0, 0.0


def record_llm_usage(provider: str, model: str, input_tokens: int, output_tokens: int) -> None:
    provider = (provider or "unknown").lower()
    model = model or "unknown"
    input_tokens = max(0, int(input_tokens or 0))
    output_tokens = max(0, int(output_tokens or 0))
    if input_tokens:
        LLM_TOKENS.labels(provider, model, "input").inc(input_tokens)
    if output_tokens:
        LLM_TOKENS.labels(provider, model, "output").inc(output_tokens)
    input_rate, output_rate = _model_price(provider, model)
    cost = (
        input_tokens * input_rate + output_tokens * output_rate
    ) / 1_000_000
    if cost:
        LLM_COST_USD.labels(provider, model).inc(cost)
        _REQUEST_COST_USD.set(_REQUEST_COST_USD.get() + cost)


def record_resolution() -> None:
    RESOLUTIONS.inc()
    RESOLUTION_COST_USD.observe(current_request_cost_usd())


def reset_pending_resolutions() -> object:
    return _PENDING_RESOLUTIONS.set(0)


def restore_pending_resolutions(token: object) -> None:
    _PENDING_RESOLUTIONS.reset(token)  # type: ignore[arg-type]


def stage_resolution() -> None:
    _PENDING_RESOLUTIONS.set(_PENDING_RESOLUTIONS.get() + 1)


def finalize_resolutions() -> None:
    count = _PENDING_RESOLUTIONS.get()
    for _ in range(count):
        record_resolution()
    _PENDING_RESOLUTIONS.set(0)


def record_operation(operation: str, outcome: str) -> None:
    OPERATION_RUNS.labels(operation, outcome).inc()


def configure_scenario_gauges() -> None:
    input_rate, output_rate = _model_price("openai", "gpt-6-luna")
    cost_per_message = (
        config.OBSERVABILITY_ESTIMATED_INPUT_TOKENS_PER_MESSAGE * input_rate
        + config.OBSERVABILITY_ESTIMATED_OUTPUT_TOKENS_PER_MESSAGE * output_rate
    ) / 1_000_000
    for users in (100, 1000):
        WEEKLY_ESTIMATED_COST_USD.labels(str(users)).set(
            users * config.OBSERVABILITY_WEEKLY_MESSAGES_PER_USER * cost_per_message
        )

    try:
        value_brl = float(config.OBSERVABILITY_VALUE_PER_RESOLUTION_BRL)
    except (TypeError, ValueError):
        value_brl = 0.0
    brl_per_usd = config.OBSERVABILITY_BRL_PER_USD
    ROI_CONFIGURED.set(1 if value_brl > 0 and brl_per_usd > 0 else 0)
    ROI_VALUE_BRL.set(value_brl)
    BRL_PER_USD.set(brl_per_usd)


def prometheus_payload() -> bytes:
    return generate_latest()


configure_scenario_gauges()


try:
    from langchain_core.callbacks import BaseCallbackHandler

    class MetricsCallbackHandler(BaseCallbackHandler):
        """Lê tokens devolvidos pelo modelo sem guardar prompts ou respostas."""
        run_inline = True

        def on_llm_end(self, response, **kwargs) -> None:
            usage = {}
            provider = "unknown"
            model = "unknown"
            llm_output = getattr(response, "llm_output", None) or {}
            if isinstance(llm_output, dict):
                usage = llm_output.get("token_usage") or llm_output.get("usage") or {}
                model = llm_output.get("model_name") or model
                provider = llm_output.get("model_provider") or provider

            for generation_list in getattr(response, "generations", []) or []:
                for generation in generation_list:
                    message = getattr(generation, "message", None)
                    metadata = getattr(message, "response_metadata", {}) or {}
                    provider = metadata.get("model_provider") or provider
                    model = metadata.get("model_name") or metadata.get("model") or model
                    usage = (
                        getattr(message, "usage_metadata", None)
                        or metadata.get("token_usage")
                        or metadata.get("usage")
                        or usage
                    )
                    if usage:
                        break
                if usage:
                    break

            if not isinstance(usage, dict):
                return
            input_tokens = usage.get("input_tokens", usage.get("prompt_tokens", 0))
            output_tokens = usage.get("output_tokens", usage.get("completion_tokens", 0))
            if provider == "unknown":
                if model.startswith("gpt-"):
                    provider = "openai"
                elif model.startswith("openai/gpt-oss-"):
                    provider = "groq"
            record_llm_usage(provider, model, input_tokens, output_tokens)

        def on_llm_error(self, error, **kwargs) -> None:
            # A chamada que falhou não tem token/custo reportado pelo provedor.
            return None

except ImportError:  # pragma: no cover - dependências da aplicação incluem LangChain.
    MetricsCallbackHandler = None  # type: ignore[assignment,misc]
