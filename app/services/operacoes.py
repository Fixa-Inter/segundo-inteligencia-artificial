"""Prepara gravações e vincula a aprovação aos dados exatos da operação."""

import hashlib
import json
from datetime import datetime, timezone

from app.schemas import UsuarioContexto

TIPOS = {"solicitacao", "ocorrencia", "feedback", "edicao"}


def calcular_hash(dados: dict) -> str:
    texto = json.dumps(dados, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False)
    return hashlib.sha256(texto.encode("utf-8")).hexdigest()


def resumo(documento: dict) -> dict:
    return {"id": documento["_id"], "tipo": documento["tipo"], "dados": documento["dados"]}


async def preparar_operacao(contexto: dict, tipo: str, referencia: str, dados: dict) -> dict:
    from app.memory.persistencia import operacoes as persistencia

    usuario = contexto.get("usuario")
    if not isinstance(usuario, UsuarioContexto) or not contexto.get("session_id") or not contexto.get("turno_id"):
        raise ValueError("Usuário, sessão e turno são obrigatórios para preparar uma operação.")
    if tipo not in TIPOS:
        raise ValueError("Tipo de operação não permitido.")
    identidade = {"usuario": usuario.usuario_id, "sessao": contexto["session_id"],
                  "tipo": tipo, "referencia": referencia}
    documento = {
        "_id": calcular_hash(identidade), "usuario_id": usuario.usuario_id,
        "sessao_id": contexto["session_id"], "turno_id": contexto["turno_id"],
        "tipo": tipo, "dados": dados, "estado": "preparada",
        "conteudo_hash": calcular_hash({"tipo": tipo, "dados": dados}),
        "criada_em": datetime.now(timezone.utc),
    }
    salvo = await persistencia.preparar(documento)
    operacao = resumo(salvo)
    pendentes = contexto.setdefault("operacoes_pendentes", [])
    if operacao not in pendentes:
        if any(item["id"] == operacao["id"] for item in pendentes):
            raise ValueError("A mesma operação foi preparada com dados diferentes.")
        pendentes.append(operacao)
    return {"status": "OPERACAO_PREPARADA", "operacao": operacao,
            "mensagem": "Operação preparada para validação interna. Ainda não houve gravação definitiva. Não peça uma nova confirmação ao usuário."}


def aprovacao_operacoes(operacoes: list[dict], contexto: dict) -> dict:
    return {"usuario_id": contexto["usuario"].usuario_id, "sessao_id": contexto["session_id"],
            "turno_id": contexto["turno_id"], "conteudo_hash": calcular_hash({"operacoes": operacoes})}


def dados_cadastro(rascunho: dict) -> dict:
    """Inclui os anexos na aprovação, além dos campos e da versão do rascunho."""
    return {"proposta_id": rascunho["id"], "versao": rascunho["versao"],
            "dados": rascunho["dados"], "imagens": rascunho.get("imagens", [])}


def dados_edicao(acao: dict) -> dict:
    return {campo: acao.get(campo) for campo in ("id", "tipo", "registro_id", "campo", "novo_valor", "imagens")}
