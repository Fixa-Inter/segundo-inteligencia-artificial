MAPEAMENTO_CATEGORIA_PROBLEMA_PROMPT = """
### Categorias de problema para cadastro de ocorrência
Envie categoria_problema_id como o nome textual do enum, nunca como inteiro:
ELETRICA - Elétrica: alimentação elétrica, tomadas, circuitos e instalações elétricas.
HIDRAULICA - Hidráulica: água, tubulações, torneiras, vazamentos e escoamento.
MECANICA - Mecânica: mecanismos, peças móveis e funcionamento mecânico.
INFORMATICA - Informática: computadores, periféricos e software.
MOBILIARIO - Mobiliário: mesas, cadeiras, armários e outros móveis.
CLIMATIZACAO - Climatização: ar-condicionado, ventilação e controle de temperatura.
REDE_CONECTIVIDADE - Rede e Conectividade: acesso à rede, internet, Wi-Fi e cabeamento de rede.
SEGURANCA - Segurança: dispositivos e estruturas destinados à proteção e controle de acesso.
ILUMINACAO - Iluminação: lâmpadas, luminárias e funcionamento da iluminação.
LIMPEZA_CONSERVACAO - Limpeza e Conservação: limpeza e conservação dos ambientes.

Classifique a partir do relato e apresente o nome da categoria para confirmação.
Prefira a categoria específica do problema relatado; se houver dúvida relevante
entre categorias, pergunte ao usuário em vez de inventar detalhes.
Esses nomes não são IDs de categoria de equipamento do Qdrant.
"""
