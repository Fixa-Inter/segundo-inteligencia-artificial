from app.core import data_atual
import logging
from calendar import monthrange
from datetime import date, datetime, timedelta
import unicodedata

from app.core.clients.postgres import executar_consulta
from app.schemas import UsuarioContexto


registrador = logging.getLogger(__name__)

ORDEM_PRIORIDADE = ("ALTA", "MEDIA", "BAIXA")
PRIORIDADE_POR_ID = {0: "ALTA", 1: "MEDIA", 2: "BAIXA"}
STATUS_ORDEM_SERVICO_POR_ID = {
    0: "Não Iniciada",
    1: "Atrasada",
    2: "Pausada",
    3: "Em andamento",
    4: "Concluída",
}

CATEGORIA_PROBLEMA_POR_ID = {
    1: "Elétrica",
    2: "Hidráulica",
    3: "Mecânica",
    4: "Informática",
    5: "Mobiliário",
    6: "Climatização",
    7: "Rede e Conectividade",
    8: "Segurança",
    9: "Iluminação",
    10: "Limpeza e Conservação",
}


def inicio_periodo(hoje: date) -> date:
    """Subtrai tres meses de calendario, ajustando dias inexistentes."""
    indice_mes = hoje.year * 12 + hoje.month - 1 - 3
    ano, mes_zero = divmod(indice_mes, 12)
    mes = mes_zero + 1
    return date(ano, mes, min(hoje.day, monthrange(ano, mes)[1]))


def _data_iso(valor) -> str | None:
    if valor is None:
        return None
    if isinstance(valor, datetime):
        return valor.date().isoformat()
    if isinstance(valor, date):
        return valor.isoformat()
    raise ValueError("Data retornada pelo banco em formato invalido.")


def _normalizar_filtro(valor: str) -> str:
    texto = unicodedata.normalize("NFD", valor.strip().upper())
    return "".join(caractere for caractere in texto if unicodedata.category(caractere) != "Mn")


_ID_POR_CATEGORIA_PROBLEMA = {
    _normalizar_filtro(nome): identificador
    for identificador, nome in CATEGORIA_PROBLEMA_POR_ID.items()
}
_ID_POR_PRIORIDADE = {
    _normalizar_filtro(nome): identificador
    for identificador, nome in PRIORIDADE_POR_ID.items()
}


_ID_POR_STATUS = {_normalizar_filtro(nome): codigo for codigo, nome in STATUS_ORDEM_SERVICO_POR_ID.items()}
_ID_POR_STATUS.update({
    "NAO INICIADAS": 0,
    "FINALIZADAS": 4,
})


def chave_ordenacao_status(status: str) -> tuple[int, str]:
    """Ordena pelos status definidos no enum da ordem de serviço."""
    nome = _normalizar_filtro(status)
    return (_ID_POR_STATUS.get(nome, 5), nome)


async def buscar_ordens_servico(
    usuario: UsuarioContexto,
    *,
    status: str | None = None,
    prioridade: str | None = None,
    categoria_problema: str | None = None,
    categoria_equipamento: str | None = None,
    local: str | None = None,
    termo: str | None = None,
    data_criacao_inicio: date | None = None,
    data_criacao_fim: date | None = None,
    data_prevista_inicio: date | None = None,
    data_prevista_fim: date | None = None,
) -> dict:
    """Busca OS com filtros opcionais dentro do escopo do usuario autenticado."""
    perfil = usuario.tipo_acesso.lower()
    if perfil not in {"tecnico", "gestor"}:
        return {
            "status": "ACESSO_NEGADO",
            "mensagem": "Somente tecnicos e gestores podem consultar ordens de servico.",
        }

    filtros = {
        "status": status,
        "prioridade": prioridade,
        "categoria_problema": categoria_problema,
        "categoria_equipamento": categoria_equipamento,
        "local": local,
        "termo": termo,
        "data_criacao_inicio": data_criacao_inicio,
        "data_criacao_fim": data_criacao_fim,
        "data_prevista_inicio": data_prevista_inicio,
        "data_prevista_fim": data_prevista_fim,
    }
    if not any(valor is not None for valor in filtros.values()):
        return {
            "status": "ERRO_VALIDACAO",
            "mensagem": "Informe ao menos um filtro para buscar as ordens de servico.",
        }
    if (
        data_criacao_inicio and data_criacao_fim
        and data_criacao_inicio > data_criacao_fim
    ) or (
        data_prevista_inicio and data_prevista_fim
        and data_prevista_inicio > data_prevista_fim
    ):
        return {
            "status": "ERRO_VALIDACAO",
            "mensagem": "A data inicial de cada periodo deve ser anterior ou igual a data final.",
        }

    condicoes = [
        "unidade_registro.cnpj = unidade_autenticada.cnpj",
        "os.esta_ativo IS TRUE",
        "problema.esta_ativo IS TRUE",
        "local_registro.esta_ativo IS TRUE",
        "unidade_registro.esta_ativo IS TRUE",
        "usuario_autenticado.esta_ativo IS TRUE",
        "unidade_autenticada.esta_ativo IS TRUE",
    ]
    parametros = {"usuario_id": usuario.usuario_id}
    filtros_legiveis = {}

    if perfil == "tecnico":
        condicoes.append("os.usuario_id = :usuario_id")

    if status is not None:
        status_id = _ID_POR_STATUS.get(_normalizar_filtro(status))
        if status_id is None:
            return {
                "status": "ERRO_VALIDACAO",
                "mensagem": "Use Não Iniciada/Não iniciadas, Atrasada, Pausada, Em andamento ou Concluída/Finalizadas.",
            }
        condicoes.append("os.status_ordem_servico = :status_id")
        parametros["status_id"] = status_id
        filtros_legiveis["status"] = STATUS_ORDEM_SERVICO_POR_ID[status_id]

    if prioridade is not None:
        prioridade_normalizada = _normalizar_filtro(prioridade)
        if prioridade_normalizada not in _ID_POR_PRIORIDADE:
            return {
                "status": "ERRO_VALIDACAO",
                "mensagem": "Prioridade invalida. Use ALTA, MEDIA ou BAIXA.",
            }
        condicoes.append("os.prioridade = :prioridade")
        parametros["prioridade"] = _ID_POR_PRIORIDADE[prioridade_normalizada]
        filtros_legiveis["prioridade"] = PRIORIDADE_POR_ID[parametros["prioridade"]]

    if categoria_problema is not None:
        categoria_normalizada = _normalizar_filtro(categoria_problema)
        if categoria_normalizada not in _ID_POR_CATEGORIA_PROBLEMA:
            return {
                "status": "ERRO_VALIDACAO",
                "mensagem": "Categoria do problema invalida. Informe uma categoria cadastrada.",
            }
        condicoes.append("os.categoria_problema = :categoria_problema")
        parametros["categoria_problema"] = _ID_POR_CATEGORIA_PROBLEMA[categoria_normalizada]
        filtros_legiveis["categoria_problema"] = CATEGORIA_PROBLEMA_POR_ID[
            parametros["categoria_problema"]
        ]

    if categoria_equipamento is not None:
        condicoes.append("categoria_eq.nome ILIKE :categoria_equipamento")
        parametros["categoria_equipamento"] = f"%{categoria_equipamento.strip()}%"
        filtros_legiveis["categoria_equipamento"] = categoria_equipamento.strip()

    if local is not None:
        condicoes.append("local_registro.nome ILIKE :local")
        parametros["local"] = f"%{local.strip()}%"
        filtros_legiveis["local"] = local.strip()

    if termo is not None:
        condicoes.append(
            "(problema.titulo ILIKE :termo OR problema.descricao_problema ILIKE :termo)"
        )
        parametros["termo"] = f"%{termo.strip()}%"
        filtros_legiveis["termo"] = termo.strip()

    usa_periodo_explicito = any((
        data_criacao_inicio,
        data_criacao_fim,
        data_prevista_inicio,
        data_prevista_fim,
    ))
    inicio_padrao = fim_padrao = None
    if not usa_periodo_explicito:
        hoje = data_atual()
        inicio_padrao = inicio_periodo(hoje)
        fim_padrao = hoje
        data_criacao_inicio = inicio_padrao
        data_criacao_fim = fim_padrao
        filtros_legiveis["periodo_criacao"] = {
            "inicio": inicio_padrao.isoformat(),
            "fim": fim_padrao.isoformat(),
        }

    if data_criacao_inicio is not None:
        condicoes.append("os.data_criacao >= :data_criacao_inicio")
        parametros["data_criacao_inicio"] = data_criacao_inicio
        if usa_periodo_explicito:
            filtros_legiveis["data_criacao_inicio"] = data_criacao_inicio.isoformat()
    if data_criacao_fim is not None:
        condicoes.append("os.data_criacao < :data_criacao_fim_exclusivo")
        parametros["data_criacao_fim_exclusivo"] = data_criacao_fim + timedelta(days=1)
        if usa_periodo_explicito:
            filtros_legiveis["data_criacao_fim"] = data_criacao_fim.isoformat()
    if data_prevista_inicio is not None:
        condicoes.append("os.data_prevista >= :data_prevista_inicio")
        parametros["data_prevista_inicio"] = data_prevista_inicio
        filtros_legiveis["data_prevista_inicio"] = data_prevista_inicio.isoformat()
    if data_prevista_fim is not None:
        condicoes.append("os.data_prevista < :data_prevista_fim_exclusivo")
        parametros["data_prevista_fim_exclusivo"] = data_prevista_fim + timedelta(days=1)
        filtros_legiveis["data_prevista_fim"] = data_prevista_fim.isoformat()

    sql = f"""
        SELECT
            problema.titulo,
            problema.descricao_problema AS "descricaoProblema",
            local_registro.nome AS local,
            problema.descricao_local AS "descricaoLocal",
            os.status_ordem_servico AS "statusOrdemServico",
            os.categoria_problema AS categoria_id,
            categoria_eq.nome AS "categoriaEquipamento",
            os.data_prevista::date AS "dataPrevista",
            os.prioridade AS prioridade_id,
            os.data_criacao::date AS "dataCriacao"
        FROM ordem_servico AS os
        JOIN problema ON problema.id = os.problema_id
        JOIN categoria_equipamento AS categoria_eq
            ON categoria_eq.id = problema.categoria_equipamento_id
        JOIN local_unidade AS local_registro
            ON local_registro.id = problema.local_unidade_id
        JOIN unidade AS unidade_registro
            ON unidade_registro.id = local_registro.unidade_id
        JOIN usuario AS usuario_autenticado
            ON usuario_autenticado.id = :usuario_id
        JOIN unidade AS unidade_autenticada
            ON unidade_autenticada.id = usuario_autenticado.unidade_id
        WHERE {' AND '.join(condicoes)}
        ORDER BY os.data_criacao DESC
    """

    try:
        linhas = await executar_consulta(perfil, sql, parametros)
        ordens = []
        for linha in linhas:
            prioridade_formatada = PRIORIDADE_POR_ID.get(linha["prioridade_id"])
            categoria = CATEGORIA_PROBLEMA_POR_ID.get(linha["categoria_id"])
            status_formatado = STATUS_ORDEM_SERVICO_POR_ID.get(linha["statusOrdemServico"])
            if (
                prioridade_formatada is None
                or categoria is None
                or not status_formatado
            ):
                raise ValueError("Status, categoria ou prioridade de OS desconhecido.")
            ordens.append({
                "titulo": linha["titulo"],
                "descricaoProblema": linha["descricaoProblema"],
                "local": linha["local"],
                "descricaoLocal": linha["descricaoLocal"],
                "statusOrdemServico": status_formatado,
                "categoriaProblema": categoria,
                "categoriaEquipamento": linha["categoriaEquipamento"],
                "dataPrevista": _data_iso(linha["dataPrevista"]),
                "prioridade": prioridade_formatada,
                "dataCriacao": _data_iso(linha["dataCriacao"]),
            })
        ordens.sort(key=lambda ordem: (
            chave_ordenacao_status(ordem["statusOrdemServico"]),
            ORDEM_PRIORIDADE.index(ordem["prioridade"]),
        ))
    except Exception:
        registrador.exception("Falha ao buscar ordens de servico com filtros no PostgreSQL")
        return {
            "status": "ERRO_FERRAMENTA",
            "mensagem": "Nao foi possivel consultar as ordens de servico no banco.",
        }

    return {
        "status": "SUCESSO" if ordens else "SEM_RESULTADO",
        "ordens_servico": ordens,
        "filtros_aplicados": filtros_legiveis,
        "mensagem": (
            "Ordens de servico consultadas com sucesso."
            if ordens
            else "Nenhuma ordem de servico encontrada com esses filtros no escopo autorizado."
        ),
    }


async def consultar_minhas_ordens_servico(usuario: UsuarioContexto) -> dict:
    """Consulta OS atribuidas ao tecnico autenticado nos ultimos tres meses."""
    return await _consultar_ordens_servico(usuario, somente_usuario=True)


async def consultar_todas_ordens_servico(usuario: UsuarioContexto) -> dict:
    """Consulta OS do endereco do gestor nos ultimos tres meses."""
    if usuario.tipo_acesso != "gestor":
        return {"status": "ACESSO_NEGADO", "mensagem": "Consulta exclusiva para gestores."}
    return await _consultar_ordens_servico(usuario, somente_usuario=False)


async def _consultar_ordens_servico(
    usuario: UsuarioContexto,
    *,
    somente_usuario: bool,
) -> dict:
    hoje = data_atual()
    inicio = inicio_periodo(hoje)
    filtro_usuario = " AND os.usuario_id = :usuario_id" if somente_usuario else ""
    sql = f"""
        SELECT
            problema.titulo,
            problema.descricao_problema AS "descricaoProblema",
            local_registro.nome AS local,
            problema.descricao_local AS "descricaoLocal",
            os.status_ordem_servico AS "statusOrdemServico",
            os.categoria_problema AS categoria_id,
            os.data_prevista::date AS "dataPrevista",
            os.prioridade AS prioridade_id,
            os.data_criacao::date AS "dataCriacao"
        FROM ordem_servico AS os
        JOIN problema ON problema.id = os.problema_id
        JOIN local_unidade AS local_registro
            ON local_registro.id = problema.local_unidade_id
        JOIN unidade AS unidade_registro
            ON unidade_registro.id = local_registro.unidade_id
        JOIN usuario AS usuario_autenticado
            ON usuario_autenticado.id = :usuario_id
        JOIN unidade AS unidade_autenticada
            ON unidade_autenticada.id = usuario_autenticado.unidade_id
        WHERE unidade_registro.cnpj = unidade_autenticada.cnpj
          AND os.esta_ativo IS TRUE
          AND problema.esta_ativo IS TRUE
          AND local_registro.esta_ativo IS TRUE
          AND unidade_registro.esta_ativo IS TRUE
          AND usuario_autenticado.esta_ativo IS TRUE
          AND unidade_autenticada.esta_ativo IS TRUE
          AND os.data_criacao >= :inicio
          AND os.data_criacao < :fim_exclusivo
          {filtro_usuario}
        ORDER BY os.data_criacao DESC
    """
    parametros = {
        "usuario_id": usuario.usuario_id,
        "inicio": inicio,
        "fim_exclusivo": hoje + timedelta(days=1),
    }

    try:
        linhas = await executar_consulta(usuario.tipo_acesso, sql, parametros)
        ordens = []
        for linha in linhas:
            prioridade = PRIORIDADE_POR_ID.get(linha["prioridade_id"])
            categoria = CATEGORIA_PROBLEMA_POR_ID.get(linha["categoria_id"])
            status = STATUS_ORDEM_SERVICO_POR_ID.get(linha["statusOrdemServico"])
            if prioridade is None or categoria is None or not status:
                raise ValueError("Status, categoria ou prioridade de OS desconhecido.")
            ordens.append({
                "titulo": linha["titulo"],
                "descricaoProblema": linha["descricaoProblema"],
                "local": linha["local"],
                "descricaoLocal": linha["descricaoLocal"],
                "statusOrdemServico": status,
                "categoriaProblema": categoria,
                "dataPrevista": _data_iso(linha["dataPrevista"]),
                "prioridade": prioridade,
                "dataCriacao": _data_iso(linha["dataCriacao"]),
            })
        ordens.sort(key=lambda ordem: (
            chave_ordenacao_status(ordem["statusOrdemServico"]),
            ORDEM_PRIORIDADE.index(ordem["prioridade"]),
        ))
    except Exception:
        registrador.exception("Falha ao consultar ordens de servico no PostgreSQL")
        return {
            "status": "ERRO_FERRAMENTA",
            "mensagem": "Nao foi possivel consultar as ordens de servico no banco.",
        }

    return {
        "status": "SUCESSO" if ordens else "SEM_RESULTADO",
        "ordens_servico": ordens,
        "periodo": {
            "inicio": inicio.strftime("%d-%m-%Y"),
            "fim": hoje.strftime("%d-%m-%Y"),
        },
        "mensagem": (
            "Ordens de servico consultadas com sucesso."
            if ordens
            else "Nenhuma ordem de servico encontrada nos ultimos tres meses."
        ),
    }
