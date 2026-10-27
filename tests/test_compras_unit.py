import asyncio
import json

from app.agents import analista_compras, juiz_compras
from app.agents.compras.coleta import DadosCompra, campos_prioritarios_ausentes
from app.agents.compras.consulta import consultar
from app.agents.orquestrador import pedido_compra_explicito, rotear_orquestrador
from app.graph.fluxo import grafo
from app.graph.nos import validar_saida


def test_purchase_routing_and_only_item_required():
    assert pedido_compra_explicito("Quais lojas o Pechincha.ai cobre?")
    assert asyncio.run(rotear_orquestrador({}, "Onde posso comprar brocas? ")).intencao == "analista_compras"
    assert "analista_compras" in grafo.nodes
    assert campos_prioritarios_ausentes(DadosCompra(item="broca")) == []
    assert campos_prioritarios_ausentes(DadosCompra(item=" ")) == ["nome do item"]
    assert analista_compras._pede_cobertura("Quais lojas o Pechincha cobre?")
    assert not analista_compras._pede_cobertura("Quais lojas têm brocas?")


def test_store_category_and_price_are_sent_as_filters(monkeypatch):
    from app.agents.compras import consulta

    async def stores(query):
        assert query == "Amazon"
        return [{"name": "Amazon", "slug": "amazon"}]

    async def categories():
        return [{"name": "Ferramentas", "slug": "ferramentas"}]

    async def search(busca):
        assert busca.model_dump(exclude_none=True) == {
            "query": "furadeira", "store": "amazon", "category": "ferramentas",
            "min_price": 100.0, "max_price": 500.0, "page": 1,
        }
        return {"ofertas": [], "total": 0}

    monkeypatch.setattr(consulta, "listar_lojas", stores)
    monkeypatch.setattr(consulta, "listar_categorias", categories)
    monkeypatch.setattr(consulta, "buscar_ofertas", search)
    asyncio.run(consultar(DadosCompra(item="furadeira", loja="Amazon", categoria="Ferramentas",
                                      min_price=100, max_price=500, quantidade="2")))


def test_product_link_survives_output_redaction():
    url = "https://pechincha.ai/p/12345678901/oferta"
    evidence = json.dumps({"ferramenta": "search_deals", "resultado": {"ofertas": [{"url": url}]}})
    result = validar_saida({"veredito": "aprovado", "intencao": "analista_compras",
                           "resposta_candidata": f"Oferta: {url}", "mapa_pii": {}, "evidencias": [evidence]})
    assert url in result["resposta_final"]


def test_purchase_judge_receives_compact_evidence(monkeypatch):
    offers = [{"loja": "Loja A", "descricao": "Furadeira de impacto com mandril 13 mm",
               "preco": 249.9, "url": f"https://pechincha.ai/p/{i}" + "x" * 70,
               "confirmados": ["mandril 13 mm"], "ausentes": ["220 V"],
               "motivo": "Promoção encontrada para comparação; confirme os requisitos ausentes."}
              for i in range(3)]
    answer = analista_compras._resposta_ofertas(offers, "")
    evidence = [
        json.dumps({"ferramenta": "estado_analise_compra_persistida", "status_operacao": "pronto_para_busca",
                    "resultado": {"dados": {"item": "furadeira", "requisitos_obrigatorios": ["220 V"]}}}),
        json.dumps({"ferramenta": "search_deals", "status_operacao": "sucesso",
                    "resultado": {"promocoes_recebidas": 3, "ofertas": offers}}),
    ]

    async def fake_jev(state, questions, *, operacao):
        assert len(json.dumps({"state": state, "questions": questions}, ensure_ascii=False)) <= 4000
        return {"answers": {"veredito": {"type": "choice", "choice": "aprovado", "confidence": 0.9},
                            "motivo": {"type": "choice", "choice": "nenhum", "confidence": 0.9}}}

    monkeypatch.setattr(juiz_compras, "consultar_jev", fake_jev)
    result = asyncio.run(juiz_compras.julgar_compra({"perfil": "tecnico", "resposta_especialista": answer,
                                                    "evidencias": evidence, "tentativas": 0}))
    assert result["veredito"] == "aprovado"


def test_purchase_draft_survives_optional_question_before_search(monkeypatch):
    saved = {}
    calls = []

    async def get_draft(*args):
        return saved.get("draft")

    async def extract(message, previous, question):
        return DadosCompra(item="broca", recusou_opcionais=message == "não")

    async def save(*args, **kwargs):
        draft = {"id": "d1", "versao": 1, "status_fluxo": kwargs["status_fluxo"],
                 "dados": kwargs["dados"], "opcionais_oferecidos": kwargs["opcionais_oferecidos"],
                 "pergunta_pendente": kwargs["pergunta_pendente"]}
        saved["draft"] = draft
        return draft

    async def update(*args, **kwargs):
        saved["draft"] = {**saved["draft"], **kwargs["campos"]}
        return saved["draft"]

    async def search(data):
        calls.append(data)
        return {"ofertas": [], "total": 0}

    monkeypatch.setattr(analista_compras, "obter_analise_compra", get_draft)
    monkeypatch.setattr(analista_compras, "_extrair", extract)
    monkeypatch.setattr(analista_compras, "salvar_analise_compra", save)
    monkeypatch.setattr(analista_compras, "atualizar_analise_compra", update)
    monkeypatch.setattr(analista_compras, "consultar_ofertas", search)

    user = type("User", (), {"tipo_acesso": "tecnico", "usuario_id": 7})()
    context = {"usuario": user, "session_id": "s1", "turno_id": "t1", "mensagem_atual": "Quero brocas"}
    first = asyncio.run(analista_compras.executar({}, context))
    assert first["analise_compra_pendente"]["status_fluxo"] == "aguardando_opcionais"
    assert "Se quiser" in first["analise_compra_pendente"]["pergunta_pendente"]
    assert calls == []

    context["turno_id"] = "t2"
    context["mensagem_atual"] = "não"
    second = asyncio.run(analista_compras.executar({}, context))
    assert len(calls) == 1 and calls[0].item == "broca"
    assert second["analise_compra_pendente"]["status_fluxo"] == "concluida"
    assert "Não encontrei promoções ativas" in second["resposta_especialista"]
