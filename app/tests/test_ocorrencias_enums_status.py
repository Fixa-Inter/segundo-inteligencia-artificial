import asyncio
import json
import re
from contextlib import asynccontextmanager
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock

import httpx
import pytest
from pydantic import ValidationError
from app.services.operacoes import dados_cadastro

from app.services.ocorrencias import criarOcorrencia as servico
from app.services.ordensServico import buscarOrdensServico as servico_ordens
from app.services.tecnicos import buscarTecnicosDisponiveis as servico_tecnicos
from app.tools.toolsRequest import CriarOcorrenciaEntrada

ROOT = Path(__file__).resolve().parents[2]


def dados():
    return dict(local_endereco_id=6, categoria_equipamento_id=2,
                categoria_problema_id="INFORMATICA", prioridade="ALTA",
                titulo="Notebook reparado", descricao_ocorrencia="Notebook reparado",
                descricao_local="Sala de aula")


@pytest.mark.parametrize("codigo,esperado", [(200,"SUCESSO"),(201,"SUCESSO"),(204,"SUCESSO"),
    (202,"RESULTADO_INDETERMINADO"),(400,"ERRO_API"),(401,"ERRO_API"),(403,"ERRO_API"),
    (422,"ERRO_API"),(500,"RESULTADO_INDETERMINADO"),(503,"RESULTADO_INDETERMINADO")])
def test_contrato_http_sem_repetir_post(monkeypatch, codigo, esperado):
    cliente = AsyncMock()
    cliente.__aenter__.return_value = cliente
    cliente.post.return_value = httpx.Response(codigo, json={"id": 9, "titulo": "Notebook reparado"})
    monkeypatch.setattr(servico.httpx, "AsyncClient", Mock(return_value=cliente))
    monkeypatch.setattr(servico, "FIXA_URL_BASE_API", "https://example.com")
    result = asyncio.run(servico.adicionar_ocorrencia(CriarOcorrenciaEntrada(**dados()),
        "token-teste", usuario_id=7, imagens=["https://example.com/foto.jpg"]))
    assert result["status"] == esperado
    assert result["http_status"] == codigo
    cliente.post.assert_awaited_once()
    spec = json.loads((ROOT / "docs/api/swagger.json").read_text(encoding="utf-8"))
    schema = spec["components"]["schemas"]["OcorrenciaCadastrarInputDTO"]
    conteudo = cliente.post.call_args.kwargs["json"]
    assert set(conteudo) == set(schema["required"])
    for field in ("categoriaProblemaId", "prioridade"):
        assert conteudo[field] in schema["properties"][field]["enum"]
    assert conteudo["localUnidadeId"] == 6
    assert conteudo["categoriaEquipamentoId"] == 2
    assert conteudo["urlsFoto"] == ["https://example.com/foto.jpg"]


def test_limites_e_numeros_rejeitados():
    for campo, valor in [("titulo", "x"*101), ("descricao_ocorrencia", "x"*256),
                         ("descricao_local", "x"*256), ("prioridade", 0), ("categoria_problema_id", 4)]:
        with pytest.raises(ValidationError):
            CriarOcorrenciaEntrada(**{**dados(), campo: valor})


@pytest.mark.parametrize("prioridade,identificador", [("ALTA",0),("MEDIA",1),("BAIXA",2)])
def test_prioridade_e_status_fixos(monkeypatch, prioridade, identificador):
    select = AsyncMock(return_value=[])
    monkeypatch.setattr(servico_ordens, "executar_consulta", select)
    result = asyncio.run(servico_ordens.buscar_ordens_servico(
        SimpleNamespace(tipo_acesso="gestor", usuario_id=7), prioridade=prioridade, status="Concluída"))
    assert result["status"] == "SEM_RESULTADO"
    assert select.call_args.args[2]["prioridade"] == identificador
    assert select.call_args.args[2]["status_id"] == 4
    assert "os.status_ordem_servico = :status_id" in select.call_args.args[1]


def test_enums_documentados():
    def enum(nome):
        return re.findall(r'(\w+)\("([^"]+)",\s*(\d+)\)', (ROOT / f"docs/enum/{nome}.txt").read_text(encoding="utf-8"))
    assert servico_ordens.CATEGORIA_PROBLEMA_POR_ID == {int(n):label for _,label,n in enum("categoriaProblema")}
    assert servico_ordens.PRIORIDADE_POR_ID == {int(n):key for key,_,n in enum("prioridade")}
    schema = CriarOcorrenciaEntrada.model_json_schema()
    assert set(schema["properties"]["categoria_problema_id"]["enum"]) == {key for key,_,_ in enum("categoriaProblema")}
    assert set(schema["properties"]["prioridade"]["enum"]) == {key for key,_,_ in enum("prioridade")}


def test_tecnicos_contam_status_por_id(monkeypatch):
    select = AsyncMock(return_value=[dict(id=1, nome_completo="Ana", total_ordens=4, ordens_nao_concluidas=0),
                                    dict(id=2, nome_completo="Bia", total_ordens=2, ordens_nao_concluidas=1)])
    monkeypatch.setattr(servico_tecnicos, "executar_consulta", select)
    r=asyncio.run(servico_tecnicos.buscar_tecnicos_disponiveis(SimpleNamespace(tipo_acesso="gestor",usuario_id=7)))
    assert [t["id"] for t in r["tecnicos"]] == [1]
    assert "os.status_ordem_servico <> 4" in select.call_args.args[1]


@pytest.mark.parametrize("foto_inicial", [True,False])
def test_confirmacao_foto_e_protecao_duplicidade(monkeypatch, foto_inicial):
    from app.tools.ocorrencias import criarOcorrencia as modulo_ferramenta
    usuario = SimpleNamespace(tipo_acesso="tecnico",usuario_id=7,cnpj_endereco="12345678000199",access_token="teste")
    contexto = {"mensagem_atual":"Pode registrar a ocorrência", "turno_id":"confirmacao", "imagens": []}
    monkeypatch.setattr(modulo_ferramenta,"_contexto",lambda runtime:(contexto,usuario,"sessao"))
    rascunho = {"dados":dados(),"status_fluxo":"aguardando_confirmacao","confirmado":False,
                "imagens":["https://example.com/foto.jpg"] if foto_inicial else []}
    rascunho.update(id="proposta", tipo="ocorrencia", versao=1, turno_id="proposta",
                    turno_apresentacao="apresentacao", versao_apresentada=1,
                    dados_apresentados=rascunho["dados"].copy())
    monkeypatch.setattr(modulo_ferramenta,"obter_rascunho_solicitacao",AsyncMock(return_value=rascunho))
    async def atualizar(session, user, campos, **kwargs):
        assert kwargs["tipo"] == "ocorrencia"
        if rascunho["status_fluxo"] not in kwargs["status_esperados"]:return False
        rascunho.update(campos)
        return True
    monkeypatch.setattr(modulo_ferramenta,"atualizar_rascunho_solicitacao",atualizar)
    @asynccontextmanager
    async def qdrant():yield object()
    monkeypatch.setattr(modulo_ferramenta,"abrir_cliente_qdrant",qdrant)
    monkeypatch.setattr(modulo_ferramenta,"validar_selecao",AsyncMock())
    monkeypatch.setattr(modulo_ferramenta,"obter_unidade_id",AsyncMock(return_value=1))
    cadastrar = AsyncMock(return_value={"status":"SUCESSO","ocorrencia_id":19})
    monkeypatch.setattr(modulo_ferramenta,"adicionar_ocorrencia",cadastrar)
    monkeypatch.setattr(modulo_ferramenta, "preparar_operacao", AsyncMock(return_value={"status": "OPERACAO_PREPARADA"}))
    async def fluxo():
        if not foto_inicial:
            assert (await modulo_ferramenta.criar_ocorrencia.coroutine(None))["status"] == "AGUARDANDO_INFORMACAO"
            cadastrar.assert_not_awaited()
            assert rascunho["confirmado"] is True
            rascunho["imagens"]=["https://example.com/foto.jpg"]
            contexto["mensagem_atual"]="Segue a foto"
            contexto["imagens"] = rascunho["imagens"]
        assert (await modulo_ferramenta.criar_ocorrencia.coroutine(None))["status"] == "OPERACAO_PREPARADA"
        cadastrar.assert_not_awaited()
        assert (await modulo_ferramenta.processar_ocorrencia(
            None, operacao_aprovada=dados_cadastro(rascunho),
        ))["status"] == "SUCESSO"
        assert (await modulo_ferramenta.criar_ocorrencia.coroutine(None))["status"] == "SUCESSO"
    asyncio.run(fluxo())
    cadastrar.assert_awaited_once()
    assert cadastrar.call_args.kwargs["imagens"] == ["https://example.com/foto.jpg"]
