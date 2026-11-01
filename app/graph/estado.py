from typing import Annotated, Literal, TypedDict

from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages
from app.core import Emocao


class EstadoGrafo(TypedDict, total=False):
    messages: Annotated[
        list[BaseMessage],
        add_messages,
    ]

    user_id: int

    perfil: Literal[
        "solicitante",
        "tecnico",
        "gestor",
        "administrador"
    ]

    intencao: Literal[
        "ajuda_geral",
        "faq",
        "solicitacao",
        "ocorrencia",
        "analytics",
        "visualizacao",
        "feedback",
        "analista_compras",
        "fora_de_escopo",
    ] | None

    entrada_valida: bool
    mensagem_anonimizada: str
    mapa_pii: dict[str, str]
    motivo_bloqueio: str | None

    justificativa_roteamento: str

    evidencias: list[str]
    operacoes_pendentes: list[dict]
    aprovacao_operacoes: dict | None
    resultados_operacoes: list[dict]
    consultas_visualizacao: list[dict]
    visualizacao_candidata: dict | None
    visualizacao_status: str | None
    visualizacao_execucao_id: str | None
    visualizacao_aprovacao: dict | None
    visualizacao_aprovada: dict | None
    visualizacao_publica: dict | None
    resposta_especialista: str
    resposta_candidata: str

    veredito: Literal[
        "aprovado",
        "revisar",
        "bloqueado",
    ] | None

    feedback_juiz: str
    tentativas: int

    resposta_final: str
    emocao: Emocao | str
    saida_bloqueada: bool
    erro: str | None 
    solicitacao_pendente: dict | None

    ocorrencia_pendente: dict | None
    ajuda_geral_pendente: dict | None
    analise_compra_pendente: dict | None
    imagens_recebidas: bool
    anexos_pendentes: int
    cadastro_em_andamento: bool
    continua_pendente: bool
    esclarecimento_roteamento: bool
    propostas_apresentadas: list[dict]
    contexto_temporal: str


def limpar_visualizacao() -> dict:
    """Descarta a seleção e os registros internos de uma execução anterior."""
    return {
        "consultas_visualizacao": [],
        "visualizacao_candidata": None,
        "visualizacao_status": None,
        "visualizacao_execucao_id": None,
        "visualizacao_aprovacao": None,
        "visualizacao_aprovada": None,
        "visualizacao_publica": None,
    }
