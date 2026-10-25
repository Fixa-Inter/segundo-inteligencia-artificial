# Métricas de BI

Percentuais: multiplicar por 100; divisão por zero: sem base. Filtrar volumes por criação e conclusões por data de conclusão. OS abertas representam a situação atual.

## Ordens de serviço — fato_ordem_servico

| KPI | Regra | Descrição |
|---|---|---|
| Total de OS | Contar OS criadas no período. | Volume de atendimentos gerados. |
| OS abertas | Contar status 1, 2 ou 3. | OS atrasadas, pausadas ou em andamento. |
| OS atrasadas | Contar status 1. | OS classificadas como Atrasada. |
| Taxa de atraso | Atrasadas ÷ abertas × 100. | Participação das atrasadas entre as abertas. |
| OS finalizadas | Contar finalizadas com conclusão no período. | Atendimentos atualmente encerrados no período. |
| Taxa de conclusão no prazo | No prazo ÷ finalizadas com datas válidas × 100. | Cumprimento dos prazos documentados. |
| Tempo médio de espera | Média de início − criação, com datas válidas. | Espera até o primeiro início registrado. |
| Tempo médio de resolução | Média de `tempo_resolucao_minutos` válido. | Duração calculada, descontando pausas registradas. |
| Tempo médio pausado | Média de `tempo_pausado_minutos`, incluindo zeros. | Pausa registrada média por OS. |
| Taxa de reabertura | OS reabertas ao menos uma vez ÷ total × 100. | OS que retornaram ao atendimento após finalizar. |
| Taxa de reatribuição | OS com troca de técnico ÷ total × 100. | Frequência de mudança do responsável. |
| Carga ativa por técnico | Contar abertas por técnico atual. | Distribuição dos atendimentos abertos. |
| Produtividade por técnico | Contar finalizadas no período por técnico atual. | Conclusões atribuídas a cada responsável. |
| Média de tarefas por OS | Média de `qtd_tarefas`. | Quantidade média de tarefas vinculadas. |
| Taxa de tarefas concluídas | Concluídas ÷ total de tarefas × 100; falta contagem na view. | Percentual de tarefas finalizadas. |

## Solicitações — fato_problema

| KPI | Regra | Descrição |
|---|---|---|
| Total de solicitações | Contar problemas criados no período. | Volume de demanda registrada. |
| Solicitações pendentes | Contar status 0. | Demanda aguardando decisão de análise. |
| Solicitações aprovadas | Contar status 2. | Demanda aceita na análise. |
| Solicitações reprovadas | Contar status 1. | Demanda recusada na análise. |
| Taxa de aprovação | Aprovadas ÷ total de solicitações × 100. | Participação das aprovações, incluindo pendentes na base. |
| Taxa de reprovação | Reprovadas ÷ total de solicitações × 100. | Participação das reprovações, incluindo pendentes na base. |
| Taxa de conversão em OS | Solicitações com OS ÷ total × 100. | Demanda que originou ordem de serviço. |
| Solicitações por unidade | Contar por `unidade_id`. | Distribuição da demanda entre unidades. |
| Solicitações por local | Contar por `local_id`. | Ambientes com maior volume de demanda. |
| Solicitações por categoria de equipamento | Contar por `categoria_equipamento_id`. | Categorias mais citadas nas solicitações. |
| Solicitações por período | Contar por dia, mês ou ano de criação. | Evolução temporal da demanda. |
| Taxa de recorrência por local e categoria | Consolidar episódios de 24h; recorrente se sucede outro em até 30 dias. Recorrentes ÷ episódios × 100. | Repetição de demanda por local e categoria, sem inflar por solicitações do mesmo episódio. |

Recorrência: janela fixa de 24h desde o primeiro registro; comparar inícios dos episódios e filtrar o período depois da consolidação. Janelas propostas; fonte somente problemas.

## Ocorrências — fato_ocorrencia

| KPI | Regra | Descrição |
|---|---|---|
| Total de ocorrências | Contar ocorrências criadas no período. | Volume de situações registradas como resolvidas diretamente. |
| Ocorrências por técnico | Contar por `tecnico_id`. | Distribuição dos registros entre técnicos. |
| Ocorrências por unidade | Contar por `unidade_id`. | Unidades com mais registros de resolução direta. |
| Ocorrências por local | Contar por `local_id`. | Ambientes com maior volume de ocorrências. |
| Ocorrências por categoria de problema | Contar por `categoria_problema_id`. | Natureza dos problemas atendidos. |
| Ocorrências por categoria de equipamento | Contar por `categoria_equipamento_id`. | Categorias de equipamentos associadas aos registros. |
| Ocorrências por prioridade | Contar por `prioridade`. | Distribuição entre Alta, Média e Baixa. |
| Ocorrências ativas | Contar `esta_ativo = true`. | Registros ativos no cadastro, não serviços abertos. |
| Taxa de alta prioridade | Ocorrências com prioridade 0 ÷ total × 100. | Participação das situações de alta prioridade. |
| Ocorrências por período | Contar por dia, mês ou ano de criação. | Evolução dos registros de resolução direta. |

Tempos dependem do histórico e não medem trabalho efetivo; reaberturas podem afetar a resolução. Reabertura e reatribuição usam o histórico acumulado das OS criadas no período.