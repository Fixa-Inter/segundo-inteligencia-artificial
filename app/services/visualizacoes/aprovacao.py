"""Conferência da captura e vínculo entre julgamento e liberação da visualização."""

import hashlib
import json

from pydantic import TypeAdapter
from app.observability.metricas import BYTES_VISUALIZACAO

from app.schemas import UsuarioContexto
from app.schemas.visualizacao import AprovacaoVisualizacao, ConsultaVisualizacaoCapturada, StatusVisualizacao
from . import FILTROS_POR_FONTE, obter_analise
from .limites import MAXIMO_CONSULTAS_POR_EXECUCAO
from .validacao import validar_argumentos_analise, validar_resultado_consulta


def possui_visualizacao(estado) -> bool:
    return estado.get("intencao") == "visualizacao" or any(estado.get(campo) is not None for campo in (
        "visualizacao_candidata", "visualizacao_status", "visualizacao_execucao_id",
        "visualizacao_aprovacao", "visualizacao_aprovada",
    )) or bool(estado.get("consultas_visualizacao"))


def _json(valor) -> str:
    return json.dumps(valor, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False)


def validar_candidata(estado, contexto) -> ConsultaVisualizacaoCapturada | None:
    """Revalida os registros do servidor e a seleção, sem consultar bancos ou modelos."""
    if not possui_visualizacao(estado):
        return None
    if estado.get("intencao") != "visualizacao":
        raise ValueError("Visualização fora da rota correspondente.")
    status = TypeAdapter(StatusVisualizacao).validate_python(estado.get("visualizacao_status"), strict=True)
    registros = estado.get("consultas_visualizacao", [])
    if type(registros) is not list or len(registros) > MAXIMO_CONSULTAS_POR_EXECUCAO:
        raise ValueError("Quantidade de consultas capturadas inválida.")
    registros = [ConsultaVisualizacaoCapturada.model_validate(
        r.model_dump(warnings="error") if isinstance(r, ConsultaVisualizacaoCapturada) else r,
    ) for r in registros]
    candidata = estado.get("visualizacao_candidata")
    if candidata is not None:
        candidata = ConsultaVisualizacaoCapturada.model_validate(
            candidata.model_dump(warnings="error") if isinstance(candidata, ConsultaVisualizacaoCapturada) else candidata,
        )
    if registros or candidata is not None:
        usuario = contexto.get("usuario") if isinstance(contexto, dict) else None
        if (
            not isinstance(usuario, UsuarioContexto)
            or type(usuario.usuario_id) is not int or usuario.usuario_id <= 0
            or usuario.tipo_acesso.strip().lower() != "gestor"
            or estado.get("perfil") != "gestor"
            or type(estado.get("user_id")) is not int or estado["user_id"] != usuario.usuario_id
        ):
            raise ValueError("Contexto autenticado incompatível com a captura.")
        chamadas, consultas = set(), set()
        for registro in registros:
            if (
                registro.execucao_id != estado.get("visualizacao_execucao_id")
                or registro.usuario_id != usuario.usuario_id
                or registro.sessao_id != contexto.get("session_id")
                or registro.turno_id != contexto.get("turno_id")
                or registro.chamada_id in chamadas
            ):
                raise ValueError("Registro de outra execução ou chamada repetida.")
            chamadas.add(registro.chamada_id)
            analise = obter_analise(registro.consulta.analise_id)
            if registro.ferramenta != f"consultar_visualizacao_{analise.fonte.id}":
                raise ValueError("Ferramenta incompatível com a análise capturada.")
            validar_argumentos_analise(registro.consulta, analise, FILTROS_POR_FONTE[analise.fonte.id])
            validar_resultado_consulta(registro.consulta, analise, registro.unidade_id, registro.resultado)
            meta = registro.resultado.metadados
            if meta is not None:
                if meta.consulta_id in consultas:
                    raise ValueError("Identificador de consulta ambíguo.")
                consultas.add(meta.consulta_id)
    if candidata is None:
        if status in {"SUCESSO", "SUCESSO_PARCIAL"}:
            raise ValueError("Sucesso sem candidata capturada.")
        return None
    if status not in {"SUCESSO", "SUCESSO_PARCIAL"}:
        raise ValueError("Status não admite candidata.")
    correspondentes = [r for r in registros if _json(r.model_dump(mode="json")) == _json(candidata.model_dump(mode="json"))]
    if len(correspondentes) != 1:
        raise ValueError("Candidata não corresponde integralmente a uma consulta capturada.")
    if candidata.resultado.status not in {"SUCESSO", "SUCESSO_PARCIAL"} or candidata.resultado.dados is None:
        raise ValueError("A candidata não possui resultado utilizável.")
    if candidata.resultado.status == "SUCESSO_PARCIAL" and status != "SUCESSO_PARCIAL":
        raise ValueError("O status oculta uma limitação da consulta.")
    return candidata


def contexto_julgamento(estado, candidata, *, etapa="juiz") -> dict:
    """Envia o dado selecionado uma vez, sem identidade do usuário, sessão ou turno."""
    contexto = {
        "status": estado.get("visualizacao_status"),
        "candidata": None if candidata is None else {
            "ferramenta": candidata.ferramenta, "chamada_id": candidata.chamada_id,
            "consulta": candidata.consulta.model_dump(mode="json"),
            "resultado": candidata.resultado.model_dump(mode="json"),
        },
        "consultas": [{
            "ferramenta": r["ferramenta"], "chamada_id": r["chamada_id"],
            "status": r["resultado"]["status"],
            "consulta_id": (r["resultado"].get("metadados") or {}).get("consulta_id"),
            "mensagem": r["resultado"]["mensagem"], "avisos": r["resultado"]["avisos"],
            **({"metadados": r["resultado"].get("metadados")}
               if r["resultado"]["status"] not in {"SUCESSO", "SUCESSO_PARCIAL"} else {}),
        } for r in estado.get("consultas_visualizacao", [])],
    }
    if etapa not in {"juiz", "revisor"}:
        raise ValueError("Etapa de medição inválida.")
    BYTES_VISUALIZACAO.labels(etapa).observe(len(_json(contexto).encode("utf-8")))
    return contexto


def criar_aprovacao(candidata, status, texto) -> dict:
    texto = texto.strip()
    conteudo = {"candidata": candidata.model_dump(mode="json"), "status": status, "texto": texto}
    return AprovacaoVisualizacao(
        texto_avaliado=texto, conteudo_sha256=hashlib.sha256(_json(conteudo).encode("utf-8")).hexdigest(),
    ).model_dump(mode="json")


def liberar_visualizacao(estado, contexto) -> dict | None:
    candidata = validar_candidata(estado, contexto)
    if candidata is None:
        if estado.get("visualizacao_aprovacao") is not None or estado.get("visualizacao_aprovada") is not None:
            raise ValueError("Aprovação sem candidata atual.")
        return None
    if estado.get("veredito") != "aprovado" or estado.get("erro") or estado.get("saida_bloqueada"):
        raise ValueError("Visualização sem aprovação ou saída bloqueada.")
    dados_aprovacao = estado.get("visualizacao_aprovacao")
    if isinstance(dados_aprovacao, AprovacaoVisualizacao):
        dados_aprovacao = dados_aprovacao.model_dump(warnings="error")
    aprovacao = AprovacaoVisualizacao.model_validate(dados_aprovacao)
    texto = (estado.get("resposta_candidata") or estado.get("resposta_especialista", "")).strip()
    if aprovacao.model_dump() != criar_aprovacao(candidata, estado["visualizacao_status"], texto):
        raise ValueError("Texto ou dados alterados após o julgamento.")
    return candidata.resultado.model_dump(mode="json")
