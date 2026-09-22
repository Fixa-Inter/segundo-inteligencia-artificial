MAPEAMENTO_CATEGORIA_PROBLEMA_PROMPT = """
### Categorias de problema para cadastro de ocorrência
Use categoria_problema_id conforme este mapeamento, sem criar outros códigos:
1 - Elétrica: alimentação elétrica, tomadas, circuitos e instalações elétricas.
2 - Hidráulica: água, tubulações, torneiras, vazamentos e escoamento.
3 - Mecânica: mecanismos, peças móveis e funcionamento mecânico.
4 - Informática: computadores, periféricos e software.
5 - Mobiliário: mesas, cadeiras, armários e outros móveis.
6 - Climatização: ar-condicionado, ventilação e controle de temperatura.
7 - Rede e Conectividade: acesso à rede, internet, Wi-Fi e cabeamento de rede.
8 - Segurança: dispositivos e estruturas destinados à proteção e controle de acesso.
9 - Iluminação: lâmpadas, luminárias e funcionamento da iluminação.
10 - Limpeza e Conservação: limpeza e conservação dos ambientes.

Classifique a partir do relato e apresente o nome da categoria para confirmação.
Prefira a categoria específica do problema relatado; se houver dúvida relevante
entre categorias, pergunte ao usuário em vez de inventar detalhes.
Esses IDs não são IDs de categoria de equipamento do Qdrant.
"""
