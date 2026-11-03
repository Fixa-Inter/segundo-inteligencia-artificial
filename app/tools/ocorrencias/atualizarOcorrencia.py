"""Seleção, proposta e aceite de atualização no mesmo rascunho de ocorrência."""

import logging
import re
from typing import Literal
from langchain.tools import ToolRuntime, tool
from app.core import aceite_explicito, normalizar_mensagem, MENSAGENS, metadados_proposta
from app.memory.persistencia import (
    registrar_coleta_parcial,
    obter_rascunho_solicitacao,
    atualizar_rascunho_solicitacao,
)
from app.services.ocorrencias import atualizarOcorrencia as servico
from app.services.operacoes import dados_atualizacao, preparar_operacao
from app.tools.ajuda_geral.edicoes import _contexto as _contexto_base, _imagens
from app.schemas.cadastros import CategoriaProblema, Prioridade
from app.tools import salvar_proposta, confirmou_selecao as _confirmou_selecao

def _contexto(runtime):
    """Confere o contexto autenticado exigido pela ferramenta. Usado por atualizar_ocorrencia, buscar_ocorrencias_para_atualizar, processar_atualizacao."""
    contexto, usuario, sessao = _contexto_base(runtime)
    servico.validar_usuario(usuario)
    if contexto.get("intencao_atual") not in {None, "ocorrencia"}:
        raise ValueError(MENSAGENS["prepare_o_tipo_de_registro_solicitado_nesta_mensagem"])
    return contexto, usuario, sessao


async def _salvar(contexto: dict, rascunho: dict, **campos) -> dict:
    """Atualiza a proposta versionada usando o armazenamento do domínio. Usado por atualizar_ocorrencia, buscar_ocorrencias_para_atualizar."""
    return await salvar_proposta(contexto, rascunho, atualizar_rascunho_solicitacao, **campos)


def _resposta(rascunho: dict) -> dict:
    """Projeta rascunho e metadados para a resposta da ferramenta. Usado por atualizar_ocorrencia, processar_atualizacao."""
    return {"status": "AGUARDANDO_CONFIRMACAO", "proposta": metadados_proposta(rascunho)}


def _erro(erro: Exception) -> dict:
    """Traduz falha de validação, permissão ou execução para o contrato do domínio. Usado por atualizar_ocorrencia, buscar_ocorrencias_para_atualizar."""
    if isinstance(erro, (ValueError, PermissionError)):
        return {"status": "ACESSO_NEGADO" if isinstance(erro, PermissionError) else "ERRO_VALIDACAO", "mensagem": str(erro)}
    logging.getLogger(__name__).exception("Falha no fluxo de atualização de ocorrência")
    return {"status": "ERRO_FERRAMENTA", "mensagem": MENSAGENS["nao_foi_possivel_processar_a_alteracao"]}


@tool
async def buscar_ocorrencias_para_atualizar(descricao: str, runtime: ToolRuntime) -> dict:
    """Busca no Qdrant ocorrências próprias e ativas pelo significado da descrição."""
    try:
        contexto, usuario, sessao = _contexto(runtime)
        rascunho = await registrar_coleta_parcial(
            sessao, usuario.usuario_id, tipo="ocorrencia", turno_id=contexto["turno_id"],
            relato=contexto["mensagem_atual"], operacao="atualizar",
        )
        candidatos = await servico.buscar_proprias_ativas(usuario, descricao)
        imagens = list(dict.fromkeys([*rascunho.get("imagens", []), *_imagens(contexto)]))
        rascunho = await _salvar(contexto, rascunho, candidatos=[r["id"] for r in candidatos],
                                 imagens=imagens, acao_fotos=None if imagens else "manter",
                                 etapa="busca", status_fluxo="coletando_dados", registro_id=None,
                                 original=None, dados={}, rotulos={}, selecao_confirmada=False)
        return {"status": "SUCESSO" if candidatos else "SEM_RESULTADO", "ocorrencias": candidatos,
                "mensagem": MENSAGENS["ocorrencia_atualizacao_selecionar" if candidatos else "ocorrencia_atualizacao_sem_resultados"]}
    except Exception as erro:
        return _erro(erro)


@tool
async def atualizar_ocorrencia(
    runtime: ToolRuntime, ocorrencia_id: int | None = None,
    titulo: str | None = None, descricao_ocorrencia: str | None = None,
    descricao_local: str | None = None, local_unidade_id: int | None = None,
    categoria_equipamento_id: int | None = None,
    categoria_problema: CategoriaProblema | None = None, prioridade: Prioridade | None = None,
    acao_fotos: Literal["adicionar", "substituir"] | None = None,
) -> dict:
    """Seleciona uma ocorrência encontrada, coleta várias alterações e prepara atualização após dois aceites.

    O primeiro aceite confirma a seleção do registro; o segundo confirma a proposta final.
    Fotos vêm do contexto. Sem novas alterações, chame novamente após o aceite do usuário.
    """
    # Lógica: executa esta etapa e preserva o tratamento de falhas do domínio.
    try:
        contexto, usuario, sessao = _contexto(runtime)
        rascunho = await obter_rascunho_solicitacao(sessao, usuario.usuario_id, tipo="ocorrencia")
        if not rascunho or rascunho.get("operacao") != "atualizar":
            raise ValueError(MENSAGENS["ocorrencia_atualizacao_buscar_primeiro"])
        if rascunho.get("status_fluxo") in {"enviando", "resultado_indeterminado", "cadastrada"}:
            return {"status": "JA_CONCLUIDA" if rascunho["status_fluxo"] == "cadastrada" else "RESULTADO_INDETERMINADO",
                    "mensagem": MENSAGENS["a_proposta_anterior_ja_foi_executada"] if rascunho["status_fluxo"] == "cadastrada"
                    else MENSAGENS["confira_a_ultima_alteracao_no_banco_antes_de_criar_outra_proposta"]}
        if rascunho.get("pausado"):
            raise ValueError(MENSAGENS["retome_explicitamente_a_proposta_pausada_antes_de_confirmar"])
        novos = servico.validar_alteracoes({chave: valor for chave, valor in {
            "titulo": titulo, "descricao_ocorrencia": descricao_ocorrencia, "descricao_local": descricao_local,
            "local_unidade_id": local_unidade_id, "categoria_equipamento_id": categoria_equipamento_id,
            "categoria_problema": categoria_problema, "prioridade": prioridade,
        }.items() if valor is not None})
        imagens = list(dict.fromkeys([*rascunho.get("imagens", []), *_imagens(contexto)]))
        alteracoes = {**rascunho.get("alteracoes", {}), **novos}
        if acao_fotos and acao_fotos != rascunho.get("acao_fotos"):
            mensagem = normalizar_mensagem(contexto["mensagem_atual"])
            padrao = (r"(?<!nao )\b(?:adicionar|adicione|adiciona|acrescentar|acrescente|juntar)\b"
                      if acao_fotos == "adicionar" else
                      r"(?<!nao )\b(?:substituir|substitua|substitui|trocar todas|troque todas)\b")
            if ("?" in contexto["mensagem_atual"] or re.search(r"\b(?:nao|nunca|jamais|talvez|se)\b", mensagem)
                    or not re.search(padrao, mensagem)):
                acao_fotos = None
        if ocorrencia_id is not None and ocorrencia_id != rascunho.get("registro_id"):
            if ocorrencia_id not in rascunho.get("candidatos", []):
                raise ValueError(MENSAGENS["ocorrencia_atualizacao_buscar_primeiro"])
            registro = await servico.consultar_propria_ativa(usuario, ocorrencia_id)
            if registro is None:
                raise ValueError(MENSAGENS["registro_nao_encontrado_indisponivel_ou_sem_autorizacao"])
            rascunho = await _salvar(
                contexto, rascunho, registro_id=ocorrencia_id, original=servico.snapshot(registro),
                dados={campo: registro[campo] for campo in servico.CAMPOS},
                rotulos={"local_unidade_id": registro["local"], "categoria_equipamento_id": registro["categoria_equipamento"]},
                etapa="selecao", selecao_confirmada=False, alteracoes=alteracoes,
                imagens=imagens, acao_fotos=acao_fotos or (None if imagens else "manter"),
                status_fluxo="aguardando_confirmacao",
            )
            return _resposta(rascunho)
        if not rascunho.get("registro_id"):
            raise ValueError(MENSAGENS["ocorrencia_atualizacao_selecionar"])
        if rascunho.get("etapa") == "selecao":
            if (not _confirmou_selecao(contexto["mensagem_atual"])
                    or not rascunho.get("turno_selecao_apresentada")
                    or rascunho.get("turno_selecao_apresentada") == contexto["turno_id"]
                    or rascunho.get("versao_selecao_apresentada") != rascunho["versao"]):
                if (alteracoes != rascunho.get("alteracoes", {}) or imagens != rascunho.get("imagens", [])
                        or acao_fotos and acao_fotos != rascunho.get("acao_fotos")):
                    rascunho = await _salvar(contexto, rascunho, alteracoes=alteracoes, imagens=imagens,
                                             acao_fotos=acao_fotos or rascunho.get("acao_fotos"))
                return _resposta(rascunho)
            rascunho = await _salvar(contexto, rascunho, selecao_confirmada=True,
                                     etapa="alteracoes", status_fluxo="coletando_dados")
        acao = acao_fotos or rascunho.get("acao_fotos") or (None if imagens else "manter")
        if imagens and acao == "manter":
            acao = None
        rotulos = dict(rascunho.get("rotulos", {}))
        for campo in ("local_unidade_id", "categoria_equipamento_id"):
            if campo in alteracoes:
                opcao = await servico.localizar_opcao(usuario, campo, alteracoes[campo])
                if opcao is None:
                    raise ValueError(MENSAGENS["a_nova_categoria_ou_local_nao_esta_ativo_na_unidade_do_usuario"])
                rotulos[campo] = opcao["nome"]
        dados = {**{campo: rascunho["original"][campo] for campo in servico.CAMPOS}, **alteracoes}
        rotulos.update(servico.rotulos_enums(dados))
        mudanca = (dados != rascunho.get("dados") or imagens != rascunho.get("imagens", [])
                   or acao != rascunho.get("acao_fotos") or alteracoes != rascunho.get("alteracoes", {}))
        if mudanca or rascunho.get("etapa") != "final":
            rascunho = await _salvar(
                contexto, rascunho, dados=dados, rotulos=rotulos, alteracoes=alteracoes,
                imagens=imagens, acao_fotos=acao, confirmado=False,
                etapa="final" if (alteracoes or imagens) and acao else "alteracoes",
                status_fluxo="aguardando_confirmacao" if (alteracoes or imagens) and acao else "coletando_dados",
            )
            if imagens and acao is None:
                return {"status": "AGUARDANDO_INFORMACAO", "mensagem": MENSAGENS["ocorrencia_atualizacao_escolher_fotos"]}
            if not alteracoes and not imagens:
                return {"status": "AGUARDANDO_INFORMACAO", "mensagem": MENSAGENS["ocorrencia_atualizacao_quais_campos"]}
            return _resposta(rascunho)
        return await processar_atualizacao(runtime)
    except Exception as erro:
        return _erro(erro)


async def processar_atualizacao(runtime, *, operacao_aprovada: dict | None = None) -> dict:
    """Confere proposta final de atualização; prepara operação ou efetiva pelo serviço quando já aprovada. Usado por atualizar_ocorrencia."""
    contexto, usuario, sessao = _contexto(runtime)
    rascunho = await obter_rascunho_solicitacao(sessao, usuario.usuario_id, tipo="ocorrencia")
    if (not rascunho or rascunho.get("operacao") != "atualizar" or not rascunho.get("selecao_confirmada")
            or rascunho.get("etapa") != "final" or rascunho.get("pausado")
            or rascunho.get("status_fluxo") != "aguardando_confirmacao"):
        raise ValueError(MENSAGENS["atualizacao_proposta_mudou"])
    dados = dados_atualizacao(rascunho)
    if (not aceite_explicito(contexto["mensagem_atual"], acoes=("alterar", "atualizar", "salvar", "enviar", "prosseguir", "continuar"))
            or not rascunho.get("turno_apresentacao") or rascunho["turno_apresentacao"] == contexto["turno_id"]
            or rascunho.get("atualizacao_apresentada") != dados):
        return _resposta(rascunho)
    if operacao_aprovada is None:
        return await preparar_operacao(contexto, "atualizacao_ocorrencia", f"{rascunho['id']}:{rascunho['versao']}", dados)
    if dados != operacao_aprovada:
        raise ValueError(MENSAGENS["atualizacao_proposta_mudou"])
    controle = {"rascunho_id": rascunho["id"], "versao": rascunho["versao"], "tipo": "ocorrencia"}
    if not await atualizar_rascunho_solicitacao(sessao, usuario.usuario_id, {"status_fluxo": "enviando"},
                                              status_esperados={"aguardando_confirmacao"}, exigir_ativo=True, **controle):
        return {"status": "RESULTADO_INDETERMINADO", "mensagem": MENSAGENS["confira_a_ultima_alteracao_no_banco_antes_de_criar_outra_proposta"]}
    try:
        registro = await servico.atualizar_propria_ativa(usuario, dados)
        resultado = ({"status": "SUCESSO", "registro": registro} if registro is not None else
                     {"status": "NAO_PERMITIDO", "mensagem": MENSAGENS["ocorrencia_atualizacao_registro_mudou"]})
    except Exception:
        logging.getLogger(__name__).exception("Resultado SQL de atualização não confirmado")
        resultado = {"status": "RESULTADO_INDETERMINADO", "mensagem": MENSAGENS["confira_o_registro_no_banco_antes_de_tentar_novamente"]}
    try:
        await atualizar_rascunho_solicitacao(sessao, usuario.usuario_id, {
            "status_fluxo": {"SUCESSO": "cadastrada", "RESULTADO_INDETERMINADO": "resultado_indeterminado"}.get(resultado["status"], "cancelada"),
            "resultado": resultado,
        }, status_esperados={"enviando"}, **controle)
    except Exception:
        logging.getLogger(__name__).exception("Resultado SQL recebido sem atualizar rascunho")
    return resultado
