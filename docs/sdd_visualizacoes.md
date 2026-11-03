# Especificação das visualizações gerenciais FIXA

Este catálogo registra as 27 análises implementadas. As definições executáveis ficam em `app/services/visualizacoes` e a interface pública em seu `__init__.py`.

| ID | Análise | Fonte | Formato |
| --- | --- | --- | --- |
| VIS-01 | OS criadas por período | os_criacao | serie_temporal |
| VIS-02 | OS finalizadas por período | os_conclusao | serie_temporal |
| VIS-03 | Distribuição das OS por status | os_atual | categorias |
| VIS-04 | Carga ativa por técnico | os_atual | categorias |
| VIS-05 | Produtividade por técnico | os_conclusao | categorias |
| VIS-06 | Distribuição do tempo de espera | os_criacao | histograma |
| VIS-07 | Distribuição do tempo de resolução | os_conclusao | histograma |
| VIS-08 | Solicitações por status | solicitacao | categorias |
| VIS-09 | Solicitações criadas por período | solicitacao | serie_temporal |
| VIS-10 | Solicitações por local | solicitacao | categorias |
| VIS-11 | Solicitações por categoria de equipamento | solicitacao | categorias |
| VIS-12 | Episódios recorrentes por categoria | recorrencia | categorias |
| VIS-13 | Recorrência por local | recorrencia | categorias |
| VIS-14 | Evolução da taxa de recorrência | recorrencia | serie_temporal |
| VIS-15 | Tempo de resolução por unidade | os_conclusao | boxplot |
| VIS-16 | Tempo pausado por categoria de problema | os_criacao | boxplot |
| VIS-17 | Tempo de espera por tipo de local | os_criacao | boxplot |
| VIS-18 | Reabertura por categoria de problema | os_criacao | categorias |
| VIS-19 | Reatribuição por técnico | os_criacao | categorias |
| VIS-20 | Evolução do cumprimento dos prazos | os_conclusao | serie_temporal |
| VIS-21 | Tempo médio de pausa por categoria de problema | os_criacao | categorias |
| VIS-22 | OS abertas com prazo vencido por local | os_atual | categorias |
| VIS-23 | Conversão de solicitações em OS por categoria | solicitacao | categorias |
| VIS-24 | Reprovação de solicitações por local | solicitacao | categorias |
| VIS-25 | Solicitações por episódio | recorrencia | histograma |
| VIS-26 | Ocorrências por período e prioridade | ocorrencia | serie_temporal |
| VIS-27 | Ocorrências de alta prioridade por local | ocorrencia | categorias |

A unidade é resolvida pelo servidor. Somente gestor e administrador na plataforma web podem consultar/publicar visualizações. Os serviços validam período, filtros, população, cobertura e limites antes da publicação.

Períodos usam início inclusivo e fim exclusivo, com máximo de 366 dias. Séries aceitam dia, semana ou mês; OS atuais são snapshot sem período. Existem limites de 50 grupos, 500 pontos e dez intervalos de histograma. Quartis e cobertura consideram a população completa; extremos publicados podem ser limitados com contagem de omissões.

Resultados de tools são capturados no servidor por execução/turno/sessão/usuário/unidade. O juiz avalia dados e texto; somente o conteúdo aprovado é publicado e persistido. Falhas, ausência de base e resultado truncado não viram gráficos de sucesso. O histórico devolve o payload salvo, sem recálculo.
