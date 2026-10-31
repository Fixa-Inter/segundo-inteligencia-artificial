"""Schemas públicos, autorização e execução real do SDK sem bancos externos."""

import asyncio
import json
from datetime import date
from typing import Annotated, TypedDict
from unittest.mock import AsyncMock

from langchain.tools import ToolRuntime
from langchain_core.messages import AIMessage, BaseMessage
from langgraph.graph import END, StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode
import pytest

from app.core.tempo import agora_local
from app.graph.contexto import ContextoGrafo
from app.schemas import UsuarioContexto
from app.schemas.visualizacao import (
    DadosCategorias, MetadadosConsultaVisualizacao, PeriodoVisualizacao,
    PontoCategoria, ResultadoConsultaVisualizacao,
)
from app.services.indicadores.gerais import databricks
from app.services.visualizacoes import ANALISES, _DOMINIOS
from app.tools.metricas_kpis import contexto as contexto_indicadores
from app.tools.visualizacoes import FERRAMENTAS_VISUALIZACOES
from app.tools.visualizacoes.contexto import MENSAGEM_BLOQUEIO_MOBILE


FERRAMENTAS = {t.name.removeprefix("consultar_visualizacao_"): t for t in FERRAMENTAS_VISUALIZACOES}
MATRIZ = [(a.fonte.id, a.id) for a in ANALISES.values()]


def usuario(perfil="gestor", usuario_id=10):
    return UsuarioContexto(
        access_token="segredo-token-teste", usuario_id=usuario_id, nome_completo="Pessoa teste",
        email="teste@example.com", tipo_acesso=perfil, cnpj_endereco="12345678000195",
    )


def runtime(perfil="gestor", usuario_id=10, contexto=None):
    return ToolRuntime(
        state={"perfil": "gestor", "unidade_id": 888, "user_id": 999},
        context={"usuario": usuario(perfil, usuario_id), "unidade_id": 999} if contexto is None else contexto,
        config={"configurable": {"unidade_id": 777}}, stream_writer=lambda _: None,
        tool_call_id="consulta-teste", store=None,
    )


def argumentos(analise_id="VIS-01"):
    a = ANALISES[analise_id]
    dados = {"analise_id": analise_id, "filtros": {}}
    if a.fonte.campo_periodo:
        dados["periodo"] = {"inicio": "2026-10-01", "fim": "2026-10-04"}
        dados["granularidade"] = "dia" if a.formato_dados == "serie_temporal" else None
    return dados


def resultado_vazio(consulta, unidade_id):
    a = ANALISES[consulta.analise_id]
    aplicados = {**consulta.filtros, "unidade_id": unidade_id}
    aplicados.update({f.campo: f.valor for f in a.filtros_obrigatorios})
    return ResultadoConsultaVisualizacao(
        status="SEM_RESULTADO", mensagem="Sem registros.",
        metadados=MetadadosConsultaVisualizacao(
            analise_id=a.id, fonte=a.fonte.tabela, formato_dados=a.formato_dados,
            campo_valor=a.campo_valor, agregacao=a.agregacao, unidade_medida=a.unidade_medida,
            escala_percentual=a.escala_percentual, periodo=getattr(consulta, "periodo", None),
            granularidade=getattr(consulta, "granularidade", None), consultado_em=agora_local(),
            consulta_id="consulta-teste", filtros_solicitados=consulta.filtros,
            filtros_aplicados=aplicados, qtd_registros_considerados=0,
        ),
    )


@pytest.fixture(autouse=True)
def dependencias(monkeypatch):
    monkeypatch.setenv("LANGSMITH_TRACING", "false")
    monkeypatch.setenv("LANGCHAIN_TRACING_V2", "false")
    resolver = AsyncMock(return_value=7)
    monkeypatch.setattr(contexto_indicadores, "obter_unidade_id", resolver)
    banco = AsyncMock(return_value=[])
    monkeypatch.setattr(databricks, "executar_consulta", banco)
    servicos, originais = {}, {}
    for dominio in _DOMINIOS:
        originais[dominio.FONTE.id] = dominio.consultar

        async def consultar(consulta, *, unidade_id):
            return resultado_vazio(consulta, unidade_id)

        servicos[dominio.FONTE.id] = AsyncMock(side_effect=consultar)
        monkeypatch.setattr(dominio, "consultar", servicos[dominio.FONTE.id])
    return resolver, servicos, banco, originais


def invocar(fonte="os_criacao", dados=None, contexto_runtime=None):
    entrada = {**(argumentos() if dados is None else dados), "runtime": contexto_runtime or runtime()}
    resultado = asyncio.run(FERRAMENTAS[fonte].ainvoke(entrada))
    return json.loads(resultado) if isinstance(resultado, str) else resultado


@pytest.mark.parametrize("fonte", tuple(FERRAMENTAS))
def test_mobile_nao_executa_tool_mesmo_com_gestor_valido(dependencias, fonte):
    resolver, servicos, banco, _ = dependencias
    analise_id = next(a.id for a in ANALISES.values() if a.fonte.id == fonte)
    contexto_runtime = runtime(contexto={"usuario": usuario(), "plataforma": "mobile"})
    resultado = invocar(fonte, argumentos(analise_id), contexto_runtime)
    assert resultado["status"] == "ACESSO_NEGADO"
    assert resultado["mensagem"] == MENSAGEM_BLOQUEIO_MOBILE
    resolver.assert_not_awaited()
    for servico in servicos.values():
        servico.assert_not_awaited()
    banco.assert_not_awaited()


@pytest.mark.parametrize("fonte", tuple(FERRAMENTAS))
def test_schema_mostra_so_argumentos_e_analises_da_fonte(fonte):
    ferramenta = FERRAMENTAS[fonte]
    schema = ferramenta.tool_call_schema.model_json_schema()
    propriedades = schema["properties"]
    esperado = {"analise_id", "filtros"} if fonte == "os_atual" else {"analise_id", "filtros", "periodo", "granularidade"}
    assert set(propriedades) == esperado
    assert set(propriedades["analise_id"]["enum"]) == {a.id for a in ANALISES.values() if a.fonte.id == fonte}
    assert ferramenta.args_schema.model_config["extra"] == "forbid"
    assert ferramenta._injected_args_keys == {"runtime"}
    assert "access_token" not in json.dumps(schema) and "cnpj_endereco" not in json.dumps(schema)
    assert ferramenta.return_direct is False


@pytest.mark.parametrize("fonte,analise_id", MATRIZ)
def test_27_analises_resolvem_unidade_no_servidor_e_despacham_no_dominio(dependencias, fonte, analise_id):
    resolver, servicos, banco, _ = dependencias
    contexto_runtime = runtime()
    resultado = invocar(fonte, argumentos(analise_id), contexto_runtime)
    assert resultado["status"] == "SEM_RESULTADO"
    assert resultado["metadados"]["filtros_aplicados"]["unidade_id"] == 7
    assert resultado["metadados"]["analise_id"] == analise_id
    resolver.assert_awaited_once_with(contexto_runtime.context["usuario"])
    servicos[fonte].assert_awaited_once()
    assert servicos[fonte].await_args.kwargs == {"unidade_id": 7}
    assert servicos[fonte].await_args.args[0].analise_id == analise_id
    for outra, servico in servicos.items():
        if outra != fonte:
            servico.assert_not_awaited()
    banco.assert_not_awaited()
    json.dumps(resultado, allow_nan=False)
    ResultadoConsultaVisualizacao.model_validate(resultado)


@pytest.mark.parametrize("fonte", tuple(FERRAMENTAS))
def test_analise_de_outra_fonte_e_rejeitada_antes_da_unidade(dependencias, fonte):
    resolver, servicos, _, _ = dependencias
    permitido = next(a.id for a in ANALISES.values() if a.fonte.id == fonte)
    dados = argumentos(permitido)
    dados["analise_id"] = "VIS-01" if fonte != "os_criacao" else "VIS-02"
    resultado = invocar(fonte, dados)
    assert resultado["status"] == "ERRO_VALIDACAO"
    resolver.assert_not_awaited()
    servicos[fonte].assert_not_awaited()


@pytest.mark.parametrize("perfil", ["solicitante", "tecnico", "administrador", "desconhecido"])
def test_outros_perfis_nao_sao_autorizados_pelo_estado_que_diz_gestor(dependencias, perfil):
    resolver, servicos, banco, _ = dependencias
    assert invocar(contexto_runtime=runtime(perfil))["status"] == "ACESSO_NEGADO"
    resolver.assert_not_awaited()
    servicos["os_criacao"].assert_not_awaited()
    banco.assert_not_awaited()


@pytest.mark.parametrize("contexto", [{}, {"usuario": {}}, {"usuario": None}, {"unidade_id": 7}])
def test_contexto_nao_autenticado_nao_pode_ser_substituido_por_id_solto(dependencias, contexto):
    resolver, _, banco, _ = dependencias
    assert invocar(contexto_runtime=runtime(contexto=contexto))["status"] == "ACESSO_NEGADO"
    resolver.assert_not_awaited()
    banco.assert_not_awaited()


def test_runtime_ausente_e_negado_sem_excecao_de_assinatura(dependencias):
    resolver, _, _, _ = dependencias
    resultado = asyncio.run(FERRAMENTAS["os_criacao"].ainvoke(argumentos()))
    assert resultado["status"] == "ACESSO_NEGADO"
    resolver.assert_not_awaited()


@pytest.mark.parametrize("identificador", [0, -1, True, "10"])
def test_usuario_invalido_ou_adulterado_e_negado(dependencias, identificador):
    resolver, _, _, _ = dependencias
    contexto_runtime = runtime()
    contexto_runtime.context["usuario"] = usuario().model_copy(update={"usuario_id": identificador})
    assert invocar(contexto_runtime=contexto_runtime)["status"] == "ACESSO_NEGADO"
    resolver.assert_not_awaited()


@pytest.mark.parametrize("unidade", [None, True, 0, -1, "7", 7.0])
def test_unidade_resolvida_invalida_nao_vira_consulta_sem_escopo(dependencias, unidade):
    resolver, servicos, banco, _ = dependencias
    resolver.return_value = unidade
    assert invocar()["status"] == "ACESSO_NEGADO"
    servicos["os_criacao"].assert_not_awaited()
    banco.assert_not_awaited()


@pytest.mark.parametrize("erro,status", [
    (PermissionError("segredo-banco"), "ACESSO_NEGADO"),
    (ValueError("segredo-banco"), "ACESSO_NEGADO"),
    (RuntimeError("segredo-banco"), "ERRO_FERRAMENTA"),
])
def test_vinculo_nao_confirmado_nao_tem_fallback_ou_detalhes_sensiveis(dependencias, caplog, erro, status):
    resolver, servicos, banco, _ = dependencias
    resolver.side_effect = erro
    resultado = invocar()
    assert resultado["status"] == status and resultado["dados"] is None
    assert "segredo-banco" not in json.dumps(resultado) and "segredo-banco" not in caplog.text
    servicos["os_criacao"].assert_not_awaited()
    banco.assert_not_awaited()


@pytest.mark.parametrize("campo", ["unidade_id", "instituicao_id", "fonte", "tabela", "sql", "usuario"])
def test_argumentos_protegidos_nao_sao_aceitos_pelo_sdk(dependencias, campo):
    resolver, _, _, _ = dependencias
    resultado = invocar(dados={**argumentos(), campo: "segredo-modelo"})
    assert resultado["status"] == "ERRO_VALIDACAO"
    assert "segredo-modelo" not in json.dumps(resultado) and "segredo-token" not in json.dumps(resultado)
    resolver.assert_not_awaited()


def test_runtime_em_json_nao_e_tratado_como_objeto_injetado(dependencias):
    resolver, _, _, _ = dependencias
    resultado = asyncio.run(FERRAMENTAS["os_criacao"].ainvoke({
        **argumentos(), "runtime": {"context": {"usuario": usuario().model_dump()}},
    }))
    resultado = json.loads(resultado)
    assert resultado["status"] == "ERRO_VALIDACAO" and "segredo-token" not in json.dumps(resultado)
    resolver.assert_not_awaited()


@pytest.mark.parametrize("campo,valor", [("periodo", None), ("granularidade", None), ("periodo", {"inicio": "2026-10-01", "fim": "2026-10-04"})])
def test_snapshot_recusa_campos_temporais_mesmo_nulos(dependencias, campo, valor):
    resolver, _, _, _ = dependencias
    assert invocar("os_atual", {**argumentos("VIS-03"), campo: valor})["status"] == "ERRO_VALIDACAO"
    resolver.assert_not_awaited()


@pytest.mark.parametrize("filtros", [
    {"unidade_id": 8}, {"sql": "SELECT 1"}, {"local_id": "7"},
    {"local_id": list(range(51))}, {"status_problema_id": 1},
])
def test_filtros_invalidos_sao_rejeitados_antes_de_resolver_unidade(dependencias, filtros):
    resolver, _, _, _ = dependencias
    assert invocar(dados={**argumentos(), "filtros": filtros})["status"] == "ERRO_VALIDACAO"
    resolver.assert_not_awaited()


def test_periodo_e_granularidade_incompativeis_sao_rejeitados_sem_banco(dependencias):
    resolver, _, _, _ = dependencias
    dados = argumentos()
    dados["periodo"] = {"inicio": "2025-01-01", "fim": "2026-01-03"}
    assert invocar(dados=dados)["status"] == "ERRO_VALIDACAO"
    assert invocar(dados={**argumentos(), "granularidade": None})["status"] == "ERRO_VALIDACAO"
    resolver.assert_not_awaited()


def test_filtros_textuais_de_recorrencia_mantem_zeros_e_multiplos_valores(dependencias):
    _, servicos, _, _ = dependencias
    dados = {**argumentos("VIS-13"), "filtros": {"local_id": ["001", "1"]}}
    resultado = invocar("recorrencia", dados)
    assert resultado["status"] == "SEM_RESULTADO"
    assert servicos["recorrencia"].await_args.args[0].filtros == {"local_id": ["001", "1"]}


@pytest.mark.parametrize("status", ["TIMEOUT", "RESULTADO_TRUNCADO", "SEM_BASE_CALCULO", "ERRO_FERRAMENTA"])
def test_status_dos_servicos_nao_sao_convertidos_em_graficos(dependencias, status):
    _, servicos, _, _ = dependencias
    servicos["os_criacao"].side_effect = None
    servicos["os_criacao"].return_value = ResultadoConsultaVisualizacao(status=status, mensagem="Sem gráfico.")
    resultado = invocar()
    assert resultado["status"] == status and resultado["dados"] is None


@pytest.mark.parametrize("alteracao", [
    {"analise_id": "VIS-02"}, {"fonte": "outra_fonte"}, {"campo_valor": "outra_medida"},
    {"granularidade": "mes"}, {"filtros_solicitados": {"local_id": 8}},
    {"filtros_aplicados": {"unidade_id": 999}}, {"filtros_nao_aplicados": ["local_id"]},
])
def test_resultado_de_consulta_diferente_nao_e_liberado(dependencias, alteracao):
    _, servicos, _, _ = dependencias
    async def resposta(consulta, *, unidade_id):
        resultado = resultado_vazio(consulta, unidade_id)
        resultado.metadados = resultado.metadados.model_copy(update=alteracao)
        return resultado
    servicos["os_criacao"].side_effect = resposta
    assert invocar()["status"] == "ERRO_FERRAMENTA"


def test_excecao_inesperada_do_servico_nao_vaza_detalhes(dependencias, caplog):
    _, servicos, _, _ = dependencias
    servicos["os_criacao"].side_effect = RuntimeError("segredo-servico")
    resultado = invocar()
    assert resultado["status"] == "ERRO_FERRAMENTA" and resultado["dados"] is None
    assert "segredo-servico" not in json.dumps(resultado) and "segredo-servico" not in caplog.text


def test_chamadas_concorrentes_nao_compartilham_unidade_resolvida(dependencias):
    resolver, _, _, _ = dependencias
    async def resolver_usuario(usuario):
        return 7 if usuario.usuario_id == 10 else 8
    resolver.side_effect = resolver_usuario
    async def executar():
        return await asyncio.gather(*[
            FERRAMENTAS["os_criacao"].ainvoke({**argumentos(), "runtime": runtime(usuario_id=id_)})
            for id_ in (10, 20)
        ])
    resultados = asyncio.run(executar())
    assert [r["metadados"]["filtros_aplicados"]["unidade_id"] for r in resultados] == [7, 8]
    assert resolver.await_count == 2


def test_argumentos_sao_copiados_antes_do_await_de_unidade(dependencias):
    resolver, servicos, _, _ = dependencias
    filtros = {"local_id": [1]}
    periodo = PeriodoVisualizacao(inicio="2026-10-01", fim="2026-10-04")
    async def resolver_mutando(_usuario):
        filtros["local_id"].append(2)
        periodo.fim = date(2026, 10, 5)
        return 7
    resolver.side_effect = resolver_mutando
    dados = {**argumentos(), "filtros": filtros, "periodo": periodo}
    resultado = asyncio.run(FERRAMENTAS["os_criacao"].coroutine(**dados, runtime=runtime()))
    assert resultado["status"] == "SEM_RESULTADO"
    assert servicos["os_criacao"].await_args.args[0].filtros == {"local_id": [1]}
    assert servicos["os_criacao"].await_args.args[0].periodo.fim == date(2026, 10, 4)


def test_resposta_fora_dos_limites_nao_e_liberada_mesmo_se_servico_nao_validar(dependencias):
    _, servicos, _, _ = dependencias
    async def resposta(consulta, *, unidade_id):
        vazio = resultado_vazio(consulta, unidade_id)
        return ResultadoConsultaVisualizacao(
            status="SUCESSO", mensagem="Dados.", metadados=vazio.metadados,
            dados=DadosCategorias(pontos=[
                PontoCategoria(grupo={"status_id": i, "status_os": str(i)}, valor=1, qtd_registros=1)
                for i in range(51)
            ]),
        )
    servicos["os_atual"].side_effect = resposta
    resultado = invocar("os_atual", argumentos("VIS-03"))
    assert resultado["status"] == "ERRO_FERRAMENTA" and resultado["dados"] is None


class EstadoTeste(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]


def executar_no_toolnode(args, contexto):
    grafo = StateGraph(EstadoTeste, context_schema=ContextoGrafo)
    grafo.add_node("ferramentas", ToolNode(FERRAMENTAS_VISUALIZACOES))
    grafo.set_entry_point("ferramentas")
    grafo.add_edge("ferramentas", END)
    resultado = asyncio.run(grafo.compile().ainvoke({"messages": [AIMessage(
        content="", tool_calls=[{"name": FERRAMENTAS["os_criacao"].name, "args": args, "id": "call-teste", "type": "tool_call"}],
    )]}, context=contexto))
    return resultado["messages"][-1]


def test_toolnode_injeta_runtime_e_preserva_resultado_json_real(dependencias, monkeypatch):
    resolver, _, banco, originais = dependencias
    dominio = next(d for d in _DOMINIOS if d.FONTE.id == "os_criacao")
    monkeypatch.setattr(dominio, "consultar", originais["os_criacao"])
    banco.return_value = [{"data_referencia": "2026-10-02", "valor": "3", "qtd_registros": "3"}]
    mensagem = executar_no_toolnode(argumentos(), {"usuario": usuario(), "unidade_id": 999})
    resultado = json.loads(mensagem.content)
    assert mensagem.tool_call_id == "call-teste" and mensagem.status == "success"
    assert resultado["status"] == "SUCESSO"
    assert [p["valor"] for p in resultado["dados"]["pontos"]] == [0, 3, 0]
    assert resultado["dados"]["pontos"][0]["data_referencia"] == "2026-10-01"
    assert resultado["metadados"]["filtros_aplicados"]["unidade_id"] == 7
    assert banco.await_args.args[1]["unidade_id"] == 7
    resolver.assert_awaited_once()
    ResultadoConsultaVisualizacao.model_validate(resultado)


def test_toolnode_nao_aceita_usuario_falso_no_runtime_do_modelo(dependencias):
    resolver, _, banco, _ = dependencias
    mensagem = executar_no_toolnode(
        {**argumentos(), "runtime": {"context": {"usuario": usuario().model_dump()}}},
        {"usuario": usuario("tecnico")},
    )
    assert json.loads(mensagem.content)["status"] == "ACESSO_NEGADO"
    resolver.assert_not_awaited()
    banco.assert_not_awaited()


def test_erro_de_schema_no_toolnode_tem_json_seguro(dependencias):
    resolver, _, _, _ = dependencias
    mensagem = executar_no_toolnode({**argumentos(), "unidade_id": "segredo-modelo"}, {"usuario": usuario()})
    assert mensagem.status == "error"
    assert json.loads(mensagem.content)["status"] == "ERRO_VALIDACAO"
    assert "segredo-modelo" not in mensagem.content
    resolver.assert_not_awaited()
