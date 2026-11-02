"""Coordena a coleta, a consulta de promoções e a persistência da compra."""


import json
import logging
import re
from datetime import datetime, timezone

from app.agents.compras.avaliacao import avaliar as _avaliar, normalizar as _normalizar, oferta_sem_avaliacao
from app.agents.compras.coleta import (
    DadosCompra, campos_prioritarios_ausentes as _campos_prioritarios_ausentes,
    dados_persistiveis as _dados_persistiveis, extrair as _extrair, opcionais_ausentes, pergunta_opcionais,
)
from app.agents.compras.consulta import consultar as consultar_ofertas
from app.agents.compras.respostas import resposta_ofertas as _resposta_ofertas
from app.mcp.pechincha import ErroPechincha, listar_lojas
from app.memory.persistencia.analise_compra import (
    atualizar_analise_compra, obter_analise_compra, salvar_analise_compra,
)

from app.core.respostas import MENSAGENS
from app.graph.respostas_padrao import (
    resposta_cobertura_lojas,
    resposta_busca_compra,
    resposta_erro_compra,
)

LOGGER = logging.getLogger(__name__)


def _pede_cobertura(mensagem: str) -> bool:
    texto = _normalizar(mensagem)
    return bool(re.search(r"\b(?:quais|que) lojas\b", texto)) and bool(
        "pechincha" in texto or re.search(r"\b(?:cobre|atende)\b", texto)
    )


async def _responder_cobertura(estado: dict) -> dict:
    evidencias = list(estado.get("evidencias", []))
    try:
        lojas = await listar_lojas()
        amostra = [loja for loja in lojas[:5] if isinstance(loja, dict)]
        nomes = [str(loja.get("name") or loja.get("nome") or loja.get("slug") or "") for loja in amostra]
        resposta = resposta_cobertura_lojas(nomes)
        evidencias.append(json.dumps({"ferramenta": "list_stores", "status_execucao": "success",
            "status_operacao": "sucesso", "resultado": {"lojas": amostra}}, ensure_ascii=False))
    except ErroPechincha as exc:
        resposta = MENSAGENS['nao_foi_possivel_consultar_as_lojas_do_pechincha_ai_agora']
        evidencias.append(json.dumps({"ferramenta": "list_stores", "status_execucao": "error",
            "status_operacao": exc.codigo, "resultado": {}}, ensure_ascii=False))
    return {"resposta_especialista": resposta, "evidencias": evidencias, "erro": None}


async def executar(estado: dict, contexto: dict) -> dict:
    usuario = contexto["usuario"]
    if usuario.tipo_acesso.lower() not in {"tecnico", "gestor", "administrador"}:
        return {"resposta_especialista": MENSAGENS['esta_pesquisa_de_compras_esta_disponivel_para_tecnicos_administradores_e_gestores'],
                "erro": None}
    if _pede_cobertura(contexto["mensagem_atual"]):
        return await _responder_cobertura(estado)

    sessao_id, usuario_id = contexto["session_id"], usuario.usuario_id
    anterior = await obter_analise_compra(sessao_id, usuario_id)
    if isinstance(anterior, dict) and anterior.get("pausado"):
        anterior = None
    dados = await _extrair(contexto["mensagem_atual"], anterior,
                           bool((anterior or {}).get("opcionais_oferecidos")))
    faltantes = _campos_prioritarios_ausentes(dados)
    oferecidos = bool((anterior or {}).get("opcionais_oferecidos")) or bool(dados.recusou_opcionais)
    if faltantes:
        status = "coletando_dados"
        resposta = MENSAGENS['para_pesquisar_informe_o_nome_do_item_que_deseja_comprar']
    elif not oferecidos and (opcionais_ausentes(dados) or dados.questao_compatibilidade):
        status = "aguardando_opcionais"
        oferecidos = True
        resposta = pergunta_opcionais(dados)
    else:
        status = "pronto_para_busca"
        resposta = ""

    rascunho = await salvar_analise_compra(
        sessao_id, usuario_id, dados=_dados_persistiveis(dados), status_fluxo=status,
        opcionais_oferecidos=oferecidos, turno_id=contexto["turno_id"],
        pergunta_pendente=resposta or None,
    )
    evidencias = [*estado.get("evidencias", []), json.dumps({
        "ferramenta": "estado_analise_compra_persistida", "status_execucao": "success",
        "status_operacao": status, "resultado": {"id": rascunho["id"], "versao": rascunho["versao"],
        "dados": rascunho["dados"], "opcionais_oferecidos": oferecidos},
    }, ensure_ascii=False)]
    if resposta:
        return {"analise_compra_pendente": rascunho, "evidencias": evidencias,
                "resposta_especialista": resposta, "erro": None}

    try:
        resultado = await consultar_ofertas(dados)
        produtos = resultado["ofertas"]
        try:
            ofertas, diferencas = await _avaliar(dados, produtos) if produtos else ([], "")
        except Exception:
            LOGGER.exception("Falha na avaliação das promoções")
            ofertas = [oferta for p in produtos if (oferta := oferta_sem_avaliacao(dados, p))]
            diferencas = ""
        ofertas = ofertas[:3]
        resposta = resposta_busca_compra(produtos, ofertas, diferencas)
        status_busca = "sem_resultado" if not produtos else "sucesso"
        resumo = {"status": status_busca, "consultada_em": datetime.now(timezone.utc).isoformat(),
                  "ofertas": ofertas}
        rascunho = await atualizar_analise_compra(
            sessao_id, usuario_id, id_analise=rascunho["id"], versao=rascunho["versao"],
            status_esperado="pronto_para_busca", campos={"status_fluxo": "concluida", "ultima_busca": resumo},
            exigir_ativo=True,
        )
        evidencias.append(json.dumps({"ferramenta": "search_deals", "status_execucao": "success",
            "status_operacao": status_busca, "resultado": {"promocoes_recebidas": len(produtos),
            "ofertas": ofertas}}, ensure_ascii=False))
    except ErroPechincha as exc:
        rascunho = await atualizar_analise_compra(
            sessao_id, usuario_id, id_analise=rascunho["id"], versao=rascunho["versao"],
            status_esperado="pronto_para_busca", campos={"status_fluxo": "erro_busca",
            "ultima_busca": {"status": exc.codigo, "consultada_em": datetime.now(timezone.utc).isoformat()}},
            exigir_ativo=True,
        )
        evidencias.append(json.dumps({"ferramenta": "search_deals", "status_execucao": "error",
            "status_operacao": exc.codigo, "resultado": {}}, ensure_ascii=False))
        resposta = resposta_erro_compra(exc.codigo, exc)
    return {"analise_compra_pendente": rascunho, "evidencias": evidencias,
            "resposta_especialista": resposta, "erro": None}
