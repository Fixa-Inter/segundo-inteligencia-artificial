from typing import Literal

from langchain_core.messages import HumanMessage, SystemMessage
from pydantic import BaseModel, Field
from langgraph.runtime import Runtime


from app.agents.agents import (
    faq_gestor,
    faq_solicitante,
    faq_tecnico,
    solicitacoes_gestor,
    solicitacoes_solicitante,
    solicitacoes_tecnico,
    FAQResultado,
)

from app.agents.agentsResult import (
    SolicitacaoOcorrenciaResultado,
)
from app.graph.context import GraphContext

from app.agents.llms import (
    llm_gemini,
    llm_groq,
    llm_rapido,
)
from app.agents.prompts import construtor
from app.graph.state import GraphState

# BaseModel para saída estruturada do roteador, que vem do Pydantic e vê se os dados recebidos tem o formato esperado
class DecisaoRoteamento(BaseModel):
    intencao: Literal[
        "faq",
        "solicitacao",
        "analytics",
        "visualizacao",
        "feedback",
        "fora_de_escopo",
    ] = Field(
        description="Intenção identificada na mensagem do usuário."
    )

    justificativa: str = Field(
        description="Justificativa curta para a intenção selecionada."
    )


class AvaliacaoJuiz(BaseModel):
    veredito: Literal["aprovado", "revisar", "bloqueado"]
    feedback: str

# Utiliza a saida da decisaoroteamento para não acabar saindo qualquer coisa
roteador_estruturado = llm_rapido.with_structured_output(
    DecisaoRoteamento
)

# Aplica a saída estruturada antes de configurar o fallback.
juiz_estruturado = (
    llm_gemini
    .with_structured_output(AvaliacaoJuiz)
    .with_fallbacks([
        llm_groq.with_structured_output(AvaliacaoJuiz)
    ])
)


def obter_pergunta(state: GraphState) -> str:
    messages = state.get("messages", [])

    if not messages:
        return ""

    return str(messages[-1].content).strip()


def validar_entrada(state: GraphState) -> dict:
    pergunta = obter_pergunta(state)
    perfil = state.get("perfil")

    if not pergunta:
        return {
            "entrada_valida": False,
            "erro": "A mensagem está vazia.",
        }

    if perfil not in {"solicitante", "tecnico", "gestor"}:
        return {
            "entrada_valida": False,
            "erro": "Perfil inválido ou não autenticado.",
        }

    return {
        "entrada_valida": True,
        "erro": None,
    }


def supervisionar(state: GraphState) -> dict:
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
                SystemMessage(content=instrucao),
                HumanMessage(content=pergunta),
            ]
        )

        return {
            "intencao": decisao.intencao,
            "justificativa_roteamento": decisao.justificativa,
            "erro": None,
        }

    except Exception as erro:
        return {
            "intencao": "fora_de_escopo",
            "justificativa_roteamento": "Falha no roteamento.",
            "erro": f"Erro no supervisor: {erro}",
        }

async def executar_faq(
    state: GraphState,
    runtime: Runtime[GraphContext],
) -> dict:
    agentes_por_perfil = {
        "solicitante": faq_solicitante,
        "tecnico": faq_tecnico,
        "gestor": faq_gestor,
    }

    perfil = state.get("perfil")
    agente = agentes_por_perfil.get(perfil)

    if agente is None:
        return {
            "resposta_especialista": "",
            "erro": (
                "Não existe agente FAQ "
                f"para o perfil: {perfil}"
            ),
        }

    try:
        resultado = await agente.ainvoke(
            {
                "messages": state.get("messages", []),
            },
            context=runtime.context,
        )

        resposta_estruturada = resultado.get(
            "structured_response"
        )

        if not isinstance(
            resposta_estruturada,
            FAQResultado,
        ):
            raise ValueError(
                "O agente FAQ retornou uma resposta incompatível."
            )

        return {
            "resposta_especialista": (
                resposta_estruturada.resposta
            ),
            "erro": None,
        }

    except Exception as erro:
        return {
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
    agentes_por_perfil = {
        "solicitante": solicitacoes_solicitante,
        "tecnico": solicitacoes_tecnico,
        "gestor": solicitacoes_gestor,
    }

    perfil = state.get("perfil")
    agente = agentes_por_perfil.get(perfil)

    if agente is None:
        return {
            "resposta_especialista": "",
            "erro": (
                "Não existe agente de solicitações "
                f"para o perfil: {perfil}"
            ),
        }

    try:
        resultado = await agente.ainvoke(
            {
                "messages": state.get("messages", []),
            },
            context=runtime.context,
        )

        resposta_estruturada = resultado.get(
            "structured_response"
        )

        if not isinstance(
            resposta_estruturada,
            SolicitacaoOcorrenciaResultado,
        ):
            raise ValueError(
                "O agente retornou uma resposta incompatível."
            )

        return {
            "resposta_especialista": (
                resposta_estruturada.resposta
            ),
            "erro": None,
        }

    except Exception as erro:
        return {
            "resposta_especialista": "",
            "erro": (
                "Erro durante a execução do agente "
                f"de solicitações: {erro}"
            ),
        }
    
def obter_prompt_juiz(perfil: str) -> str:
    construtores_por_perfil = {
        "solicitante": construtor.construir_juiz_solicitante,
        "tecnico": construtor.construir_juiz_tecnico,
        "gestor": construtor.construir_juiz_gestor,
    }

    funcao_construtora = construtores_por_perfil.get(perfil)

    if funcao_construtora is None:
        raise ValueError(
            f"Não existe prompt de juiz para o perfil: {perfil}"
        )

    return funcao_construtora()


def julgar_resposta(state: GraphState) -> dict:
    if state.get("erro"):
        return {
            "veredito": "bloqueado",
            "feedback_juiz": "A execução do especialista apresentou erro.",
            "tentativas": state.get("tentativas", 0),
        }

    pergunta = obter_pergunta(state)
    perfil = state.get("perfil")
    resposta = state.get("resposta_especialista", "")
    evidencias = state.get("evidencias", [])

    if not perfil:
        return {
            "veredito": "bloqueado",
            "feedback_juiz": "O perfil do usuário não foi informado.",
            "tentativas": state.get("tentativas", 0),
            "erro": "Perfil ausente durante o julgamento.",
        }

    if not resposta:
        return {
            "veredito": "bloqueado",
            "feedback_juiz": "O agente especialista não produziu resposta.",
            "tentativas": state.get("tentativas", 0),
            "erro": "Resposta especialista vazia.",
        }

    evidencias_formatadas = (
        "\n".join(evidencias)
        if evidencias
        else "Nenhuma evidência foi fornecida."
    )

    entrada_juiz = f"""
Perfil autenticado:
{perfil}

Solicitação do usuário:
{pergunta}

Evidências disponíveis:
{evidencias_formatadas}

Resposta candidata:
{resposta}

Avalie a resposta candidata e produza o veredito estruturado.
"""

    try:
        avaliacao = juiz_estruturado.invoke(
            [
                SystemMessage(
                    content=obter_prompt_juiz(perfil)
                ),
                HumanMessage(content=entrada_juiz),
            ]
        )

        tentativas = state.get("tentativas", 0)

        if avaliacao.veredito == "revisar":
            tentativas += 1

        return {
            "veredito": avaliacao.veredito,
            "feedback_juiz": avaliacao.feedback,
            "tentativas": tentativas,
            "erro": None,
        }

    except Exception as erro:
        return {
            "veredito": "bloqueado",
            "feedback_juiz": "Não foi possível avaliar a resposta.",
            "tentativas": state.get("tentativas", 0),
            "erro": f"Erro durante o julgamento: {erro}",
        }


def validar_saida(state: GraphState) -> dict:
    resposta = state.get("resposta_especialista", "").strip()

    if state.get("veredito") != "aprovado":
        return {
            "resposta_final": (
                "A resposta não foi aprovada para envio."
            ),
            "erro": state.get("erro"),
        }

    if not resposta:
        return {
            "resposta_final": (
                "Não foi possível produzir uma resposta válida."
            ),
            "erro": "Resposta final vazia.",
        }

    return {
        "resposta_final": resposta,
        "erro": None,
    }


def tratar_erro(state: GraphState) -> dict:
    if state.get("erro"):
        return {
            "resposta_final": (
                "Não foi possível processar sua solicitação neste momento. "
                "Tente novamente mais tarde."
            )
        }

    if state.get("intencao") == "fora_de_escopo":
        return {
            "resposta_final": (
                "Posso ajudar com dúvidas sobre o aplicativo, chamados "
                "de manutenção, indicadores, visualizações e feedback."
            )
        }

    return {
        "resposta_final": (
            "Essa funcionalidade ainda não está disponível."
        )
    }