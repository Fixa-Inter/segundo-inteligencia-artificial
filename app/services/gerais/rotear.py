"""Decisão de intenção do chat pelo JEV."""

import json

from app.graph.continuacoes import propostas_pendentes
from app.services.gerais.jev import DecisaoIncertaJEV, consultar_jev, ler_choice, ler_noul


CRITERIOS_INTENCAO = {
    "faq": "Dúvida sobre o aplicativo ou políticas de uso.",
    "ajuda_geral": (
        "Consulta sobre registros, descrições, equipamentos, locais, problemas, "
        "ocorrências, ordens, tarefas ou eventos existentes; alteração de solicitação "
        "existente ou anexo em registro existente."
    ),
    "solicitacao": "Pede reparo ainda necessário ou consulta solicitações de manutenção.",
    "ocorrencia": "Registra manutenção ou reparo que já foi realizado.",
    "analytics": "Pede métricas, indicadores ou análises.",
    "visualizacao": "Pede gráficos ou visualizações.",
    "feedback": "Envia crítica, elogio ou sugestão.",
    "fora_de_escopo": "Assunto sem relação com a plataforma ou manutenção.",
}

INSTRUCAO_INTENCAO = (
    "Qual é a intenção da mensagem atual? Use o histórico apenas para resolver "
    "referências e respostas curtas. Uma proposta pendente não obriga o usuário a "
    "continuar: se mudou de assunto, classifique o novo pedido. Um defeito que "
    "ainda requer reparo é solicitação; manutenção já executada é ocorrência, "
    "mesmo que o relato mencione um defeito passado. Se não estiver claro se o "
    "serviço foi realizado, escolha solicitação apenas quando houver pedido de "
    "reparo; nos demais casos o especialista deve esclarecer antes de registrar."
)


def _resumir_propostas(estado: dict, *, pausadas: bool = False) -> dict:
    return {
        tipo: {
            "status": proposta.get("status" if tipo == "ajuda_geral" else "status_fluxo"),
            "pausado": bool(proposta.get("pausado")),
            "dados": json.loads(json.dumps(proposta.get("dados", {}), default=str)),
        }
        for tipo, proposta in propostas_pendentes(estado, pausadas=pausadas).items()
    }


async def rotear_jev(estado: dict, pergunta: str) -> dict:
    historico = [
        {"papel": mensagem.type, "conteudo": str(mensagem.content)}
        for mensagem in estado.get("messages", [])[-8:]
        if mensagem.type in {"human", "ai"}
    ]
    ativo = _resumir_propostas(estado)
    dados = await consultar_jev(
        {
            "mensagem_atual": pergunta,
            "historico": historico,
            "propostas_ativas": ativo,
            "propostas_pausadas": _resumir_propostas(estado, pausadas=True),
            "imagens_recebidas": bool(estado.get("imagens_recebidas")),
            "contexto_temporal": estado.get("contexto_temporal", ""),
        },
        {
            "intencao": {
                "type": "choice", "instructions": INSTRUCAO_INTENCAO,
                "criteria": CRITERIOS_INTENCAO,
            },
            "continua_pendente": {
                "type": "noul",
                "instructions": (
                    "A mensagem atual fornece detalhe, correção, pergunta ou imagem "
                    "referente a uma proposta ativa, sem iniciar outro assunto? "
                    "Uma proposta pausada só pode ser retomada por pedido explícito."
                ),
            },
        },
        operacao="roteador",
    )
    respostas = dados["answers"]
    intencao, confianca = ler_choice(respostas, "intencao", set(CRITERIOS_INTENCAO))
    continuacao = ler_noul(respostas, "continua_pendente")
    if confianca < 0.35 or ativo and 0.35 < continuacao < 0.65:
        raise DecisaoIncertaJEV("Roteamento incerto.")
    return {
        "intencao": intencao,
        "continua_pendente": bool(ativo) and continuacao >= 0.65,
        "justificativa": f"JEV: {intencao} (confiança {confianca:.2f}).",
    }
