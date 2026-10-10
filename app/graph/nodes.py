import logging

from typing import Literal

from langchain_core.messages import (
    AIMessage,
    HumanMessage,
    SystemMessage,
)
from langgraph.runtime import Runtime
from pydantic import BaseModel, Field

from app.agents.agents import (
    selecionar_agente,
    analytics_gestor,
    faq_gestor,
    faq_solicitante,
    faq_tecnico,
    feedback,
    solicitacoes_gestor,
    solicitacoes_solicitante,
    solicitacoes_tecnico,
    visualizacoes_gestor,
)
from app.agents.juiz import julgar_resposta
from app.agents.agentsResult import (
    AnalyticsResultado,
    FAQResultado,
    FeedbackResultado,
    SolicitacaoOcorrenciaResultado,
    VisualizacaoResultado,
)
from app.agents.llms import (
    llm_rapido,
)
from app.graph.context import GraphContext
from app.graph.evidencias import executar_com_evidencias
from app.graph.state import GraphState
from app.guardrails import (
    guardrail_entrada,
    guardrail_saida,
)


logger = logging.getLogger(__name__)


class DecisaoRoteamento(BaseModel):
    intencao: Literal[
        "faq",
        "solicitacao",
        "analytics",
        "visualizacao",
        "feedback",
        "fora_de_escopo",
    ] = Field(
        description=(
            "Intenção identificada na mensagem do usuário."
        )
    )

    justificativa: str = Field(
        description=(
            "Justificativa curta para a intenção selecionada."
        )
    )


roteador_estruturado = (
    llm_rapido.with_structured_output(
        DecisaoRoteamento
    )
)


def obter_pergunta(
    state: GraphState,
) -> str:
    messages = state.get(
        "messages",
        [],
    )

    if not messages:
        return ""

    return str(
        messages[-1].content
    ).strip()


def validar_entrada(
    state: GraphState,
) -> dict:
    pergunta = (
        state.get("mensagem_anonimizada")
        or obter_pergunta(state)
    )

    perfil = state.get("perfil")

    if not pergunta:
        return {
            "entrada_valida": False,
            "motivo_bloqueio": "mensagem_vazia",
            "resposta_final": (
                "A mensagem não pode estar vazia."
            ),
            "erro": None,
        }

    if perfil not in {
        "solicitante",
        "tecnico",
        "gestor",
    }:
        return {
            "entrada_valida": False,
            "motivo_bloqueio": "perfil_invalido",
            "resposta_final": (
                "O usuário não possui um perfil válido."
            ),
            "erro": None,
        }

    try:
        resultado = guardrail_entrada(
            pergunta
        )

    except Exception:
        logger.exception("Falha no guardrail de entrada")
        return {
            "entrada_valida": False,
            "motivo_bloqueio": (
                "erro_guardrail_entrada"
            ),
            "resposta_final": (
                "Não foi possível validar a solicitação."
            ),
            "erro": (
                "Falha inesperada no guardrail de entrada."
            ),
        }

    if resultado["bloqueado"]:
        return {
            "entrada_valida": False,
            "motivo_bloqueio": resultado["motivo"],
            "resposta_final": resultado["mensagem"],
            "erro": None,
        }

    return {
        "entrada_valida": True,
        "motivo_bloqueio": None,
        "erro": None,
    }


def supervisionar(
    state: GraphState,
) -> dict:
    pergunta = obter_pergunta(state)

    instrucao = """
Classifique a solicitação em uma destas intenções:

- faq: dúvida sobre o aplicativo ou políticas;
- solicitacao: criar, consultar ou alterar um chamado;
- analytics: métricas, indicadores ou análises;
- visualizacao: gráficos ou visualizações;
- feedback: crítica, elogio ou sugestão;
- fora_de_escopo: assunto não relacionado à plataforma.

Não responda à solicitação. Apenas classifique.
"""

    try:
        decisao = roteador_estruturado.invoke(
            [
                SystemMessage(
                    content=instrucao,
                ),
                HumanMessage(
                    content=pergunta,
                ),
            ]
        )

        return {
            "intencao": decisao.intencao,
            "justificativa_roteamento": (
                decisao.justificativa
            ),
            "erro": None,
        }

    except Exception as erro:
        logger.exception("Falha no supervisor")
        return {
            "intencao": "fora_de_escopo",
            "justificativa_roteamento": (
                "Falha no roteamento."
            ),
            "erro": (
                f"Erro no supervisor: {erro}"
            ),
        }


async def executar_faq(
    state: GraphState,
    runtime: Runtime[GraphContext],
) -> dict:
    perfil = state.get("perfil")
    agente = selecionar_agente("faq", perfil, {
        "solicitante": faq_solicitante,
        "tecnico": faq_tecnico,
        "gestor": faq_gestor,
    })

    if agente is None:
        return {
            "resposta_especialista": "",
            "erro": (
                "Não existe agente FAQ "
                f"para o perfil: {perfil}"
            ),
        }

    evidencias = list(state.get("evidencias", []))
    try:
        resultado, evidencias = await executar_com_evidencias(
            agente, state, runtime.context, FAQResultado,
        )

        resposta_estruturada = resultado.get(
            "structured_response"
        )

        if not isinstance(
            resposta_estruturada,
            FAQResultado,
        ):
            raise ValueError(
                "O agente FAQ retornou uma "
                "resposta incompatível."
            )

        return {
            "evidencias": evidencias,
            "resposta_especialista": (
                resposta_estruturada.resposta
            ),
            "erro": None,
        }

    except Exception as erro:
        logger.exception("Falha no agente FAQ")
        return {
            "evidencias": evidencias,
            "resposta_especialista": "",
            "erro": (
                "Erro durante a execução do FAQ: "
                f"{erro}"
            ),
        }


async def executar_solicitacao(
    state: GraphState,
    runtime: Runtime[GraphContext],
) -> dict:
    perfil = state.get("perfil")
    agente = selecionar_agente("solicitacao", perfil, {
        "solicitante": solicitacoes_solicitante,
        "tecnico": solicitacoes_tecnico,
        "gestor": solicitacoes_gestor,
    })

    if agente is None:
        return {
            "resposta_especialista": "",
            "erro": (
                "Não existe agente de solicitações "
                f"para o perfil: {perfil}"
            ),
        }

    evidencias = list(state.get("evidencias", []))
    try:
        resultado, evidencias = await executar_com_evidencias(
            agente, state, runtime.context, SolicitacaoOcorrenciaResultado,
        )

        resposta_estruturada = resultado.get(
            "structured_response"
        )

        if not isinstance(
            resposta_estruturada,
            SolicitacaoOcorrenciaResultado,
        ):
            raise ValueError(
                "O agente retornou uma "
                "resposta incompatível."
            )

        return {
            "evidencias": evidencias,
            "resposta_especialista": (
                resposta_estruturada.resposta
            ),
            "erro": None,
        }

    except Exception as erro:
        logger.exception("Falha no agente de solicitações")
        return {
            "evidencias": evidencias,
            "resposta_especialista": "",
            "erro": (
                "Erro durante a execução do agente "
                f"de solicitações: {erro}"
            ),
        }


async def executar_analytics(
    state: GraphState,
    runtime: Runtime[GraphContext],
) -> dict:
    if state.get("perfil") != "gestor":
        return {
            "resposta_especialista": (
                "Seu perfil nao possui permissao para "
                "consultar indicadores gerenciais."
            ),
            "erro": None,
        }

    evidencias = list(state.get("evidencias", []))
    try:
        resultado, evidencias = await executar_com_evidencias(
            analytics_gestor, state, runtime.context, AnalyticsResultado,
        )

        resposta_estruturada = resultado.get(
            "structured_response"
        )

        if not isinstance(
            resposta_estruturada,
            AnalyticsResultado,
        ):
            raise ValueError(
                "O agente de analytics retornou uma "
                "resposta incompativel."
            )

        return {
            "evidencias": evidencias,
            "resposta_especialista": (
                resposta_estruturada.resposta
            ),
            "erro": None,
        }

    except Exception as erro:
        logger.exception("Falha no agente de analytics")
        return {
            "evidencias": evidencias,
            "resposta_especialista": "",
            "erro": (
                "Erro durante a execucao do agente "
                f"de analytics: {erro}"
            ),
        }


async def executar_visualizacao(
    state: GraphState,
    runtime: Runtime[GraphContext],
) -> dict:
    if state.get("perfil") != "gestor":
        return {
            "resposta_especialista": (
                "Seu perfil nao possui permissao para "
                "gerar visualizacoes gerenciais."
            ),
            "erro": None,
        }

    evidencias = list(state.get("evidencias", []))
    try:
        resultado, evidencias = await executar_com_evidencias(
            visualizacoes_gestor, state, runtime.context, VisualizacaoResultado,
        )

        resposta_estruturada = resultado.get(
            "structured_response"
        )

        if not isinstance(
            resposta_estruturada,
            VisualizacaoResultado,
        ):
            raise ValueError(
                "O agente de visualizacoes retornou uma "
                "resposta incompativel."
            )

        return {
            "evidencias": evidencias,
            "resposta_especialista": (
                resposta_estruturada.resposta
            ),
            "erro": None,
        }

    except Exception as erro:
        logger.exception("Falha no agente de visualizações")
        return {
            "evidencias": evidencias,
            "resposta_especialista": "",
            "erro": (
                "Erro durante a execucao do agente "
                f"de visualizacoes: {erro}"
            ),
        }


async def executar_feedback(
    state: GraphState,
    runtime: Runtime[GraphContext],
) -> dict:
    evidencias = list(state.get("evidencias", []))
    try:
        resultado, evidencias = await executar_com_evidencias(
            feedback, state, runtime.context, FeedbackResultado,
        )

        resposta_estruturada = resultado.get(
            "structured_response"
        )

        if not isinstance(
            resposta_estruturada,
            FeedbackResultado,
        ):
            raise ValueError(
                "O agente de feedback retornou uma "
                "resposta incompativel."
            )

        return {
            "evidencias": evidencias,
            "resposta_especialista": (
                resposta_estruturada.resposta
            ),
            "erro": None,
        }

    except Exception as erro:
        logger.exception("Falha no agente de feedback")
        return {
            "evidencias": evidencias,
            "resposta_especialista": "",
            "erro": (
                "Erro durante a execucao do agente "
                f"de feedback: {erro}"
            ),
        }


def validar_saida(
    state: GraphState,
) -> dict:
    resposta = state.get(
        "resposta_especialista",
        "",
    ).strip()

    if state.get("veredito") != "aprovado":
        resposta_final = (
            "A resposta não foi aprovada para envio."
        )

        return {
            "resposta_final": resposta_final,
            "messages": [
                AIMessage(
                    content=resposta_final,
                ),
            ],
            "erro": state.get("erro"),
        }

    if not resposta:
        resposta_final = (
            "Não foi possível produzir uma "
            "resposta válida."
        )

        return {
            "resposta_final": resposta_final,
            "messages": [
                AIMessage(
                    content=resposta_final,
                ),
            ],
            "erro": "Resposta final vazia.",
        }

    try:
        resultado = guardrail_saida(
            resposta=resposta,
            mapa_pii=state.get(
                "mapa_pii",
                {},
            ),
            restaurar_pii=False,
        )

        resposta_final = resultado[
            "conteudo"
        ]

    except Exception:
        logger.exception("Falha no guardrail de saída")
        resposta_final = (
            "Não foi possível revisar a resposta."
        )

        return {
            "resposta_final": resposta_final,
            "messages": [
                AIMessage(
                    content=resposta_final,
                ),
            ],
            "erro": (
                "Falha inesperada no "
                "guardrail de saída."
            ),
        }

    return {
        "resposta_final": resposta_final,
        "messages": [
            AIMessage(
                content=resposta_final,
            ),
        ],
        "erro": None,
    }


def tratar_erro(
    state: GraphState,
) -> dict:
    resposta_existente = state.get(
        "resposta_final"
    )

    if resposta_existente:
        resposta = resposta_existente

    elif state.get("erro"):
        resposta = (
            "Não foi possível processar sua "
            "solicitação neste momento. "
            "Tente novamente mais tarde."
        )

    elif (
        state.get("intencao")
        == "fora_de_escopo"
    ):
        resposta = (
            "Posso ajudar com dúvidas sobre o "
            "aplicativo, chamados de manutenção, "
            "indicadores, visualizações e feedback."
        )

    else:
        resposta = (
            "Essa funcionalidade ainda não "
            "está disponível."
        )

    return {
        "resposta_final": resposta,
        "messages": [
            AIMessage(
                content=resposta,
            ),
        ],
    }
