from typing import Annotated, Literal, TypedDict
from langgraph.graph.message import add_messages
from langchain_core.messages import BaseMessage

# TypedDict para o estado do grafo, que define a estrutura de dados que será usada para armazenar o estado do grafo durante a execução do fluxo de trabalho.
# O total=False indica que todas as chaves são opcionais, permitindo que o estado seja construído gradualmente à medida que o fluxo de trabalho avança.
# O messages é uma lista de mensagens que serão processadas pelo grafo, e o add_messages é um validador que garante que as mensagens sejam do tipo BaseMessage. O annotated é usado para adicionar metadados ao campo messages, permitindo que o validador add_messages seja aplicado a ele.
class GraphState(TypedDict, total=False):
    messages: Annotated[list[BaseMessage], add_messages]

    user_id: int
    perfil: Literal[
        "solicitante",
        "tecnico",
        "gestor"
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
