"""Seis tools vinculadas aos serviços de domínio de visualização."""

from app.services.visualizacoes import (
    ocorrencia,
    os_atual,
    os_conclusao,
    os_criacao,
    recorrencia,
    solicitacao,
)
from .execucao import criar_tool

# consultar_visualizacao_os_criacao: Recurso compartilhado de consultar visualizacao os criacao usado pelas funções deste módulo e pela interface pública.
consultar_visualizacao_os_criacao = criar_tool(os_criacao)
# consultar_visualizacao_os_conclusao: Recurso compartilhado de consultar visualizacao os conclusao usado pelas funções deste módulo e pela interface pública.
consultar_visualizacao_os_conclusao = criar_tool(os_conclusao)
# consultar_visualizacao_os_atual: Recurso compartilhado de consultar visualizacao os atual usado pelas funções deste módulo e pela interface pública.
consultar_visualizacao_os_atual = criar_tool(os_atual)
# consultar_visualizacao_solicitacao: Recurso compartilhado de consultar visualizacao solicitacao usado pelas funções deste módulo e pela interface pública.
consultar_visualizacao_solicitacao = criar_tool(solicitacao)
# consultar_visualizacao_recorrencia: Recurso compartilhado de consultar visualizacao recorrencia usado pelas funções deste módulo e pela interface pública.
consultar_visualizacao_recorrencia = criar_tool(recorrencia)
# consultar_visualizacao_ocorrencia: Recurso compartilhado de consultar visualizacao ocorrencia usado pelas funções deste módulo e pela interface pública.
consultar_visualizacao_ocorrencia = criar_tool(ocorrencia)
