"""Contagens exatas de registros próprios, independentes das listagens limitadas."""

import logging
from datetime import date, datetime, time

from app.core import MENSAGENS
from app.core.clients import executar_consulta
from app.schemas import UsuarioContexto
from app.services.gerais import obter_unidade_id

registrador = logging.getLogger(__name__)
PERFIS = {"solicitante", "tecnico", "gestor", "administrador"}
SITUACOES = {
    "solicitacao": {"PENDENTE": 0, "REPROVADA": 1, "APROVADA": 2, "CONCLUIDA": 3},
    "ordem_servico": {"NAO_INICIADA": 0, "ATRASADA": 1, "PAUSADA": 2,
                      "EM_ANDAMENTO": 3, "CONCLUIDA": 4},
}


async def contar_meus_registros(
    usuario: UsuarioContexto, tipo_registro: str, *, situacao: str | None = None,
    inicio: date | None = None, fim: date | None = None,
) -> dict:
    """Conta somente registros autorizados do usuário; datas usam [início, fim)."""
    try:
        if not isinstance(usuario, UsuarioContexto) or usuario.tipo_acesso not in PERFIS:
            raise PermissionError(MENSAGENS["contexto_de_autenticacao_invalido"])
        tabelas = {"solicitacao": "problema", "ocorrencia": "ocorrencia",
                   "ordem_servico": "ordem_servico", "feedback": "feedback"}
        if tipo_registro not in tabelas:
            raise ValueError("Tipo de registro inválido para contagem pessoal.")
        if tipo_registro in {"ocorrencia", "ordem_servico"} and usuario.tipo_acesso == "solicitante":
            raise PermissionError("Seu perfil não pode consultar esse tipo de registro.")
        if any(valor is not None and type(valor) is not date for valor in (inicio, fim)):
            raise ValueError("Informe datas válidas para o período.")
        if inicio is not None and fim is not None and inicio >= fim:
            raise ValueError("O fim exclusivo deve ser posterior ao início.")
        coluna_status = "r.status" if tipo_registro == "solicitacao" else "r.status_ordem_servico"
        condicoes = ["r.usuario_id = :usuario_id"]
        parametros = {"usuario_id": usuario.usuario_id}
        if situacao is not None:
            if tipo_registro == "ordem_servico" and situacao == "ABERTA":
                condicoes.append("r.status_ordem_servico <> 4")
            elif situacao in SITUACOES.get(tipo_registro, {}):
                condicoes.append(f"{coluna_status} = :situacao")
                parametros["situacao"] = SITUACOES[tipo_registro][situacao]
            else:
                raise ValueError("Situação não disponível para esse tipo de registro.")

        unidade = await obter_unidade_id(usuario)
        parametros["unidade_id"] = unidade
        if tipo_registro == "feedback":
            joins = "JOIN usuario autor ON autor.id = r.usuario_id"
            condicoes.extend(["autor.unidade_id = :unidade_id", "autor.esta_ativo IS TRUE"])
        else:
            joins = ""
            local_fk = "r.local_unidade_id"
            condicoes.append("r.esta_ativo IS TRUE")
            if tipo_registro == "ordem_servico":
                joins = "JOIN problema p ON p.id = r.problema_id "
                local_fk = "p.local_unidade_id"
                condicoes.append("p.esta_ativo IS TRUE")
            joins += f"JOIN local_unidade local ON local.id = {local_fk}"
            condicoes.extend(["local.unidade_id = :unidade_id", "local.esta_ativo IS TRUE"])
        for nome, valor, operador in (("inicio", inicio, ">="), ("fim", fim, "<")):
            if valor is not None:
                condicoes.append(f"r.data_criacao {operador} :{nome}")
                parametros[nome] = datetime.combine(valor, time.min)
        # Tabela e colunas são escolhidas acima em listas fixas; valores são parâmetros.
        linhas = await executar_consulta(
            usuario.tipo_acesso,
            f"SELECT COUNT(*) AS total FROM {tabelas[tipo_registro]} r {joins} "
            + "WHERE " + " AND ".join(condicoes), parametros,
        )
        if len(linhas) != 1 or type(linhas[0].get("total")) is not int or linhas[0]["total"] < 0:
            raise RuntimeError("Contagem incompatível com o resultado esperado.")
        return {
            "status": "SUCESSO", "tipo_registro": tipo_registro, "escopo": "proprio",
            "total": linhas[0]["total"], "situacao": situacao,
            "periodo": {"inicio": inicio.isoformat() if inicio else None,
                        "fim_exclusivo": fim.isoformat() if fim else None},
            "mensagem": "Contagem dos seus registros consultada com sucesso.",
        }
    except (ValueError, PermissionError) as erro:
        return {"status": "ACESSO_NEGADO" if isinstance(erro, PermissionError) else "ERRO_VALIDACAO",
                "mensagem": str(erro)}
    except Exception:
        registrador.exception("Falha na contagem pessoal de registros")
        return {"status": "ERRO_FERRAMENTA", "mensagem": MENSAGENS["nao_foi_possivel_consultar_os_registros_agora"]}
