from typing import Annotated, Literal, TypedDict

from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages


class GraphState(TypedDict, total=False):
    messages: Annotated[
        list[BaseMessage],
        add_messages,
    ]

    user_id: str

    perfil: Literal[
        "solicitante",
        "tecnico",
        "gestor",
    ]

    intencao: Literal[
        "faq",
        "solicitacao",
        "analytics",
        "visualizacao",
        "feedback",
        "fora_de_escopo",
    ]

    entrada_valida: bool
    mensagem_anonimizada: str
    mapa_pii: dict[str, str]
    motivo_bloqueio: str | None

    justificativa_roteamento: str

    evidencias: list[str]
    resposta_especialista: str

    veredito: Literal[
        "aprovado",
        "revisar",
        "bloqueado",
    ]

    feedback_juiz: str
    tentativas: int

    resposta_final: str
    erro: str | None