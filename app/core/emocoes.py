from enum import Enum

# Emocao: contrato/estrutura de emocoes; usado pelos consumidores desta interface.
class Emocao(str, Enum):
    NEUTRO = "NEUTRO"
    CURIOSO = "CURIOSO"
    PENSATIVO = "PENSATIVO"
    CONFIRMACAO = "CONFIRMACAO"
    SUCESSO = "SUCESSO"
    EMPATICO = "EMPATICO"
    ALERTA = "ALERTA"
    ERRO = "ERRO"
    BLOQUEADO = "BLOQUEADO"
    CONSELHEIRO = "CONSELHEIRO"
    AGUARDANDO = "AGUARDANDO"
    CELEBRACAO = "CELEBRACAO"
