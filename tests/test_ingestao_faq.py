"""Contratos da ingestão: corpus por perfil, isolamento e preservação em falhas, sem rede."""

import asyncio
from contextlib import asynccontextmanager
from importlib import import_module
from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock

import pytest
from langchain_core.documents import Document
from qdrant_client import AsyncQdrantClient, models


@pytest.fixture
def ingestao():
    """Obtém o módulo proprietário para substituir somente integrações externas."""
    return import_module("app.memory.embedding.popular_banco_vetorial")


@pytest.fixture
def comando():
    """Obtém a entrada operacional sem executar o comando de ingestão."""
    return import_module("app.scripts.ingerir_faq")


@pytest.fixture
def fontes(tmp_path):
    """Cria dois documentos comuns e um manual exclusivo de cada perfil."""
    arquivos = {
        "fixa/institucional.md": "Contexto institucional compartilhado.",
        "fixa/politica.md": "Política operacional compartilhada.",
        "mobile/solicitante/manual.md": "Procedimento exclusivo do solicitante.",
        "mobile/tecnico/manual.md": "Procedimento exclusivo do técnico.",
        "mobile/gestor/manual.md": "Procedimento exclusivo do gestor.",
    }
    for relativo, texto in arquivos.items():
        caminho = tmp_path / relativo
        caminho.parent.mkdir(parents=True, exist_ok=True)
        caminho.write_text(texto, encoding="utf-8")
    return tmp_path


@pytest.fixture
def qdrant_simulado(monkeypatch, ingestao):
    """Captura mutações e evita qualquer abertura de cliente real em testes de falha."""
    cliente = SimpleNamespace(
        create_payload_index=AsyncMock(), upsert=AsyncMock(), delete=AsyncMock(),
    )

    @asynccontextmanager
    async def abrir():
        yield cliente

    fabrica = Mock(side_effect=abrir)
    monkeypatch.setattr(ingestao, "abrir_cliente_qdrant", fabrica)
    return cliente, fabrica


def test_documentos_reais_distribuem_fixa_e_somente_o_manual_do_perfil(comando):
    """Confere o inventário real usado pelo comando, sem ingerir dados externos."""
    plano = comando.descobrir_documentos_faq()
    comuns = {"Documento_FIXA.md", "Documento_politicas_uso.md"}
    for perfil, caminhos in plano.items():
        assert {caminho.name for caminho in caminhos} == comuns | {f"Documento_{perfil}.md"}
        assert all(caminho.is_absolute() and caminho.is_file() for caminho in caminhos)
        assert all(caminho.parent.name in {"fixa", perfil} for caminho in caminhos)
    assert set(plano) == {"solicitante", "tecnico", "gestor"}


def test_descoberta_inclui_subpastas_e_exclui_responsabilidades_e_outros_formatos(comando, fontes):
    """Arquitetura, outros perfis e arquivos que não são Markdown não entram no corpus."""
    (fontes / "fixa" / "responsabilidade.MD").write_text("INTERNAL", encoding="utf-8")
    (fontes / "mobile" / "tecnico" / "RESPONSABILIDADE.md").write_text("INTERNAL", encoding="utf-8")
    (fontes / "fixa" / "arquivo.txt").write_text("IGNORE", encoding="utf-8")
    subpasta = fontes / "mobile" / "tecnico" / "procedimentos"
    subpasta.mkdir()
    extra = subpasta / "Extra.MD"
    extra.write_text("Outro procedimento técnico.", encoding="utf-8")
    plano = comando.descobrir_documentos_faq(fontes)
    assert len(plano["solicitante"]) == len(plano["gestor"]) == 3
    assert len(plano["tecnico"]) == 4
    assert extra in plano["tecnico"]
    assert extra not in plano["solicitante"] and extra not in plano["gestor"]


@pytest.mark.parametrize("ausente", ["fixa", "solicitante", "tecnico", "gestor"])
def test_ausencia_de_fontes_impede_inicio_do_comando(monkeypatch, comando, fontes, ausente):
    """Um perfil incompleto deve ser detectado antes de atualizar qualquer outro perfil."""
    pasta = fontes / "fixa" if ausente == "fixa" else fontes / "mobile" / ausente
    for caminho in pasta.glob("*.md"):
        caminho.unlink()
    descobrir = comando.descobrir_documentos_faq
    monkeypatch.setattr(comando, "descobrir_documentos_faq", lambda: descobrir(fontes))
    indexar = AsyncMock()
    monkeypatch.setattr(comando, "ingerir_faq", indexar)
    with pytest.raises(ValueError):
        asyncio.run(comando.main())
    indexar.assert_not_awaited()


def test_comando_envia_corpus_completo_uma_vez_por_perfil(monkeypatch, comando, fontes):
    """Impede que a ingestão por arquivo deixe apenas o último documento no perfil."""
    plano = comando.descobrir_documentos_faq(fontes)
    monkeypatch.setattr(comando, "descobrir_documentos_faq", lambda: plano)
    indexar = AsyncMock()
    monkeypatch.setattr(comando, "ingerir_faq", indexar)
    asyncio.run(comando.main())
    assert [(chamada.args[0], chamada.args[1]) for chamada in indexar.await_args_list] == list(
        (caminhos, perfil) for perfil, caminhos in plano.items()
    )


def test_markdown_preserva_acentos_remove_bom_e_nao_repete_o_mesmo_arquivo(ingestao, tmp_path):
    """Conteúdo UTF-8 e origem permanecem utilizáveis pelo FAQ."""
    caminho = tmp_path / "guia.md"
    caminho.write_text("# Solicitações\n\nInformação de manutenção.", encoding="utf-8-sig")
    documentos = ingestao.carregar_documentos_faq([caminho, str(caminho)])
    assert len(documentos) == 1
    assert documentos[0].page_content == "# Solicitações\n\nInformação de manutenção."
    assert documentos[0].metadata == {"source": "guia.md"}


def test_pdf_legado_aceita_argumento_nomeado_e_preserva_paginas(monkeypatch, ingestao, tmp_path, qdrant_simulado):
    """Chamadores anteriores continuam aceitos; a leitura PDF é simulada sem dependência externa."""
    caminho = tmp_path / "guia.pdf"
    caminho.touch()
    carregador = Mock()
    carregador.load.return_value = [
        Document(page_content="Página inicial.", metadata={"page": 0}),
        Document(page_content="Página final.", metadata={"page": 1}),
    ]
    monkeypatch.setattr(ingestao, "PyPDFLoader", Mock(return_value=carregador))
    monkeypatch.setattr(ingestao, "gerar_vetores_documentos", AsyncMock(return_value=[[1.0, 0.0]] * 2))
    assert asyncio.run(ingestao.ingerir_faq(caminho_pdf=caminho, perfil="GESTOR")) == 2
    pontos = qdrant_simulado[0].upsert.await_args.kwargs["points"]
    assert [ponto.payload["page_number"] for ponto in pontos] == [0, 1]
    assert all(ponto.payload["source"] == "guia.pdf" for ponto in pontos)


@pytest.mark.parametrize("caso", ["lista_vazia", "ausente", "vazio", "formato", "utf8", "perfil"])
def test_fontes_invalidas_preservam_qdrant(monkeypatch, ingestao, tmp_path, qdrant_simulado, caso):
    """Entrada inválida não deve gerar vetores nem iniciar mutações no índice."""
    valido = tmp_path / "valido.md"
    valido.write_text("Documento válido.", encoding="utf-8")
    invalido = tmp_path / "outro.md"
    argumentos, perfil = [valido, invalido], "solicitante"
    if caso == "lista_vazia":
        argumentos = []
    elif caso == "vazio":
        invalido.write_text("  \n", encoding="utf-8")
    elif caso == "formato":
        invalido = tmp_path / "arquivo.txt"
        invalido.write_text("Texto não permitido.", encoding="utf-8")
        argumentos = [valido, invalido]
    elif caso == "utf8":
        invalido.write_bytes(b"\xff")
    elif caso == "perfil":
        argumentos, perfil = [valido], "visitante"
    gerar = AsyncMock()
    monkeypatch.setattr(ingestao, "gerar_vetores_documentos", gerar)
    with pytest.raises((ValueError, FileNotFoundError)):
        asyncio.run(ingestao.ingerir_faq(argumentos, perfil))
    gerar.assert_not_awaited()
    qdrant_simulado[1].assert_not_called()


@pytest.mark.parametrize("falha", ["excecao", "quantidade"])
def test_falha_em_embeddings_preserva_indice(monkeypatch, ingestao, fontes, qdrant_simulado, falha):
    """Falha do provedor ou retorno incompleto não deve remover o FAQ anterior."""
    gerar = AsyncMock(side_effect=RuntimeError("Indisponível")) if falha == "excecao" else AsyncMock(return_value=[])
    monkeypatch.setattr(ingestao, "gerar_vetores_documentos", gerar)
    with pytest.raises((RuntimeError, ValueError)):
        asyncio.run(ingestao.ingerir_faq(fontes / "fixa" / "politica.md", "tecnico"))
    qdrant_simulado[1].assert_not_called()


def test_falha_em_lote_de_publicacao_nao_remove_pontos_anteriores(monkeypatch, ingestao, fontes, qdrant_simulado):
    """Mesmo após publicar um lote, falha posterior não deve disparar a limpeza do perfil."""
    monkeypatch.setattr(ingestao, "TAMANHO_LOTE", 1)
    monkeypatch.setattr(ingestao, "gerar_vetores_documentos", AsyncMock(return_value=[[1.0, 0.0]]))
    cliente, _ = qdrant_simulado
    cliente.upsert.side_effect = [None, RuntimeError("Falha no segundo lote")]
    with pytest.raises(RuntimeError):
        asyncio.run(ingestao.ingerir_faq(sorted((fontes / "fixa").glob("*.md")), "gestor"))
    assert cliente.upsert.await_count == 2
    cliente.delete.assert_not_awaited()


def test_falha_na_limpeza_nao_anuncia_ingestao_concluida(monkeypatch, ingestao, fontes, qdrant_simulado, capsys):
    """Limpeza pendente deve ser reportada como falha para permitir correção operacional."""
    monkeypatch.setattr(ingestao, "gerar_vetores_documentos", AsyncMock(return_value=[[1.0, 0.0]]))
    qdrant_simulado[0].delete.side_effect = RuntimeError("Limpeza indisponível")
    with pytest.raises(RuntimeError):
        asyncio.run(ingestao.ingerir_faq(fontes / "fixa" / "politica.md", "gestor"))
    assert "Concluído" not in capsys.readouterr().out


def test_ingestao_local_mantem_comuns_isola_perfis_e_substitui_corpus(monkeypatch, ingestao, comando, fontes):
    """Exercita filtros reais do Qdrant em memória, incluindo limpeza e nova ingestão sem duplicatas."""
    plano = comando.descobrir_documentos_faq(fontes)
    monkeypatch.setattr(comando, "descobrir_documentos_faq", lambda: plano)
    monkeypatch.setattr(comando, "ingerir_faq", ingestao.ingerir_faq)

    async def gerar(textos):
        """Produz vetores locais de duas dimensões; não chama nenhum modelo externo."""
        return [[1.0, 0.0] for _ in textos]

    monkeypatch.setattr(ingestao, "gerar_vetores_documentos", gerar)

    async def verificar():
        cliente = AsyncQdrantClient(location=":memory:")
        try:
            await cliente.create_collection(
                collection_name=ingestao.QDRANT_COLECAO_FAQ,
                vectors_config=models.VectorParams(size=2, distance=models.Distance.COSINE),
            )

            @asynccontextmanager
            async def abrir():
                yield cliente

            monkeypatch.setattr(ingestao, "abrir_cliente_qdrant", abrir)
            await cliente.upsert(
                collection_name=ingestao.QDRANT_COLECAO_FAQ,
                points=[models.PointStruct(id=1, vector=[1.0, 0.0], payload={"perfil": "solicitante", "page_content": "OBSOLETO"})],
            )
            await comando.main()
            pontos, _ = await cliente.scroll(collection_name=ingestao.QDRANT_COLECAO_FAQ, limit=100)
            assert len(pontos) == 9
            for perfil in plano:
                corpus = [ponto.payload for ponto in pontos if ponto.payload["perfil"] == perfil]
                assert len(corpus) == 3
                assert {p["source"] for p in corpus} == {"institucional.md", "politica.md", "manual.md"}
                assert next(p["page_content"] for p in corpus if p["source"] == "manual.md") == (
                    fontes / "mobile" / perfil / "manual.md"
                ).read_text(encoding="utf-8")
            outros = {p.id for p in pontos if p.payload["perfil"] != "solicitante"}
            (fontes / "mobile" / "solicitante" / "manual.md").write_text("NOVO PROCEDIMENTO", encoding="utf-8")
            await ingestao.ingerir_faq(plano["solicitante"], "solicitante")
            atuais, _ = await cliente.scroll(collection_name=ingestao.QDRANT_COLECAO_FAQ, limit=100)
            assert len(atuais) == 9
            assert {p.id for p in atuais if p.payload["perfil"] != "solicitante"} == outros
            textos = [p.payload["page_content"] for p in atuais if p.payload["perfil"] == "solicitante"]
            assert "NOVO PROCEDIMENTO" in textos
            assert "Procedimento exclusivo do solicitante." not in textos
            assert all("OBSOLETO" not in texto for texto in textos)
        finally:
            await cliente.close()

    asyncio.run(verificar())
