import asyncio
import json
from types import SimpleNamespace
from unittest.mock import AsyncMock

from langchain_core.messages import AIMessage, ToolMessage

from app.graph.evidencias import executar_com_evidencias, extrair_evidencias, ids_chamadas


def chamada(nome, identificador):
    return AIMessage(content="", tool_calls=[{
        "name": nome, "id": identificador, "args": {},
    }])


def retorno(identificador, conteudo, status="success"):
    return ToolMessage(content=conteudo, tool_call_id=identificador, status=status)


def test_multiplas_tools_preservam_resultados_e_excluem_historico_e_formato():
    historico = [chamada("listar_minhas_solicitacoes", "antiga"), retorno("antiga", "antigo")]
    mensagens = [
        *historico,
        chamada("listar_minhas_solicitacoes", "a"),
        retorno("a", '{"status":"SUCESSO","solicitacoes":[{"titulo":"Torneira"}]}'),
        chamada("listar_minhas_solicitacoes", "b"),
        retorno("b", '{"status":"SEM_RESULTADO","solicitacoes":[]}'),
        chamada("Formato", "saida"), retorno("saida", "resposta estruturada"),
    ]
    evidencias = [json.loads(e) for e in extrair_evidencias(mensagens, ids_chamadas(historico), "Formato")]
    assert [e["chamada_id"] for e in evidencias] == ["a", "b"]
    assert evidencias[0]["resultado"]["solicitacoes"] == [{"titulo": "Torneira"}]
    assert evidencias[1]["status_operacao"] == "SEM_RESULTADO"


def test_falhas_e_texto_faq_nao_sao_convertidos_em_sucesso_de_negocio():
    mensagens = [
        chamada("buscar_faq", "faq"), retorno("faq", "Trecho original do FAQ"),
        chamada("consulta", "erro"), retorno("erro", '{"status":"TIMEOUT"}'),
        chamada("consulta", "excecao"), retorno("excecao", "Falha na ferramenta", "error"),
    ]
    faq, falha, excecao = [json.loads(e) for e in extrair_evidencias(mensagens, set(), "Formato")]
    assert faq["resultado"] == "Trecho original do FAQ"
    assert faq["status_operacao"] is None
    assert falha["status_operacao"] == "TIMEOUT"
    assert excecao["status_execucao"] == "error"


def test_coletor_acumula_evidencias_sem_mutar_estado():
    class Formato:
        pass

    agente = SimpleNamespace(ainvoke=AsyncMock(return_value={"messages": [
        chamada("consulta", "nova"), retorno("nova", "resultado"),
    ]}))
    state = {"messages": [], "evidencias": ["evidencia anterior da mesma rodada"]}
    _, evidencias = asyncio.run(executar_com_evidencias(agente, state, {}, Formato))
    assert len(evidencias) == 2
    assert evidencias[0] == state["evidencias"][0]
    assert len(state["evidencias"]) == 1


def test_no_solicitacoes_entrega_multiplas_evidencias_ao_grafo(monkeypatch):
    from app.graph import nodes
    from app.agents.agentsResult import SolicitacaoOcorrenciaResultado

    mensagens = [
        chamada("buscar_opcoes_solicitacao", "busca"), retorno("busca", "local encontrado"),
        chamada("criar_solicitacao", "cadastro"), retorno("cadastro", '{"status":"SUCESSO"}'),
    ]
    agente = SimpleNamespace(ainvoke=AsyncMock(return_value={
        "messages": mensagens,
        "structured_response": SolicitacaoOcorrenciaResultado(
            agente="solicitacao", resposta="Cadastro realizado", status="SUCESSO",
        ),
    }))
    monkeypatch.setattr(nodes, "solicitacoes_solicitante", agente)
    resultado = asyncio.run(nodes.executar_solicitacao(
        {"perfil": "solicitante", "messages": [], "evidencias": []},
        SimpleNamespace(context={}),
    ))
    assert len(resultado["evidencias"]) == 2
    assert resultado["resposta_especialista"] == "Cadastro realizado"
    assert resultado["erro"] is None


def test_nova_mensagem_limpa_evidencias_do_checkpoint():
    from langchain_core.messages import HumanMessage
    from app.graph.runner import criar_estado_inicial

    usuario = SimpleNamespace(tipo_acesso="solicitante", usuario_id=1)
    estado_anterior = {"evidencias": ["consulta de outra rodada"]}
    estado_anterior.update(criar_estado_inicial([HumanMessage(content="Nova consulta")], usuario))
    assert estado_anterior["evidencias"] == []
