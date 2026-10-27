import asyncio
import json

import pytest

from app.agents.analista_compras import DadosCompra, _campos_prioritarios_ausentes, _contexto_mcp
from app.agents import analista_compras
from app.agents import juiz_compras
from app.agents.orquestrador import pedido_compra_explicito, rotear_orquestrador
from app.graph.fluxo import grafo
from app.graph.nos import validar_saida
from app.graph.transicoes import selecionar_especialista
from app.mcp import buscazap


def test_explicit_purchase_routes_to_specialist_without_llm():
    assert pedido_compra_explicito("Onde posso comprar uma furadeira 220 V?")
    assert pedido_compra_explicito("Quais lojas o BuscaZap cobre?")
    decision = asyncio.run(rotear_orquestrador({}, "Onde posso comprar uma furadeira 220 V?"))
    assert decision.intencao == "analista_compras"
    assert selecionar_especialista({"intencao": decision.intencao}) == "analista_compras"
    assert "analista_compras" in grafo.nodes
    edges = {(edge.source, edge.target) for edge in grafo.get_graph().edges}
    assert ("supervisor", "analista_compras") in edges
    assert ("analista_compras", "juiz") in edges


def test_priority_fields_are_required_but_optional_fields_are_not():
    assert _campos_prioritarios_ausentes(DadosCompra(item="broca", requisitos_obrigatorios=[], quantidade="2")) == []
    assert len(_campos_prioritarios_ausentes(DadosCompra(item="broca"))) == 2


def test_mcp_context_contains_only_declared_purchase_data():
    data = DadosCompra(item="broca", requisitos_obrigatorios=["8 mm"], quantidade="2")
    context = _contexto_mcp(data)
    assert "broca" in context and "8 mm" in context and "Quantidade: 2" in context
    assert "Orçamento" not in context and "Aplicação" not in context


def test_mcp_quota_error_is_not_mistaken_for_empty_results(monkeypatch):
    calls = []

    async def fake_rpc(method, params=None):
        calls.append(method)
        if method == "tools/list":
            return {"tools": [{"name": "buscar_produtos_por_contexto"}]}
        return {"isError": True, "error": "quota_exceeded"}

    monkeypatch.setattr(buscazap, "_rpc", fake_rpc)
    with pytest.raises(buscazap.ErroBuscaZap) as error:
        asyncio.run(buscazap.buscar_produtos("Item: broca. Quantidade: 2."))
    assert error.value.codigo == "quota_exceeded"
    assert calls == ["tools/list", "tools/call"]


def test_mcp_empty_product_list_is_success(monkeypatch):
    async def fake_rpc(method, params=None):
        if method == "tools/list":
            return {"tools": [{"name": "buscar_produtos_por_contexto"}]}
        return {"isError": False, "structuredContent": {"products": []}}

    monkeypatch.setattr(buscazap, "_rpc", fake_rpc)
    assert asyncio.run(buscazap.buscar_produtos("Item: broca."))["products"] == []


def test_store_coverage_parses_documented_content(monkeypatch):
    async def fake_rpc(method, params=None):
        if method == "tools/list":
            return {"tools": [{"name": "listar_lojas"}]}
        return {"isError": False, "content": [{"type": "text", "text": (
            "Lojas cobertas (destaques):\n\n"
            '{"total_claim":"+180 lojas","categorias":[{"categoria":"Ferramentas","lojas":["Loja A"]}]}'
        )}]}

    monkeypatch.setattr(buscazap, "_rpc", fake_rpc)
    result = asyncio.run(buscazap.listar_lojas())
    assert result["categorias"][0]["lojas"] == ["Loja A"]


def test_product_link_survives_output_redaction():
    url = "https://loja.example.com/produto/12345678901"
    evidence = json.dumps({"ferramenta": "buscar_produtos_por_contexto",
                           "resultado": {"ofertas": [{"url": url}]}})
    result = validar_saida({"veredito": "aprovado", "intencao": "analista_compras",
                           "resposta_candidata": f"Oferta: {url}", "mapa_pii": {},
                           "evidencias": [evidence]})
    assert url in result["resposta_final"]


def test_purchase_judge_receives_compact_evidence(monkeypatch):
    offers = [{"loja": "Loja A", "descricao": "Furadeira de impacto com mandril 13 mm",
               "preco": 249.9, "url": f"https://loja.example.com/produto/{i}" + "x" * 70,
               "confirmados": ["mandril 13 mm"], "ausentes": ["220 V"],
               "motivo": "Oferta encontrada para comparação; confirme os requisitos ausentes."}
              for i in range(3)]
    answer = analista_compras._resposta_ofertas(offers, "")
    evidence = [
        json.dumps({"ferramenta": "estado_analise_compra_persistida",
                    "status_operacao": "pronto_para_busca", "resultado": {
                        "dados": {"item": "furadeira", "requisitos_obrigatorios": ["220 V", "mandril 13 mm"],
                                  "quantidade": "1"}}}),
        json.dumps({"ferramenta": "buscar_produtos_por_contexto", "status_operacao": "sucesso",
                    "resultado": {"produtos_recebidos": 3, "ofertas": offers}}),
    ]

    async def fake_jev(state, questions, *, operacao):
        assert len(json.dumps({"state": state, "questions": questions}, ensure_ascii=False)) <= 4000
        return {"answers": {"veredito": {"type": "choice", "choice": "aprovado", "confidence": 0.9},
                            "motivo": {"type": "choice", "choice": "nenhum", "confidence": 0.9}}}

    monkeypatch.setattr(juiz_compras, "consultar_jev", fake_jev)
    result = asyncio.run(juiz_compras.julgar_compra({"perfil": "tecnico",
        "resposta_especialista": answer, "evidencias": evidence, "tentativas": 0}))
    assert result["veredito"] == "aprovado"


def test_purchase_draft_survives_optional_question_before_search(monkeypatch):
    saved = {}
    calls = []

    async def get_draft(*args):
        return saved.get("draft")

    async def extract(message, previous, question):
        return DadosCompra(item="broca", requisitos_obrigatorios=["8 mm"], quantidade="2",
                           recusou_opcionais=message == "não")

    async def save(*args, **kwargs):
        draft = {"id": "d1", "versao": 1, "status_fluxo": kwargs["status_fluxo"],
                 "dados": kwargs["dados"], "opcionais_oferecidos": kwargs["opcionais_oferecidos"],
                 "pergunta_pendente": kwargs["pergunta_pendente"]}
        saved["draft"] = draft
        return draft

    async def update(*args, **kwargs):
        saved["draft"] = {**saved["draft"], **kwargs["campos"]}
        return saved["draft"]

    async def search(context, *, limite):
        calls.append((context, limite))
        return {"products": [], "recomendacao": None}

    monkeypatch.setattr(analista_compras, "obter_analise_compra", get_draft)
    monkeypatch.setattr(analista_compras, "_extrair", extract)
    monkeypatch.setattr(analista_compras, "salvar_analise_compra", save)
    monkeypatch.setattr(analista_compras, "atualizar_analise_compra", update)
    monkeypatch.setattr(analista_compras, "buscar_produtos", search)

    user = type("User", (), {"tipo_acesso": "tecnico", "usuario_id": 7})()
    context = {"usuario": user, "session_id": "s1", "turno_id": "t1", "mensagem_atual": "Quero brocas 8 mm, 2 unidades"}
    first = asyncio.run(analista_compras.executar({}, context))
    assert first["analise_compra_pendente"]["status_fluxo"] == "aguardando_opcionais"
    assert "Se quiser" in first["analise_compra_pendente"]["pergunta_pendente"]
    assert calls == []

    context["turno_id"] = "t2"
    context["mensagem_atual"] = "não"
    second = asyncio.run(analista_compras.executar({}, context))
    assert len(calls) == 1 and calls[0][1] == 5
    assert second["analise_compra_pendente"]["status_fluxo"] == "concluida"
    assert "Não encontrei produtos" in second["resposta_especialista"]
