import logging

from app.core.clients.postgres import executar_consulta
from app.schemas import UsuarioContexto

from app.core.respostas import MENSAGENS


registrador = logging.getLogger(__name__)

_SQL_TECNICOS_DISPONIVEIS = """
    WITH usuario_autenticado AS (
        SELECT unidade.cnpj
        FROM usuario AS autenticado
        JOIN unidade ON unidade.id = autenticado.unidade_id
        WHERE autenticado.id = :usuario_id
          AND autenticado.tipo_acesso = 2
          AND autenticado.esta_ativo IS TRUE
          AND unidade.esta_ativo IS TRUE
    ), tecnicos AS (
        SELECT tecnico.id, tecnico.nome_completo, unidade_tecnico.cnpj
        FROM usuario AS tecnico
        JOIN unidade AS unidade_tecnico
            ON unidade_tecnico.id = tecnico.unidade_id
        JOIN usuario_autenticado
            ON usuario_autenticado.cnpj = unidade_tecnico.cnpj
        WHERE tecnico.tipo_acesso = 3
          AND tecnico.esta_ativo IS TRUE
          AND unidade_tecnico.esta_ativo IS TRUE
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
                WHERE os.status_ordem_servico <> 4
            )::integer AS ordens_nao_concluidas
        FROM ordem_servico AS os
        JOIN problema ON problema.id = os.problema_id
        JOIN local_unidade AS local_registro
            ON local_registro.id = problema.local_unidade_id
        JOIN unidade AS unidade_registro
            ON unidade_registro.id = local_registro.unidade_id
        WHERE os.usuario_id = tecnico.id
          AND os.esta_ativo IS TRUE
          AND problema.esta_ativo IS TRUE
          AND local_registro.esta_ativo IS TRUE
          AND unidade_registro.esta_ativo IS TRUE
          AND unidade_registro.cnpj = tecnico.cnpj
    ) AS carga ON TRUE
    ORDER BY ordens_nao_concluidas, tecnico.nome_completo
"""


async def buscar_tecnicos_disponiveis(usuario: UsuarioContexto) -> dict:
    """Seleciona tecnicos livres ou, se nao houver, os de menor carga aberta."""
    if usuario.tipo_acesso.lower() not in {"gestor", "administrador"}:
        return {
            "status": "ACESSO_NEGADO",
            "mensagem": MENSAGENS['somente_gestores_e_administradores_podem_consultar_tecnicos_disponiveis'],
        }

    try:
        tecnicos = await executar_consulta(
            usuario.tipo_acesso,
            _SQL_TECNICOS_DISPONIVEIS,
            {"usuario_id": usuario.usuario_id},
        )
    except Exception:
        registrador.exception("Falha ao buscar tecnicos disponiveis no PostgreSQL")
        return {
            "status": "ERRO_FERRAMENTA",
            "mensagem": MENSAGENS['nao_foi_possivel_consultar_os_tecnicos_disponiveis'],
        }

    if not tecnicos:
        return {
            "status": "SEM_RESULTADO",
            "tecnicos": [],
            "mensagem": MENSAGENS['nenhum_tecnico_ativo_foi_encontrado_neste_endereco'],
        }

    sem_ordens_abertas = [
        tecnico for tecnico in tecnicos
        if tecnico["ordens_nao_concluidas"] == 0
    ]
    if sem_ordens_abertas:
        selecionados = sem_ordens_abertas
        criterio = "Tecnicos sem ordens em status diferentes de Concluída."
    else:
        menor_carga = min(tecnico["ordens_nao_concluidas"] for tecnico in tecnicos)
        selecionados = [
            tecnico for tecnico in tecnicos
            if tecnico["ordens_nao_concluidas"] == menor_carga
        ]
        criterio = (
            "Nenhum tecnico esta com todas as ordens concluidas; exibidos os "
            f"tecnicos com menor quantidade de ordens nao concluidas ({menor_carga})."
        )

    return {
        "status": "SUCESSO",
        "tecnicos": selecionados,
        "criterio": criterio,
        "mensagem": MENSAGENS['tecnicos_disponiveis_consultados_com_sucesso'],
    }
