"""Execução e tratamento comuns dos KPIs; SQL/população ficam em cada domínio."""

from datetime import date
from app.core import MENSAGENS
from .databricks import ConfiguracaoDatabricksAusente, ErroDatabricks, TimeoutConsultaDatabricks

def validar_periodo_indicadores(inicio: date, fim: date) -> dict | None:
    """Valida datas estritas e intervalo [início, fim) usado pelos três domínios."""
    if type(inicio) is not date or type(fim) is not date:
        return {"status": "ERRO_VALIDACAO", "mensagem": MENSAGENS['informe_inicio_e_fim_do_periodo_como_datas_validas']}
    if inicio >= fim:
        return {"status": "ERRO_VALIDACAO", "mensagem": MENSAGENS['o_inicio_deve_ser_anterior_ao_fim_exclusivo_do_periodo']}
    return None


async def consultar_linhas_indicador(sql, parametros, *, executor, registrador, tipos_parametros=None):
    """Converte falhas/ausência de linhas em status, preservando o executor injetado.

    Os serviços informam seus parâmetros/tipos: snapshots de OS e períodos dos
    demais KPIs mantêm contratos distintos. Nenhum SQL é gerado por este método.
    """
    try:
        linhas = await executor(sql, parametros, tipos_parametros=tipos_parametros)
    except TimeoutConsultaDatabricks:
        return {"status": "TIMEOUT", "mensagem": MENSAGENS['a_consulta_de_indicadores_excedeu_o_tempo_limite']}
    except ConfiguracaoDatabricksAusente as erro:
        registrador.error("Configuração Databricks ausente: %s", erro)
        return {"status": "ERRO_FERRAMENTA", "mensagem": MENSAGENS['a_consulta_de_indicadores_nao_esta_configurada']}
    except ErroDatabricks:
        registrador.exception("Falha ao consultar indicador no Databricks")
        return {"status": "ERRO_FERRAMENTA", "mensagem": MENSAGENS['nao_foi_possivel_consultar_o_indicador_no_databricks']}
    except Exception:
        registrador.exception("Falha inesperada ao consultar indicador no Databricks")
        return {"status": "ERRO_FERRAMENTA", "mensagem": MENSAGENS['nao_foi_possivel_consultar_o_indicador_no_databricks']}
    if not linhas:
        return {"status": "SEM_RESULTADO", "mensagem": MENSAGENS['a_consulta_nao_retornou_resultados']}
    return linhas
