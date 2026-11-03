# Responsabilidade: app/services/indicadores

## Objetivo do módulo

Consultar indicadores gerenciais no Databricks.

## O que deve ser armazenado aqui

SQL parametrizado e interpretação de métricas de OS, solicitações e ocorrências.

## Comportamento e limites atuais

Usa consultas e validação comuns de gerais/consultas.py, mantendo SQL, população e políticas por domínio. Unidade vem do servidor. Distingue criação, conclusão e snapshot; média de tarefas continua indisponível.

Módulo pai: [app/services](../RESPONSABILIDADE.md).

## Submódulos

| Pasta | Responsabilidade |
| --- | --- |
| [gerais](gerais/RESPONSABILIDADE.md) | Executar consultas analíticas e validar escopo comum. |

## Funcionalidades disponíveis e arquivos

O catálogo registra os recursos existentes. Funções assíncronas usam `await`; ferramentas LangChain devem receber o contexto injetado. Símbolos com `_` são detalhes internos, cuja assinatura e regras devem ser conferidas antes de reutilizar.

### [__init__.py](__init__.py)

Interface do pacote: reúne importações públicas e recursos descritos abaixo.

- Auxiliares internos (reutilização deve preservar o contexto deste arquivo): `__getattr__`, `__dir__`.
- Constantes, aliases e estado de módulo: `_EXPORTACOES`.
- Importações/reexportações existentes: `from app.core.interfaces import resolver_exportacao as _resolver_exportacao`.

Exportações e proprietários (carregados sob demanda):

- `gerais` → `.gerais` (submódulo).
- `obter_carga_ativa_tecnicos` → `.ordem_servico` (`obter_carga_ativa_tecnicos`).
- `obter_media_tarefas_por_os` → `.ordem_servico` (`obter_media_tarefas_por_os`).
- `obter_ocorrencias_ativas` → `.ocorrencia` (`obter_ocorrencias_ativas`).
- `obter_ocorrencias_por_categoria_equipamento` → `.ocorrencia` (`obter_ocorrencias_por_categoria_equipamento`).
- `obter_ocorrencias_por_categoria_problema` → `.ocorrencia` (`obter_ocorrencias_por_categoria_problema`).
- `obter_ocorrencias_por_local` → `.ocorrencia` (`obter_ocorrencias_por_local`).
- `obter_ocorrencias_por_periodo` → `.ocorrencia` (`obter_ocorrencias_por_periodo`).
- `obter_ocorrencias_por_prioridade` → `.ocorrencia` (`obter_ocorrencias_por_prioridade`).
- `obter_ocorrencias_por_tecnico` → `.ocorrencia` (`obter_ocorrencias_por_tecnico`).
- `obter_ocorrencias_por_unidade` → `.ocorrencia` (`obter_ocorrencias_por_unidade`).
- `obter_os_abertas` → `.ordem_servico` (`obter_os_abertas`).
- `obter_os_atrasadas` → `.ordem_servico` (`obter_os_atrasadas`).
- `obter_os_finalizadas` → `.ordem_servico` (`obter_os_finalizadas`).
- `obter_produtividade_tecnicos` → `.ordem_servico` (`obter_produtividade_tecnicos`).
- `obter_solicitacoes_aprovadas` → `.problema` (`obter_solicitacoes_aprovadas`).
- `obter_solicitacoes_pendentes` → `.problema` (`obter_solicitacoes_pendentes`).
- `obter_solicitacoes_por_categoria_equipamento` → `.problema` (`obter_solicitacoes_por_categoria_equipamento`).
- `obter_solicitacoes_por_local` → `.problema` (`obter_solicitacoes_por_local`).
- `obter_solicitacoes_por_periodo` → `.problema` (`obter_solicitacoes_por_periodo`).
- `obter_solicitacoes_por_unidade` → `.problema` (`obter_solicitacoes_por_unidade`).
- `obter_solicitacoes_reprovadas` → `.problema` (`obter_solicitacoes_reprovadas`).
- `obter_taxa_aprovacao_solicitacoes` → `.problema` (`obter_taxa_aprovacao_solicitacoes`).
- `obter_taxa_atraso_os` → `.ordem_servico` (`obter_taxa_atraso_os`).
- `obter_taxa_conclusao_prazo` → `.ordem_servico` (`obter_taxa_conclusao_prazo`).
- `obter_taxa_conversao_solicitacoes_os` → `.problema` (`obter_taxa_conversao_solicitacoes_os`).
- `obter_taxa_ocorrencias_alta_prioridade` → `.ocorrencia` (`obter_taxa_ocorrencias_alta_prioridade`).
- `obter_taxa_reabertura_os` → `.ordem_servico` (`obter_taxa_reabertura_os`).
- `obter_taxa_reatribuicao_os` → `.ordem_servico` (`obter_taxa_reatribuicao_os`).
- `obter_taxa_recorrencia_local_categoria` → `.problema` (`obter_taxa_recorrencia_local_categoria`).
- `obter_taxa_reprovacao_solicitacoes` → `.problema` (`obter_taxa_reprovacao_solicitacoes`).
- `obter_tempo_medio_espera_os` → `.ordem_servico` (`obter_tempo_medio_espera_os`).
- `obter_tempo_medio_pausado_os` → `.ordem_servico` (`obter_tempo_medio_pausado_os`).
- `obter_tempo_medio_resolucao_os` → `.ordem_servico` (`obter_tempo_medio_resolucao_os`).
- `obter_total_ocorrencias` → `.ocorrencia` (`obter_total_ocorrencias`).
- `obter_total_os` → `.ordem_servico` (`obter_total_os`).
- `obter_total_solicitacoes` → `.problema` (`obter_total_solicitacoes`).
- `ordem_servico` → `.ordem_servico` (submódulo).

### [ocorrencia.py](ocorrencia.py)

Consultas de métricas de ocorrências na camada gold.

- `async obter_total_ocorrencias(inicio: date, fim: date, *, unidade_id: int) -> dict`: Soma ocorrências criadas no período [início, fim).
- `async obter_ocorrencias_por_tecnico(inicio: date, fim: date, *, unidade_id: int) -> dict`: Agrupa ocorrências criadas no período por técnico.
- `async obter_ocorrencias_por_unidade(inicio: date, fim: date, *, unidade_id: int) -> dict`: Retorna apenas a unidade autenticada para as ocorrências do período.
- `async obter_ocorrencias_por_local(inicio: date, fim: date, *, unidade_id: int) -> dict`: Agrupa ocorrências criadas no período por local.
- `async obter_ocorrencias_por_categoria_problema(inicio: date, fim: date, *, unidade_id: int) -> dict`: Agrupa ocorrências por categoria de problema, não de equipamento.
- `async obter_ocorrencias_por_categoria_equipamento(inicio: date, fim: date, *, unidade_id: int) -> dict`: Agrupa ocorrências criadas no período por categoria de equipamento.
- `async obter_ocorrencias_por_prioridade(inicio: date, fim: date, *, unidade_id: int) -> dict`: Agrupa ocorrências por código de prioridade: alta 0, média 1, baixa 2.
- `async obter_ocorrencias_ativas(inicio: date, fim: date, *, unidade_id: int) -> dict`: Soma ocorrências do período aguardando revisão/aprovação do gestor.
- `async obter_taxa_ocorrencias_alta_prioridade(inicio: date, fim: date, *, unidade_id: int) -> dict`: Calcula ocorrências de prioridade zero sobre o total da coorte.
- `async obter_ocorrencias_por_periodo(inicio: date, fim: date, granularidade: str, *, unidade_id: int) -> dict`: Agrupa ocorrências criadas por dia, mês ou ano.
- Auxiliares internos (reutilização deve preservar o contexto deste arquivo): `_consultar`, `_obter_por_dimensao`.
- Constantes, aliases e estado de módulo: `registrador`.

### [ordem_servico.py](ordem_servico.py)

Consultas de métricas e KPIs de ordens de serviço na camada gold.

- `async obter_total_os(inicio: date, fim: date, *, unidade_id: int) -> dict`: Conta OS criadas no período `[início, fim)`.
- `async obter_os_abertas(*, unidade_id: int) -> dict`: Conta OS atualmente abertas (status 1, 2 ou 3), sem filtro de criação.
- `async obter_os_atrasadas(*, unidade_id: int) -> dict`: Conta OS atualmente classificadas como Atrasada (status 1).
- `async obter_taxa_atraso_os(*, unidade_id: int) -> dict`: Calcula a parcela de OS atrasadas entre as OS abertas no snapshot atual.
- `async obter_os_finalizadas(inicio: date, fim: date, *, unidade_id: int) -> dict`: Conta OS atualmente finalizadas, por data de conclusão em `[início, fim)`.
- `async obter_taxa_conclusao_prazo(inicio: date, fim: date, *, unidade_id: int) -> dict`: Calcula a conclusão no prazo entre OS finalizadas elegíveis no período.
- `async obter_tempo_medio_espera_os(inicio: date, fim: date, *, unidade_id: int) -> dict`: Calcula a espera válida até o início das OS criadas no período.
- `async obter_tempo_medio_resolucao_os(inicio: date, fim: date, *, unidade_id: int) -> dict`: Calcula a resolucao valida das OS concluidas no periodo.
- `async obter_tempo_medio_pausado_os(inicio: date, fim: date, *, unidade_id: int) -> dict`: Calcula tempo pausado valido nas OS criadas no periodo, incluindo zero.
- `async obter_taxa_reabertura_os(inicio: date, fim: date, *, unidade_id: int) -> dict`: Calcula parcela da coorte de OS criadas que foi reaberta ao menos uma vez.
- `async obter_taxa_reatribuicao_os(inicio: date, fim: date, *, unidade_id: int) -> dict`: Calcula parcela da coorte de OS criadas com troca de técnico.
- `async obter_carga_ativa_tecnicos(*, unidade_id: int) -> dict`: Consulta carga atual de OS abertas por técnico, sem período de criação.
- `async obter_produtividade_tecnicos(inicio: date, fim: date, *, unidade_id: int) -> dict`: Consulta conclusões no período por técnico atual.
- `async obter_media_tarefas_por_os(inicio: date, fim: date, *, unidade_id: int) -> dict`: Retorna INDICADOR_INDISPONIVEL enquanto faltam contagens necessárias no BI.
- Auxiliares internos (reutilização deve preservar o contexto deste arquivo): `_parametros_periodo`, `_resposta`, `_consultar_linhas`, `_consultar`, `_obter_taxa_coorte`.
- Constantes, aliases e estado de módulo: `registrador`.

### [problema.py](problema.py)

Consultas de métricas e KPIs de solicitações (problemas) na camada gold.

- `async obter_total_solicitacoes(inicio: date, fim: date, *, unidade_id: int) -> dict`: Soma solicitações criadas no período inclusivo/exclusivo informado.
- `async obter_solicitacoes_pendentes(inicio: date, fim: date, *, unidade_id: int) -> dict`: Soma pendências do período conforme a última atualização da unidade.
- `async obter_solicitacoes_aprovadas(inicio: date, fim: date, *, unidade_id: int) -> dict`: Soma aprovações do período conforme a última atualização da unidade.
- `async obter_solicitacoes_reprovadas(inicio: date, fim: date, *, unidade_id: int) -> dict`: Soma reprovações do período conforme a última atualização da unidade.
- `async obter_taxa_aprovacao_solicitacoes(inicio: date, fim: date, *, unidade_id: int) -> dict`: Calcula aprovações sobre todas as solicitações criadas na coorte.
- `async obter_taxa_reprovacao_solicitacoes(inicio: date, fim: date, *, unidade_id: int) -> dict`: Calcula reprovações sobre todas as solicitações criadas na coorte.
- `async obter_taxa_conversao_solicitacoes_os(inicio: date, fim: date, *, unidade_id: int) -> dict`: Calcula a parcela da coorte que gerou uma ou mais ordens de serviço.
- `async obter_solicitacoes_por_unidade(inicio: date, fim: date, *, unidade_id: int) -> dict`: Retorna apenas a unidade autenticada; a tabela não contém seu nome.
- `async obter_solicitacoes_por_local(inicio: date, fim: date, *, unidade_id: int) -> dict`: Agrupa a coorte por local; a gold não contém nome ou tipo do local.
- `async obter_solicitacoes_por_categoria_equipamento(inicio: date, fim: date, *, unidade_id: int) -> dict`: Agrupa a coorte por categoria de equipamento, não por problema.
- `async obter_solicitacoes_por_periodo(inicio: date, fim: date, granularidade: str, *, unidade_id: int) -> dict`: Agrupa a coorte por dia, mês ou ano conforme granularidade informada.
- `async obter_taxa_recorrencia_local_categoria(inicio: date, fim: date, *, unidade_id: int) -> dict`: Calcula recorrência por local/categoria conforme episódios gold prontos.
- Auxiliares internos (reutilização deve preservar o contexto deste arquivo): `_consultar`, `_resposta`, `_obter_soma`, `_obter_taxa`, `_obter_por_dimensao`.
- Constantes, aliases e estado de módulo: `registrador`.

## Semântica das consultas

- Unidade é obrigatória e validada antes da chamada ao warehouse; tools resolvem o vínculo autenticado no servidor.
- Volumes de criação, conclusões e snapshots usam bases temporais próprias. Períodos são `[inicio, fim)` e granularidade dos KPIs é `dia`, `mes` ou `ano`.
- `ordem_servico.py`: total, abertas/atrasadas/taxa atual, finalizadas/prazo, tempos, reabertura/reatribuição, carga/produtividade e resposta explícita de indisponibilidade da média de tarefas.
- `problema.py`: volume/status, aprovação/reprovação/conversão, agrupamentos e recorrência a partir das estruturas gold já calculadas.
- `ocorrencia.py`: volume, agrupamentos, prioridade e pendências de revisão/aprovação. `obter_ocorrencias_ativas()` usa `qtd_ocorrencias_ativas` da gold, sem reconstruir um snapshot de cada dia passado.
- Percentuais, denominadores, cobertura e ausência de base vêm dos serviços. Não recalcular indicadores no texto do agente.

## Dependências internas observadas

Importações existentes nos arquivos desta pasta; não representam uma arquitetura desejada nem autorização para ampliar escopos.

- [app/core](../../core/RESPONSABILIDADE.md).
- [app/services/indicadores/gerais](gerais/RESPONSABILIDADE.md).
