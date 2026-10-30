# Mapeamento implementado de métricas e KPIs — `workspace.fixa_pipeline`

Este documento descreve o código atual do agente de indicadores. O inventário público contém **36 tools**: 14 de ordens de serviço, 11 de solicitações, uma de recorrência e 10 de ocorrências. **35 consultam `workspace.fixa_pipeline`**. OS-14 permanece no inventário, mas retorna `INDICADOR_INDISPONIVEL` até o BI publicar as contagens necessárias para calcular a média consolidada com exatidão. OS-15 não foi implementada.

Os SQLs executáveis estão nos serviços [`ordem_servico.py`](../app/services/indicadores/ordem_servico.py), [`problema.py`](../app/services/indicadores/problema.py) e [`ocorrencia.py`](../app/services/indicadores/ocorrencia.py). O desenho, as decisões do usuário e a dependência de BI estão em [sdd_indicadores_fixa_pipeline_design.md](sdd_indicadores_fixa_pipeline_design.md); o progresso está em [sdd_indicadores_fixa_pipeline_tarefas.md](sdd_indicadores_fixa_pipeline_tarefas.md).

## Escopo e interpretação

- As tools são exclusivas de gestores. A unidade vem do vínculo do usuário autenticado, resolvido no PostgreSQL; os IDs de unidade coincidem nos dois bancos. O modelo e a mensagem do usuário não fornecem `unidade_id`. Os serviços exigem o ID positivo e as consultas filtram `unidade_id = :unidade_id` antes da agregação. Ausência de vínculo ou falha de resolução impede a consulta analítica.
- Os valores analíticos vêm apenas do Databricks. `buscar_historico` serve ao contexto conversacional e não substitui uma consulta de indicadores.
- Métricas com período usam início inclusivo e fim exclusivo. Tabelas diárias agregam por `data_referencia`; a fonte de episódios filtra `inicio_episodio`. OS-07 a OS-09 usam os timestamps do detalhe de OS. As métricas de situação atual não recebem período.
- Estados de solicitações e ocorrências selecionam registros do período de criação e refletem a última atualização disponível desses registros. O pipeline atualiza o status, sem repetir a pendência em uma nova linha a cada dia. A soma dos dias não reconstitui o estado histórico no fechamento de cada dia e não promete tempo real.
- Status de OS: 1 atrasada, 2 pausada, 3 em andamento, 4 finalizada. OS aberta usa os códigos 1, 2 e 3; atraso aqui significa status 1. Prioridade 0 significa alta. Taxas usam razão entre totais da mesma população, com denominador nulo quando não há base.
- As tools “por unidade” retornam apenas a unidade autenticada. Agrupamentos por IDs podem não trazer nomes legíveis; o agente não deve inventá-los nem apresentar comparações com outras unidades.

## Ordens de serviço

| ID | Tool | Fonte em `workspace.fixa_pipeline` | Regra implementada |
| --- | --- | --- | --- |
| OS-01 | `obter_total_os` | `gold_kpi_os_criacao_diario` | Soma de `qtd_os_criadas` por data de criação. |
| OS-02 | `obter_os_abertas` | `gold_os_por_status` | Soma de `qtd_os` nos status 1, 2 e 3; situação atual. |
| OS-03 | `obter_os_atrasadas` | `gold_os_por_status` | Soma de `qtd_os` no status 1; situação atual. |
| OS-04 | `obter_taxa_atraso_os` | `gold_os_por_status` | 100 × OS em status 1 / OS nos status 1, 2 e 3. |
| OS-05 | `obter_os_finalizadas` | `gold_kpi_os_conclusao_diario` | Soma de `qtd_os_finalizadas` por data de conclusão. |
| OS-06 | `obter_taxa_conclusao_prazo` | `gold_kpi_os_conclusao_diario` | 100 × soma das concluídas no prazo / soma das OS com prazo válido. |
| OS-07 | `obter_tempo_medio_espera_os` | `gold_os_tempos` | Média dos minutos válidos de espera, por criação. |
| OS-08 | `obter_tempo_medio_resolucao_os` | `gold_os_tempos` | Média dos minutos válidos de resolução, por conclusão. |
| OS-09 | `obter_tempo_medio_pausado_os` | `gold_os_tempos` | Média dos minutos não nulos e não negativos de pausa, por criação. |
| OS-10 | `obter_taxa_reabertura_os` | `gold_kpi_os_criacao_diario` | 100 × soma das reabertas / soma das criadas na coorte. |
| OS-11 | `obter_taxa_reatribuicao_os` | `gold_kpi_os_criacao_diario` | 100 × soma das reatribuídas / soma das criadas na coorte. |
| OS-12 | `obter_carga_ativa_tecnicos` | `gold_kpi_carga_ativa_tecnico` | Soma das OS ativas por técnico, dentro da unidade; situação atual. |
| OS-13 | `obter_produtividade_tecnicos` | `gold_kpi_produtividade_tecnico` | Soma das OS finalizadas por técnico e data de conclusão. |
| OS-14 | `obter_media_tarefas_por_os` | Sem consulta enquanto BI-01 estiver pendente | Retorna `INDICADOR_INDISPONIVEL`; não apresenta média aproximada. |

**OS-14.** A média diária fornecida pelo BI exclui OS sem tarefas. Ponderá-la por `qtd_os_criadas` produz uma média consolidada incorreta. O usuário escolheu fornecer ao BI as contagens de tarefas consideradas e de OS com tarefas da mesma unidade/data/população. Os nomes `qtd_tarefas_total` e `qtd_os_com_tarefas` são apenas sugestões; não são colunas confirmadas. Quando o contrato efetivo estiver disponível, a fórmula será `SUM(tarefas) / NULLIF(SUM(OS com tarefas), 0)`, mantendo `os_criadas` como informação adicional. A tool já exige a unidade autenticada, mas não faz consulta até a publicação desses campos.

## Solicitações e recorrência

PR-01 a PR-11 usam somente `workspace.fixa_pipeline.gold_kpi_solicitacoes_diario`, filtrada por unidade e intervalo de datas. Seus campos de estado refletem a atualização mais recente dos registros criados no período.

| ID | Tool | Regra implementada |
| --- | --- | --- |
| PR-01 | `obter_total_solicitacoes` | Soma das solicitações criadas. |
| PR-02 | `obter_solicitacoes_pendentes` | Soma das solicitações da coorte ainda pendentes. |
| PR-03 | `obter_solicitacoes_aprovadas` | Soma das solicitações da coorte aprovadas. |
| PR-04 | `obter_solicitacoes_reprovadas` | Soma das solicitações da coorte reprovadas. |
| PR-05 | `obter_taxa_aprovacao_solicitacoes` | 100 × aprovadas / total de solicitações. |
| PR-06 | `obter_taxa_reprovacao_solicitacoes` | 100 × reprovadas / total de solicitações. |
| PR-07 | `obter_taxa_conversao_solicitacoes_os` | 100 × solicitações com OS / total de solicitações. |
| PR-08 | `obter_solicitacoes_por_unidade` | Soma somente da unidade autenticada. |
| PR-09 | `obter_solicitacoes_por_local` | Soma por local dentro da unidade. |
| PR-10 | `obter_solicitacoes_por_categoria_equipamento` | Soma por categoria de equipamento dentro da unidade. |
| PR-11 | `obter_solicitacoes_por_periodo` | Soma por dia, mês ou ano dentro da unidade. |
| RC-01 | `obter_taxa_recorrencia_local_categoria` | Em `workspace.fixa_pipeline.gold_recorrencia_episodios`, 100 × episódios com `recorrente = TRUE` / episódios iniciados no período, por local e categoria. |

RC-01 usa o flag `recorrente` publicado pelo BI e a soma de solicitações dos episódios selecionados. Um episódio iniciado no período pode incluir solicitações posteriores ao fim do intervalo. `gold_kpi_recorrencia_diario` é fonte autorizada para análise futura, mas não é usada como fallback. `gold_kpi_recorrencia_diario2` foi excluída por decisão do usuário. Não foram confirmadas janelas fixas de 24 horas ou 30 dias.

## Ocorrências

OC-01 a OC-10 usam somente `workspace.fixa_pipeline.gold_kpi_ocorrencias_diario`, filtrada por unidade e intervalo de datas.

| ID | Tool | Regra implementada |
| --- | --- | --- |
| OC-01 | `obter_total_ocorrencias` | Soma de `qtd_ocorrencias`. |
| OC-02 | `obter_ocorrencias_por_tecnico` | Soma por `tecnico_id` dentro da unidade. |
| OC-03 | `obter_ocorrencias_por_unidade` | Soma somente da unidade autenticada. |
| OC-04 | `obter_ocorrencias_por_local` | Soma por `local_id` dentro da unidade. |
| OC-05 | `obter_ocorrencias_por_categoria_problema` | Soma por `categoria_problema_id` dentro da unidade. |
| OC-06 | `obter_ocorrencias_por_categoria_equipamento` | Soma por `categoria_equipamento_id` dentro da unidade. |
| OC-07 | `obter_ocorrencias_por_prioridade` | Soma por código de prioridade. |
| OC-08 | `obter_ocorrencias_ativas` | Soma de `qtd_ocorrencias_ativas`: ocorrências aguardando revisão/aprovação do gestor; nome público e chave preservados. |
| OC-09 | `obter_taxa_ocorrencias_alta_prioridade` | 100 × ocorrências com prioridade 0 / todas as ocorrências. |
| OC-10 | `obter_ocorrencias_por_periodo` | Soma por dia, mês ou ano dentro da unidade. |

## Estado de validação

Os 69 testes locais aprovados verificam fonte, escopo, parâmetros, contratos e fluxo afetado com dependências externas simuladas; não comprovam os números do Databricks. Uma verificação real de leitura encontrou as nove tabelas usadas e as colunas verificadas, e comparou o total de OS de duas unidades com valores distintos; essa amostra confirma o isolamento de OS-01, sem validar todas as demais fórmulas. A migração de OS-14 depende do contrato efetivo de BI-01, incluindo nomes, tipos, população e cobertura histórica dos novos campos. As [dez perguntas de validação manual](validacao_manual_indicadores_fixa_pipeline.md) cobrem as 36 tools expostas e registram a indisponibilidade esperada de OS-14.
