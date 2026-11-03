# CLASSIFICADOR_PROMPT_COMPLETO: Instrução textual enviada ao modelo; conteúdo preservado para manter comportamento do agente.
CLASSIFICADOR_PROMPT_COMPLETO = """Classifique o problema relatado em uma única categoria, escolhendo a mais específica. Responda somente com o nome do enum, sem explicações:
ELETRICA, HIDRAULICA, MECANICA, INFORMATICA, MOBILIARIO, CLIMATIZACAO, REDE_CONECTIVIDADE, SEGURANCA, ILUMINACAO, LIMPEZA_CONSERVACAO ou NAO_CLASSIFICAVEL se não houver informação suficiente ou categoria adequada.
"""
