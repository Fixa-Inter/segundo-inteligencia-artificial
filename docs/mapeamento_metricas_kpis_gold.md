# Mapeamento de métricas e KPIs — `workspace.gold`

Escopo: 37 indicadores solicitados no arquivo `mapeamento_kpis_metricas_iniciais.md` (15 OS, 11 solicitações, 10 ocorrências e 1 recorrência). Os nomes de função abaixo são **propostos**; nenhuma função ou consulta foi implementada. **KPI** designa taxa percentual; **métrica** designa contagem ou média. Cada item usa no máximo **uma consulta SQL**. OS-15 não possui consulta executável com as tabelas fornecidas.

## Convenções e evidências

- `:inicio` e `:fim` delimitam `[início, fim)`. Nas tabelas diárias são **datas inteiras**; em `os_tempos` e `recorrencia_episodios` são timestamps. `:granularidade` aceita somente `dia`, `mes` ou `ano`. Todos são parâmetros, nunca texto concatenado ao SQL.
- `data_referencia` nas tabelas de criação/solicitação/ocorrência representa o dia de criação; em conclusão/produtividade, o dia de conclusão. Essa correspondência é descrita pelo mapeamento das tabelas e precisa ser confirmada com a definição das tabelas no Databricks.
- Contagens vazias retornam 0; taxas e médias sem observações válidas retornam `NULL` (“sem base”). Taxas são percentuais de 0 a 100. Não calcular médias de percentuais diários. Tempos estão em minutos.
- Status de OS: 1 atrasada, 2 pausada, 3 em andamento, 4 finalizada. “Aberta” = 1, 2 ou 3. “Atrasada” neste relatório é **status 1**, não prazo vencido. Prioridade 0 = alta. Status de solicitação: 0 pendente, 1 reprovada, 2 aprovada.
- Snapshots descrevem o **estado atual da última atualização**, sem recorte histórico. Status e conversão de solicitações, atividade cadastral das ocorrências, reabertura e reatribuição são estados/resumos atuais das coortes criadas no período. Conclusões exigem status atual finalizado. Atribuição de técnico é a atual.
- Evidências: **I** = [`mapeamento_kpis_metricas_iniciais.md`](<C:/Users/lorenzooliveira-ieg/Downloads/mapeamento_kpis_metricas_iniciais.md>), linha nominal da métrica; **C** = [`contexto_kpi_metricas.md`](<C:/Users/lorenzooliveira-ieg/Downloads/contexto_kpi_metricas.md>), seção/ID indicado; **T** = [`mapeamento_tabelas_kpi.md`](<C:/Users/lorenzooliveira-ieg/Downloads/mapeamento_tabelas_kpi.md>), tabela e colunas citadas. I comprova o pedido; C, a regra; T, os campos disponíveis. São evidências documentais, não testes de dados reais.
- O projeto roteia `analytics` ao agente de gestor, mas [`app/agents/registro.py`](../app/agents/registro.py) o instancia sem ferramentas de dados; [`app/agents/indicadores.py`](../app/agents/indicadores.py) recebe apenas `buscar_historico` por padrão. O prompt atual contém nomes ilustrativos de ferramentas e ainda afirma PostgreSQL como fonte. Este relatório fixa as definições analíticas para a futura implementação com `workspace.gold`, sem alterar o código.

## Ordens de serviço

### OS-01 — Total de OS

- **Tipo/função:** métrica · `obter_total_os`. **Uso:** volume de OS criadas no período.
- **Cálculo/evidência:** soma das OS criadas por dia; I “Total de OS”; C §4.1 OS-01 e §3.3; T `kpi_os_criacao_diario.qtd_os_criadas`.

```sql
SELECT COALESCE(SUM(qtd_os_criadas), 0) AS total_os
FROM workspace.gold.kpi_os_criacao_diario
WHERE data_referencia >= CAST(:inicio AS DATE) AND data_referencia < CAST(:fim AS DATE);
```

### OS-02 — OS abertas

- **Tipo/função:** métrica · `obter_os_abertas`. **Uso:** backlog atual, inclusive OS antigas.
- **Cálculo/evidência:** soma das OS nos status 1, 2 e 3, sem filtro de criação; I “OS abertas”; C §4.1 OS-02 e §3.2; T `os_por_status.status_id`, `qtd_os`.

```sql
SELECT COALESCE(SUM(qtd_os), 0) AS os_abertas
FROM workspace.gold.os_por_status WHERE status_id IN (1, 2, 3);
```

### OS-03 — OS atrasadas

- **Tipo/função:** métrica · `obter_os_atrasadas`. **Uso:** quantidade atual em status Atrasada.
- **Cálculo/evidência:** soma do status 1; I “OS atrasadas”; C §4.1 OS-03 e §3.2; T `os_por_status.status_id`, `qtd_os`.

```sql
SELECT COALESCE(SUM(qtd_os), 0) AS os_atrasadas
FROM workspace.gold.os_por_status WHERE status_id = 1;
```

### OS-04 — Taxa de atraso

- **Tipo/função:** KPI · `obter_taxa_atraso_os`. **Uso:** proporção do backlog atual classificada como atrasada.
- **Cálculo/evidência:** `100 × status 1 / status (1,2,3)`; I “Taxa de atraso”; C §4.1 OS-04 e §3.2; T `os_por_status.status_id`, `qtd_os`. Retorna as duas contagens de apoio.

```sql
SELECT COALESCE(SUM(CASE WHEN status_id = 1 THEN qtd_os ELSE 0 END), 0) AS atrasadas,
       COALESCE(SUM(CASE WHEN status_id IN (1,2,3) THEN qtd_os ELSE 0 END), 0) AS abertas,
       100.0 * SUM(CASE WHEN status_id = 1 THEN qtd_os ELSE 0 END)
       / NULLIF(SUM(CASE WHEN status_id IN (1,2,3) THEN qtd_os ELSE 0 END), 0) AS taxa_pct
FROM workspace.gold.os_por_status;
```

### OS-05 — OS finalizadas

- **Tipo/função:** métrica · `obter_os_finalizadas`. **Uso:** conclusões no período, entre OS **atualmente** finalizadas.
- **Cálculo/evidência:** soma diária de conclusões; I “OS finalizadas”; C §4.1 OS-05 e §3.3; T `kpi_os_conclusao_diario.qtd_os_finalizadas`. Reabertura posterior pode retirar uma OS dessa série; OS sem data de conclusão não entra no período.

```sql
SELECT COALESCE(SUM(qtd_os_finalizadas), 0) AS os_finalizadas
FROM workspace.gold.kpi_os_conclusao_diario
WHERE data_referencia >= CAST(:inicio AS DATE) AND data_referencia < CAST(:fim AS DATE);
```

### OS-06 — Taxa de conclusão no prazo

- **Tipo/função:** KPI · `obter_taxa_conclusao_prazo`. **Uso:** cumprimento dos prazos documentados nas conclusões do período.
- **Cálculo/evidência:** `100 × concluídas no prazo / finalizadas com prazo válido`; I “Taxa de conclusão no prazo”; C §4.1 OS-06; T `kpi_os_conclusao_diario` com `qtd_os_concluidas_no_prazo`, `qtd_os_com_prazo_valido`, `qtd_os_finalizadas`. A diferença entre finalizadas e elegíveis mede exclusão por falta de datas válidas.

```sql
SELECT COALESCE(SUM(qtd_os_finalizadas), 0) AS finalizadas,
       COALESCE(SUM(qtd_os_com_prazo_valido), 0) AS elegiveis,
       COALESCE(SUM(qtd_os_concluidas_no_prazo), 0) AS no_prazo,
       100.0 * SUM(qtd_os_concluidas_no_prazo)
       / NULLIF(SUM(qtd_os_com_prazo_valido), 0) AS taxa_pct
FROM workspace.gold.kpi_os_conclusao_diario
WHERE data_referencia >= CAST(:inicio AS DATE) AND data_referencia < CAST(:fim AS DATE);
```

### OS-07 — Tempo médio de espera

- **Tipo/função:** métrica · `obter_tempo_medio_espera_os`. **Uso:** espera até o primeiro início conhecido das OS criadas no período.
- **Cálculo/evidência:** média de minutos válidos; I “Tempo médio de espera”; C §4.1 OS-07; T `os_tempos.data_criacao`, `data_inicio`, `tempo_espera_minutos`. Usa o detalhe porque a tabela diária não informa quantas OS compõem cada média.

```sql
SELECT COUNT(*) AS os_com_espera_valida, AVG(tempo_espera_minutos) AS media_minutos
FROM workspace.gold.os_tempos
WHERE data_criacao >= :inicio AND data_criacao < :fim
  AND data_inicio >= data_criacao
  AND tempo_espera_minutos IS NOT NULL AND tempo_espera_minutos >= 0;
```

### OS-08 — Tempo médio de resolução

- **Tipo/função:** métrica · `obter_tempo_medio_resolucao_os`. **Uso:** duração calculada das OS atualmente finalizadas no período.
- **Cálculo/evidência:** média de `tempo_resolucao_minutos` válido; I “Tempo médio de resolução”; C §4.1 OS-08; T `os_tempos.status_id`, `data_conclusao`, `tempo_resolucao_minutos`. Não mede esforço efetivo; reaberturas podem inflar a duração.

```sql
SELECT COUNT(*) AS os_com_tempo_valido, AVG(tempo_resolucao_minutos) AS media_minutos
FROM workspace.gold.os_tempos
WHERE status_id = 4 AND data_conclusao >= :inicio AND data_conclusao < :fim
  AND data_inicio >= data_criacao AND data_conclusao >= data_inicio
  AND tempo_resolucao_minutos IS NOT NULL AND tempo_resolucao_minutos >= 0;
```

### OS-09 — Tempo médio pausado

- **Tipo/função:** métrica · `obter_tempo_medio_pausado_os`. **Uso:** pausa registrada nas OS criadas no período.
- **Cálculo/evidência:** média de minutos não nulos e não negativos, **incluindo zero**; I “Tempo médio pausado”; C §4.1 OS-09; T `os_tempos.data_criacao`, `tempo_pausado_minutos`. Zero pode significar ausência de registro de pausa.

```sql
SELECT COUNT(*) AS os_com_tempo_registrado, AVG(tempo_pausado_minutos) AS media_minutos
FROM workspace.gold.os_tempos
WHERE data_criacao >= :inicio AND data_criacao < :fim
  AND tempo_pausado_minutos IS NOT NULL AND tempo_pausado_minutos >= 0;
```

### OS-10 — Taxa de reabertura

- **Tipo/função:** KPI · `obter_taxa_reabertura_os`. **Uso:** participação de OS da coorte criada no período que já reabriram alguma vez.
- **Cálculo/evidência:** `100 × OS reabertas / OS criadas`; I “Taxa de reabertura”; C §4.1 OS-10 e §3.3; T `kpi_os_criacao_diario.qtd_os_reabertas`, `qtd_os_criadas`. Conta OS, não eventos; histórico acumulado até a atualização da gold.

```sql
SELECT COALESCE(SUM(qtd_os_reabertas), 0) AS reabertas,
       COALESCE(SUM(qtd_os_criadas), 0) AS criadas,
       100.0 * SUM(qtd_os_reabertas) / NULLIF(SUM(qtd_os_criadas), 0) AS taxa_pct
FROM workspace.gold.kpi_os_criacao_diario
WHERE data_referencia >= CAST(:inicio AS DATE) AND data_referencia < CAST(:fim AS DATE);
```

### OS-11 — Taxa de reatribuição

- **Tipo/função:** KPI · `obter_taxa_reatribuicao_os`. **Uso:** participação de OS da coorte criada no período que já trocaram de técnico.
- **Cálculo/evidência:** `100 × OS reatribuídas / OS criadas`; I “Taxa de reatribuição”; C §4.1 OS-11 e §3.3; T `kpi_os_criacao_diario.qtd_os_reatribuidas`, `qtd_os_criadas`. Conta OS, não trocas.

```sql
SELECT COALESCE(SUM(qtd_os_reatribuidas), 0) AS reatribuidas,
       COALESCE(SUM(qtd_os_criadas), 0) AS criadas,
       100.0 * SUM(qtd_os_reatribuidas) / NULLIF(SUM(qtd_os_criadas), 0) AS taxa_pct
FROM workspace.gold.kpi_os_criacao_diario
WHERE data_referencia >= CAST(:inicio AS DATE) AND data_referencia < CAST(:fim AS DATE);
```

### OS-12 — Carga ativa por técnico

- **Tipo/função:** métrica · `obter_carga_ativa_tecnicos`. **Uso:** distribuição atual das OS abertas por responsável.
- **Cálculo/evidência:** soma das OS ativas por técnico; I “Carga ativa por técnico”; C §4.1 OS-12; T `kpi_carga_ativa_tecnico.tecnico_id`, `tecnico_nome`, `qtd_os_ativas`. Sem filtro de criação. Não mede capacidade; verificar se OS sem técnico aparecem em grupo nulo na gold.

```sql
SELECT tecnico_id, tecnico_nome, COALESCE(SUM(qtd_os_ativas), 0) AS os_abertas
FROM workspace.gold.kpi_carga_ativa_tecnico
GROUP BY tecnico_id, tecnico_nome ORDER BY os_abertas DESC, tecnico_id;
```

### OS-13 — Produtividade por técnico

- **Tipo/função:** métrica · `obter_produtividade_tecnicos`. **Uso:** conclusões no período por responsável **atual**.
- **Cálculo/evidência:** soma das OS finalizadas por técnico e dia de conclusão; I “Produtividade por técnico”; C §4.1 OS-13; T `kpi_produtividade_tecnico.tecnico_id`, `tecnico_nome`, `qtd_os_finalizadas`. Reatribuição posterior pode alterar atribuição histórica.

```sql
SELECT tecnico_id, tecnico_nome, COALESCE(SUM(qtd_os_finalizadas), 0) AS os_finalizadas
FROM workspace.gold.kpi_produtividade_tecnico
WHERE data_referencia >= CAST(:inicio AS DATE) AND data_referencia < CAST(:fim AS DATE)
GROUP BY tecnico_id, tecnico_nome ORDER BY os_finalizadas DESC, tecnico_id;
```

### OS-14 — Média de tarefas por OS

- **Tipo/função:** métrica · `obter_media_tarefas_por_os`. **Uso:** tarefas vinculadas, inclusive inativas, por OS criada no período.
- **Cálculo/evidência:** média diária ponderada pelo número de OS criadas; I “Média de tarefas por OS”; C §4.1 OS-14; T `kpi_os_criacao_diario.media_tarefas_por_os`, `qtd_os_criadas`. **Condicional:** só é exata se a média diária usar todas as OS do dia, inclusive as com zero tarefa. Confirmar definição da gold; se houver exclusões, faltam numerador e denominador válidos.

```sql
SELECT COALESCE(SUM(qtd_os_criadas), 0) AS os_criadas,
       CASE WHEN SUM(CASE WHEN qtd_os_criadas > 0 AND media_tarefas_por_os IS NULL THEN 1 ELSE 0 END) > 0
            THEN NULL
            ELSE SUM(media_tarefas_por_os * qtd_os_criadas)
                 / NULLIF(SUM(qtd_os_criadas), 0) END AS media_tarefas
FROM workspace.gold.kpi_os_criacao_diario
WHERE data_referencia >= CAST(:inicio AS DATE) AND data_referencia < CAST(:fim AS DATE);
```

### OS-15 — Taxa de tarefas concluídas

- **Tipo/função:** KPI · `obter_taxa_tarefas_concluidas`. **Uso:** percentual de tarefas concluídas entre tarefas das OS da coorte escolhida.
- **Cálculo/evidência:** `100 × tarefas concluídas / tarefas totais`, com definição prévia sobre tarefas inativas; I “Taxa de tarefas concluídas”; C §4.1 OS-15; T: **nenhuma** tabela gold mapeada expõe contagem de tarefas concluídas. `media_tarefas_por_os` não fornece numerador. **SQL executável: indisponível.** Expor na gold contagens de tarefas totais e concluídas por coorte de criação; então ambas podem ser somadas e divididas em **uma consulta**. Definir inclusão de tarefas inativas antes do cálculo.

## Solicitações

As tabelas gold chamam estas linhas de “solicitações”; no contexto, elas correspondem a problemas. O período sempre seleciona a **coorte por criação**. Status e conversão descrevem sua situação atual.

### PR-01 — Total de solicitações

- **Tipo/função:** métrica · `obter_total_solicitacoes`. **Uso:** demanda registrada no período.
- **Cálculo/evidência:** soma de solicitações; I “Total de solicitações”; C §4.2 PR-01; T `kpi_solicitacoes_diario.qtd_solicitacoes`.

```sql
SELECT COALESCE(SUM(qtd_solicitacoes), 0) AS total_solicitacoes
FROM workspace.gold.kpi_solicitacoes_diario
WHERE data_referencia >= CAST(:inicio AS DATE) AND data_referencia < CAST(:fim AS DATE);
```

### PR-02 — Solicitações pendentes

- **Tipo/função:** métrica · `obter_solicitacoes_pendentes`. **Uso:** coorte ainda aguardando decisão.
- **Cálculo/evidência:** soma no status atual 0; I “Solicitações pendentes”; C §4.2 PR-02; T `kpi_solicitacoes_diario.qtd_solicitacoes_pendentes`.

```sql
SELECT COALESCE(SUM(qtd_solicitacoes_pendentes), 0) AS pendentes
FROM workspace.gold.kpi_solicitacoes_diario
WHERE data_referencia >= CAST(:inicio AS DATE) AND data_referencia < CAST(:fim AS DATE);
```

### PR-03 — Solicitações aprovadas

- **Tipo/função:** métrica · `obter_solicitacoes_aprovadas`. **Uso:** coorte atualmente aceita.
- **Cálculo/evidência:** soma no status atual 2; I “Solicitações aprovadas”; C §4.2 PR-03; T `kpi_solicitacoes_diario.qtd_solicitacoes_aprovadas`.

```sql
SELECT COALESCE(SUM(qtd_solicitacoes_aprovadas), 0) AS aprovadas
FROM workspace.gold.kpi_solicitacoes_diario
WHERE data_referencia >= CAST(:inicio AS DATE) AND data_referencia < CAST(:fim AS DATE);
```

### PR-04 — Solicitações reprovadas

- **Tipo/função:** métrica · `obter_solicitacoes_reprovadas`. **Uso:** coorte atualmente recusada.
- **Cálculo/evidência:** soma no status atual 1; I “Solicitações reprovadas”; C §4.2 PR-04; T `kpi_solicitacoes_diario.qtd_solicitacoes_reprovadas`.

```sql
SELECT COALESCE(SUM(qtd_solicitacoes_reprovadas), 0) AS reprovadas
FROM workspace.gold.kpi_solicitacoes_diario
WHERE data_referencia >= CAST(:inicio AS DATE) AND data_referencia < CAST(:fim AS DATE);
```

### PR-05 — Taxa de aprovação

- **Tipo/função:** KPI · `obter_taxa_aprovacao_solicitacoes`. **Uso:** parcela aprovada da demanda criada, incluindo pendentes na base.
- **Cálculo/evidência:** `100 × aprovadas / todas`; I “Taxa de aprovação”; C §4.2 PR-05; T `kpi_solicitacoes_diario.qtd_solicitacoes_aprovadas`, `qtd_solicitacoes`.

```sql
SELECT COALESCE(SUM(qtd_solicitacoes_aprovadas), 0) AS aprovadas,
       COALESCE(SUM(qtd_solicitacoes), 0) AS total,
       100.0 * SUM(qtd_solicitacoes_aprovadas) / NULLIF(SUM(qtd_solicitacoes), 0) AS taxa_pct
FROM workspace.gold.kpi_solicitacoes_diario
WHERE data_referencia >= CAST(:inicio AS DATE) AND data_referencia < CAST(:fim AS DATE);
```

### PR-06 — Taxa de reprovação

- **Tipo/função:** KPI · `obter_taxa_reprovacao_solicitacoes`. **Uso:** parcela recusada da demanda criada, incluindo pendentes na base.
- **Cálculo/evidência:** `100 × reprovadas / todas`; I “Taxa de reprovação”; C §4.2 PR-06; T `kpi_solicitacoes_diario.qtd_solicitacoes_reprovadas`, `qtd_solicitacoes`.

```sql
SELECT COALESCE(SUM(qtd_solicitacoes_reprovadas), 0) AS reprovadas,
       COALESCE(SUM(qtd_solicitacoes), 0) AS total,
       100.0 * SUM(qtd_solicitacoes_reprovadas) / NULLIF(SUM(qtd_solicitacoes), 0) AS taxa_pct
FROM workspace.gold.kpi_solicitacoes_diario
WHERE data_referencia >= CAST(:inicio AS DATE) AND data_referencia < CAST(:fim AS DATE);
```

### PR-07 — Taxa de conversão em OS

- **Tipo/função:** KPI · `obter_taxa_conversao_solicitacoes_os`. **Uso:** parcela da demanda que originou OS.
- **Cálculo/evidência:** `100 × solicitações com OS / todas`; I “Taxa de conversão em OS”; C §4.2 PR-07; T `kpi_solicitacoes_diario.qtd_solicitacoes_com_os`, `qtd_solicitacoes`. Uma solicitação conta uma vez, mesmo que gere mais de uma OS.

```sql
SELECT COALESCE(SUM(qtd_solicitacoes_com_os), 0) AS com_os,
       COALESCE(SUM(qtd_solicitacoes), 0) AS total,
       100.0 * SUM(qtd_solicitacoes_com_os) / NULLIF(SUM(qtd_solicitacoes), 0) AS taxa_pct
FROM workspace.gold.kpi_solicitacoes_diario
WHERE data_referencia >= CAST(:inicio AS DATE) AND data_referencia < CAST(:fim AS DATE);
```

### PR-08 — Solicitações por unidade

- **Tipo/função:** métrica · `obter_solicitacoes_por_unidade`. **Uso:** concentração da demanda entre unidades.
- **Cálculo/evidência:** soma por `unidade_id`; I “Solicitações por unidade”; C §4.2 PR-08; T `kpi_solicitacoes_diario.unidade_id`, `qtd_solicitacoes`. A tabela não fornece o nome da unidade.

```sql
SELECT unidade_id, SUM(qtd_solicitacoes) AS solicitacoes
FROM workspace.gold.kpi_solicitacoes_diario
WHERE data_referencia >= CAST(:inicio AS DATE) AND data_referencia < CAST(:fim AS DATE)
GROUP BY unidade_id ORDER BY solicitacoes DESC, unidade_id;
```

### PR-09 — Solicitações por local

- **Tipo/função:** métrica · `obter_solicitacoes_por_local`. **Uso:** locais com maior volume de demanda.
- **Cálculo/evidência:** soma por `local_id`; I “Solicitações por local”; C §4.2 PR-09; T `kpi_solicitacoes_diario.local_id`, `qtd_solicitacoes`. Sem nome/tipo de local nesta tabela.

```sql
SELECT local_id, SUM(qtd_solicitacoes) AS solicitacoes
FROM workspace.gold.kpi_solicitacoes_diario
WHERE data_referencia >= CAST(:inicio AS DATE) AND data_referencia < CAST(:fim AS DATE)
GROUP BY local_id ORDER BY solicitacoes DESC, local_id;
```

### PR-10 — Solicitações por categoria de equipamento

- **Tipo/função:** métrica · `obter_solicitacoes_por_categoria_equipamento`. **Uso:** categorias mais presentes na demanda.
- **Cálculo/evidência:** soma por `categoria_equipamento_id`; I “Solicitações por categoria de equipamento”; C §4.2 PR-10; T `kpi_solicitacoes_diario.categoria_equipamento_id`, `qtd_solicitacoes`. Não confundir com categoria de problema.

```sql
SELECT categoria_equipamento_id, SUM(qtd_solicitacoes) AS solicitacoes
FROM workspace.gold.kpi_solicitacoes_diario
WHERE data_referencia >= CAST(:inicio AS DATE) AND data_referencia < CAST(:fim AS DATE)
GROUP BY categoria_equipamento_id ORDER BY solicitacoes DESC, categoria_equipamento_id;
```

### PR-11 — Solicitações por período

- **Tipo/função:** métrica · `obter_solicitacoes_por_periodo`. **Uso:** evolução diária, mensal ou anual das criações.
- **Cálculo/evidência:** soma por início do dia/mês/ano; I “Solicitações por período”; C §4.2 PR-11; T `kpi_solicitacoes_diario.data_referencia`, `qtd_solicitacoes`. Meses/anos sem registros não aparecem.

```sql
SELECT CASE :granularidade WHEN 'dia' THEN data_referencia
       WHEN 'mes' THEN TRUNC(data_referencia, 'MM')
       WHEN 'ano' THEN TRUNC(data_referencia, 'YYYY') END AS periodo,
       SUM(qtd_solicitacoes) AS solicitacoes
FROM workspace.gold.kpi_solicitacoes_diario
WHERE data_referencia >= CAST(:inicio AS DATE) AND data_referencia < CAST(:fim AS DATE)
GROUP BY 1 ORDER BY 1;
```

### RC-01 — Taxa de recorrência por local e categoria

- **Tipo/função:** KPI · `obter_taxa_recorrencia_local_categoria`. **Uso:** repetição de demanda em episódios de cada par local/categoria de equipamento.
- **Cálculo/evidência:** `100 × episódios recorrentes iniciados no período / episódios iniciados no período`; I “Taxa de recorrência por local e categoria”; C §5 RC-01; T `recorrencia_episodios.local_id`, `categoria_equipamento_id`, `inicio_episodio`, `qtd_solicitacoes`, `recorrente`. A gold **já deve ter** consolidado janelas fixas de 24 h e marcado recorrência entre inícios de episódios consecutivos em até 30 dias, usando todo o histórico **antes** do filtro. Essas regras não podem ser auditadas só pelo esquema. `qtd_solicitacoes` é o total dos episódios iniciados no intervalo, podendo incluir registros após `:fim`.

```sql
SELECT local_id, categoria_equipamento_id,
       COALESCE(SUM(qtd_solicitacoes), 0) AS solicitacoes_nos_episodios,
       COUNT(*) AS episodios,
       COUNT(*) FILTER (WHERE recorrente = TRUE) AS episodios_recorrentes,
       100.0 * COUNT(*) FILTER (WHERE recorrente = TRUE) / NULLIF(COUNT(*), 0) AS taxa_pct
FROM workspace.gold.recorrencia_episodios
WHERE inicio_episodio >= :inicio AND inicio_episodio < :fim
GROUP BY local_id, categoria_equipamento_id
ORDER BY episodios DESC, local_id, categoria_equipamento_id;
```

## Ocorrências

Ocorrência é registro de resolução direta. “Ativa” significa ativa no cadastro, não atendimento em aberto. As consultas usam a data de criação do registro.

### OC-01 — Total de ocorrências

- **Tipo/função:** métrica · `obter_total_ocorrencias`. **Uso:** volume registrado no período.
- **Cálculo/evidência:** soma das ocorrências; I “Total de ocorrências”; C §4.3 OC-01; T `kpi_ocorrencias_diario.qtd_ocorrencias`.

```sql
SELECT COALESCE(SUM(qtd_ocorrencias), 0) AS total_ocorrencias
FROM workspace.gold.kpi_ocorrencias_diario
WHERE data_referencia >= CAST(:inicio AS DATE) AND data_referencia < CAST(:fim AS DATE);
```

### OC-02 — Ocorrências por técnico

- **Tipo/função:** métrica · `obter_ocorrencias_por_tecnico`. **Uso:** distribuição dos registros entre técnicos.
- **Cálculo/evidência:** soma por `tecnico_id`; I “Ocorrências por técnico”; C §4.3 OC-02; T `kpi_ocorrencias_diario.tecnico_id`, `qtd_ocorrencias`. Volume depende da disciplina de registro; não é produtividade isolada.

```sql
SELECT tecnico_id, SUM(qtd_ocorrencias) AS ocorrencias
FROM workspace.gold.kpi_ocorrencias_diario
WHERE data_referencia >= CAST(:inicio AS DATE) AND data_referencia < CAST(:fim AS DATE)
GROUP BY tecnico_id ORDER BY ocorrencias DESC, tecnico_id;
```

### OC-03 — Ocorrências por unidade

- **Tipo/função:** métrica · `obter_ocorrencias_por_unidade`. **Uso:** unidades com mais registros de resolução direta.
- **Cálculo/evidência:** soma por `unidade_id`; I “Ocorrências por unidade”; C §4.3 OC-03; T `kpi_ocorrencias_diario.unidade_id`, `qtd_ocorrencias`.

```sql
SELECT unidade_id, SUM(qtd_ocorrencias) AS ocorrencias
FROM workspace.gold.kpi_ocorrencias_diario
WHERE data_referencia >= CAST(:inicio AS DATE) AND data_referencia < CAST(:fim AS DATE)
GROUP BY unidade_id ORDER BY ocorrencias DESC, unidade_id;
```

### OC-04 — Ocorrências por local

- **Tipo/função:** métrica · `obter_ocorrencias_por_local`. **Uso:** locais com mais resoluções diretas registradas.
- **Cálculo/evidência:** soma por `local_id`; I “Ocorrências por local”; C §4.3 OC-04; T `kpi_ocorrencias_diario.local_id`, `qtd_ocorrencias`.

```sql
SELECT local_id, SUM(qtd_ocorrencias) AS ocorrencias
FROM workspace.gold.kpi_ocorrencias_diario
WHERE data_referencia >= CAST(:inicio AS DATE) AND data_referencia < CAST(:fim AS DATE)
GROUP BY local_id ORDER BY ocorrencias DESC, local_id;
```

### OC-05 — Ocorrências por categoria de problema

- **Tipo/função:** métrica · `obter_ocorrencias_por_categoria_problema`. **Uso:** natureza dos problemas resolvidos diretamente.
- **Cálculo/evidência:** soma por `categoria_problema_id`; I “Ocorrências por categoria de problema”; C §4.3 OC-05; T `kpi_ocorrencias_diario.categoria_problema_id`, `qtd_ocorrencias`.

```sql
SELECT categoria_problema_id, SUM(qtd_ocorrencias) AS ocorrencias
FROM workspace.gold.kpi_ocorrencias_diario
WHERE data_referencia >= CAST(:inicio AS DATE) AND data_referencia < CAST(:fim AS DATE)
GROUP BY categoria_problema_id ORDER BY ocorrencias DESC, categoria_problema_id;
```

### OC-06 — Ocorrências por categoria de equipamento

- **Tipo/função:** métrica · `obter_ocorrencias_por_categoria_equipamento`. **Uso:** categorias de equipamento citadas nos registros.
- **Cálculo/evidência:** soma por `categoria_equipamento_id`; I “Ocorrências por categoria de equipamento”; C §4.3 OC-06; T `kpi_ocorrencias_diario.categoria_equipamento_id`, `qtd_ocorrencias`.

```sql
SELECT categoria_equipamento_id, SUM(qtd_ocorrencias) AS ocorrencias
FROM workspace.gold.kpi_ocorrencias_diario
WHERE data_referencia >= CAST(:inicio AS DATE) AND data_referencia < CAST(:fim AS DATE)
GROUP BY categoria_equipamento_id ORDER BY ocorrencias DESC, categoria_equipamento_id;
```

### OC-07 — Ocorrências por prioridade

- **Tipo/função:** métrica · `obter_ocorrencias_por_prioridade`. **Uso:** distribuição de prioridade alta (0), média (1) e baixa (2).
- **Cálculo/evidência:** soma por código `prioridade`; I “Ocorrências por prioridade”; C §4.3 OC-07 e §3.1; T `kpi_ocorrencias_diario.prioridade`, `qtd_ocorrencias`.

```sql
SELECT prioridade, SUM(qtd_ocorrencias) AS ocorrencias
FROM workspace.gold.kpi_ocorrencias_diario
WHERE data_referencia >= CAST(:inicio AS DATE) AND data_referencia < CAST(:fim AS DATE)
GROUP BY prioridade ORDER BY prioridade;
```

### OC-08 — Ocorrências ativas

- **Tipo/função:** métrica · `obter_ocorrencias_ativas`. **Uso:** registros atualmente ativos no cadastro, dentre os criados no período.
- **Cálculo/evidência:** soma do indicador cadastral ativo; I “Ocorrências ativas”; C §4.3 OC-08; T `kpi_ocorrencias_diario.qtd_ocorrencias_ativas`. Confirmar que esse campo reflete o estado cadastral atual da coorte, pois a definição física da gold não foi fornecida.

```sql
SELECT COALESCE(SUM(qtd_ocorrencias_ativas), 0) AS ocorrencias_ativas
FROM workspace.gold.kpi_ocorrencias_diario
WHERE data_referencia >= CAST(:inicio AS DATE) AND data_referencia < CAST(:fim AS DATE);
```

### OC-09 — Taxa de alta prioridade

- **Tipo/função:** KPI · `obter_taxa_ocorrencias_alta_prioridade`. **Uso:** participação das ocorrências de prioridade 0 no volume registrado.
- **Cálculo/evidência:** `100 × ocorrências com prioridade 0 / todas`; I “Taxa de alta prioridade”; C §4.3 OC-09; T `kpi_ocorrencias_diario.prioridade`, `qtd_ocorrencias`. Calcula pelo código em vez da coluna pré-agregada para evitar dependência da definição da contagem de alta prioridade.

```sql
SELECT COALESCE(SUM(CASE WHEN prioridade = 0 THEN qtd_ocorrencias ELSE 0 END), 0) AS alta,
       COALESCE(SUM(qtd_ocorrencias), 0) AS total,
       100.0 * SUM(CASE WHEN prioridade = 0 THEN qtd_ocorrencias ELSE 0 END)
       / NULLIF(SUM(qtd_ocorrencias), 0) AS taxa_pct
FROM workspace.gold.kpi_ocorrencias_diario
WHERE data_referencia >= CAST(:inicio AS DATE) AND data_referencia < CAST(:fim AS DATE);
```

### OC-10 — Ocorrências por período

- **Tipo/função:** métrica · `obter_ocorrencias_por_periodo`. **Uso:** evolução diária, mensal ou anual dos registros.
- **Cálculo/evidência:** soma por início do dia/mês/ano; I “Ocorrências por período”; C §4.3 OC-10; T `kpi_ocorrencias_diario.data_referencia`, `qtd_ocorrencias`. Meses/anos sem registros não aparecem.

```sql
SELECT CASE :granularidade WHEN 'dia' THEN data_referencia
       WHEN 'mes' THEN TRUNC(data_referencia, 'MM')
       WHEN 'ano' THEN TRUNC(data_referencia, 'YYYY') END AS periodo,
       SUM(qtd_ocorrencias) AS ocorrencias
FROM workspace.gold.kpi_ocorrencias_diario
WHERE data_referencia >= CAST(:inicio AS DATE) AND data_referencia < CAST(:fim AS DATE)
GROUP BY 1 ORDER BY 1;
```

## Validações necessárias antes do consumo

1. Conferir no Databricks as definições e a atualização das tabelas gold: granularidade única por OS/episódio, datas de referência, significado das contagens de reabertura/reatribuição e atividade cadastral, inclusão de técnico nulo e ausência de duplicações. O mapeamento recebido fornece esquema e descrições, não DDL nem amostras. **Nenhum SQL acima foi executado contra o workspace.**
2. Confirmar que `media_tarefas_por_os` usa todas as OS criadas no dia; caso contrário OS-14 requer contagens próprias na gold. Expor numerador e denominador de OS-15 na gold e decidir o tratamento das tarefas inativas.
3. Verificar que `recorrencia_episodios` foi construída com janela fixa de 24 h ancorada no primeiro registro e recorrência em até 30 dias entre inícios sucessivos, usando histórico anterior ao período consultado. Os limites de 24 h e 30 dias são propostas de negócio ainda não validadas.
4. Tratar datas/timestamps no horário de negócio `America/Sao_Paulo`, sem presumir UTC nos campos `TIMESTAMP`; aplicar recortes de data somente nas tabelas diárias. Para consultar instantes dentro de um dia, usar fonte com timestamp granular, quando disponível.
5. Os agrupamentos por ID retornam **IDs**, pois as tabelas agregadas não expõem os respectivos nomes. Não inventar rótulos. Verificar cobertura de nulos e mostrar numerador/denominador nas taxas e quantidade válida nas médias.
