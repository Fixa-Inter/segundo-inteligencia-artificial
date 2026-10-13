import logging

from app.core.clients.postgres import executar_select
from app.schemas.UsuarioContexto import UsuarioContexto


logger = logging.getLogger(__name__)

_SQL_TECNICOS_DISPONIVEIS = """
    WITH usuario_autenticado AS (
        SELECT endereco.cnpj
        FROM usuario AS autenticado
        JOIN endereco ON endereco.id = autenticado.endereco_id
        WHERE autenticado.id = :usuario_id
          AND autenticado.tipo_acesso = 2
          AND autenticado.esta_ativo IS TRUE
    ), tecnicos AS (
        SELECT tecnico.id, tecnico.nome_completo, endereco_tecnico.cnpj
        FROM usuario AS tecnico
        JOIN endereco AS endereco_tecnico
            ON endereco_tecnico.id = tecnico.endereco_id
        JOIN usuario_autenticado
            ON usuario_autenticado.cnpj = endereco_tecnico.cnpj
        WHERE tecnico.tipo_acesso = 3
          AND tecnico.esta_ativo IS TRUE
    )
    SELECT
        tecnico.id,
        tecnico.nome_completo,
        COALESCE(carga.total_ordens, 0)::integer AS total_ordens,
        COALESCE(carga.ordens_nao_concluidas, 0)::integer AS ordens_nao_concluidas
    FROM tecnicos AS tecnico
    LEFT JOIN LATERAL (
        SELECT
            COUNT(os.id)::integer AS total_ordens,
            COUNT(os.id) FILTER (
                WHERE os.status_ordem_servico_id <> 4
            )::integer AS ordens_nao_concluidas
        FROM ordem_servico AS os
        JOIN status_ordem_servico AS status_os
            ON status_os.id = os.status_ordem_servico_id
        JOIN problema ON problema.id = os.problema_id
        JOIN local_endereco AS local_registro
            ON local_registro.id = problema.local_endereco_id
        JOIN endereco AS endereco_registro
            ON endereco_registro.id = local_registro.endereco_id
        WHERE os.usuario_id = tecnico.id
          AND endereco_registro.cnpj = tecnico.cnpj
    ) AS carga ON TRUE
    ORDER BY ordens_nao_concluidas, tecnico.nome_completo
"""


async def buscar_tecnicos_disponiveis(usuario: UsuarioContexto) -> dict:
    """Seleciona tecnicos livres ou, se nao houver, os de menor carga aberta."""
    if usuario.tipo_acesso.lower() != "gestor":
        return {
            "status": "ACESSO_NEGADO",
            "mensagem": "Somente gestores podem consultar tecnicos disponiveis.",
        }

    try:
        tecnicos = await executar_select(
            "gestor",
            _SQL_TECNICOS_DISPONIVEIS,
            {"usuario_id": usuario.usuario_id},
        )
    except Exception:
        logger.exception("Falha ao buscar tecnicos disponiveis no PostgreSQL")
        return {
            "status": "ERRO_FERRAMENTA",
            "mensagem": "Nao foi possivel consultar os tecnicos disponiveis.",
        }

    if not tecnicos:
        return {
            "status": "SEM_RESULTADO",
            "tecnicos": [],
            "mensagem": "Nenhum tecnico ativo foi encontrado neste endereco.",
        }

    sem_ordens_abertas = [
        tecnico for tecnico in tecnicos
        if tecnico["ordens_nao_concluidas"] == 0
    ]
    if sem_ordens_abertas:
        selecionados = sem_ordens_abertas
        criterio = "Tecnicos sem ordens em status diferentes de Finalizadas."
    else:
        menor_carga = min(tecnico["ordens_nao_concluidas"] for tecnico in tecnicos)
        selecionados = [
            tecnico for tecnico in tecnicos
            if tecnico["ordens_nao_concluidas"] == menor_carga
        ]
        criterio = (
            "Nenhum tecnico esta com todas as ordens finalizadas; exibidos os "
            f"tecnicos com menor quantidade de ordens em outros status ({menor_carga})."
        )

    return {
        "status": "SUCESSO",
        "tecnicos": selecionados,
        "criterio": criterio,
        "mensagem": "Tecnicos disponiveis consultados com sucesso.",
    }
