# Responsabilidade: app/tools/metricas_kpis

## Objetivo do módulo

Expor 36 ferramentas gerenciais de indicadores.

## O que deve ser armazenado aqui

Wrappers por domínio, schemas de período e autorização/unidade.

## Comportamento e limites atuais

registro.py reúne 36 ferramentas: 14 OS, 12 solicitações e dez ocorrências. O __init__.py só expõe a interface. Argumentos usam runtime compartilhado e unidade resolvida no servidor; granularidade dia/mes/ano.

Módulo pai: [app/tools](../RESPONSABILIDADE.md).

## Funcionalidades disponíveis e arquivos

O catálogo registra os recursos existentes. Funções assíncronas usam `await`; ferramentas LangChain devem receber o contexto injetado. Símbolos com `_` são detalhes internos, cuja assinatura e regras devem ser conferidas antes de reutilizar.

### [__init__.py](__init__.py)

Interface do pacote: reúne importações públicas e recursos descritos abaixo.

- Auxiliares internos (reutilização deve preservar o contexto deste arquivo): `__getattr__`, `__dir__`.
- Constantes, aliases e estado de módulo: `_EXPORTACOES`.
- Importações/reexportações existentes: `from app.core.interfaces import resolver_exportacao as _resolver_exportacao`.

Exportações e proprietários (carregados sob demanda):

- `FERRAMENTAS_INDICADORES` → `.registro` (`FERRAMENTAS_INDICADORES`).
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
- `resolver_unidade_indicadores` → `.contexto` (`resolver_unidade_indicadores`).
- `validar_gestor` → `.contexto` (`validar_gestor`).

### [contexto.py](contexto.py)

Autorização interna das tools de indicadores, sem argumentos do modelo.

- `validar_gestor(runtime: ToolRuntime, *, perfis_permitidos=frozenset({'gestor', 'administrador'})) -> dict | None`: Confere usuário autenticado e perfil gerencial no runtime.
- `async resolver_unidade_indicadores(runtime: ToolRuntime, *, perfis_permitidos=frozenset({'gestor', 'administrador'})) -> int | dict`: Resolve a unidade atual no servidor; nunca aceita IDs da conversa.
- Constantes, aliases e estado de módulo: `registrador`.

### [ocorrencia.py](ocorrencia.py)

Tools gerenciais para métricas de ocorrências.

- `async obter_total_ocorrencias(inicio: date, fim: date, runtime: ToolRuntime) -> dict`: Conta ocorrências criadas em [início, fim) na unidade autenticada.
- `async obter_ocorrencias_por_tecnico(inicio: date, fim: date, runtime: ToolRuntime) -> dict`: Lista o volume de ocorrências criadas por técnico no período.
- `async obter_ocorrencias_por_unidade(inicio: date, fim: date, runtime: ToolRuntime) -> dict`: Retorna o volume de ocorrências do período somente da unidade autenticada.
- `async obter_ocorrencias_por_local(inicio: date, fim: date, runtime: ToolRuntime) -> dict`: Lista o volume de ocorrências criadas por local no período.
- `async obter_ocorrencias_por_categoria_problema(inicio: date, fim: date, runtime: ToolRuntime) -> dict`: Lista ocorrências por categoria de problema no período.
- `async obter_ocorrencias_por_categoria_equipamento(inicio: date, fim: date, runtime: ToolRuntime) -> dict`: Lista ocorrências agrupadas por categoria de equipamento.
- `async obter_ocorrencias_por_prioridade(inicio: date, fim: date, runtime: ToolRuntime) -> dict`: Lista ocorrências por prioridade: alta 0, média 1, baixa 2.
- `async obter_ocorrencias_ativas(inicio: date, fim: date, runtime: ToolRuntime) -> dict`: Conta ocorrências do período aguardando revisão/aprovação do gestor na unidade.
- `async obter_taxa_ocorrencias_alta_prioridade(inicio: date, fim: date, runtime: ToolRuntime) -> dict`: Calcula a parcela de ocorrências com prioridade alta (código 0).
- `async obter_ocorrencias_por_periodo(inicio: date, fim: date, granularidade: Literal['dia', 'mes', 'ano'], runtime: ToolRuntime) -> dict`: Agrupa ocorrências pela data de criação em dia, mês ou ano.
- Auxiliares internos (reutilização deve preservar o contexto deste arquivo): `_ArgumentosPeriodoGranularidade`.
  `_ArgumentosPeriodoGranularidade`: `granularidade: Literal['dia', 'mes', 'ano']`.

### [ordem_servico.py](ordem_servico.py)

Tools gerenciais para métricas e KPIs de ordens de serviço.

- `async obter_total_os(inicio: date, fim: date, runtime: ToolRuntime) -> dict`: Conta ordens de serviço criadas no período `[início, fim)`.
- `async obter_os_abertas(runtime: ToolRuntime) -> dict`: Conta ordens atualmente abertas: atrasadas, pausadas ou em andamento.
- `async obter_os_atrasadas(runtime: ToolRuntime) -> dict`: Conta ordens atualmente no status Atrasada; não filtra por período.
- `async obter_taxa_atraso_os(runtime: ToolRuntime) -> dict`: Calcula a taxa de atraso entre as ordens atualmente abertas.
- `async obter_os_finalizadas(inicio: date, fim: date, runtime: ToolRuntime) -> dict`: Conta ordens atualmente finalizadas por data de conclusão no período `[início, fim)`.
- `async obter_taxa_conclusao_prazo(inicio: date, fim: date, runtime: ToolRuntime) -> dict`: Calcula a taxa no prazo entre as OS concluídas e elegíveis no período `[início, fim)`.
- `async obter_tempo_medio_espera_os(inicio: date, fim: date, runtime: ToolRuntime) -> dict`: Calcula a espera média em minutos das OS criadas no período `[início, fim)`.
- `async obter_tempo_medio_resolucao_os(inicio: date, fim: date, runtime: ToolRuntime) -> dict`: Calcula tempo de resolucao das OS concluidas no periodo [inicio, fim).
- `async obter_tempo_medio_pausado_os(inicio: date, fim: date, runtime: ToolRuntime) -> dict`: Calcula tempo pausado medio das OS criadas no periodo [inicio, fim).
- `async obter_taxa_reabertura_os(inicio: date, fim: date, runtime: ToolRuntime) -> dict`: Calcula parcela da coorte de OS criadas que foi reaberta ao menos uma vez.
- `async obter_taxa_reatribuicao_os(inicio: date, fim: date, runtime: ToolRuntime) -> dict`: Calcula parcela da coorte de OS criadas com troca de técnico.
- `async obter_carga_ativa_tecnicos(runtime: ToolRuntime) -> dict`: Consulta carga atual de OS abertas por técnico, sem período de criação.
- `async obter_produtividade_tecnicos(inicio: date, fim: date, runtime: ToolRuntime) -> dict`: Consulta conclusões no período por técnico atual.
- `async obter_media_tarefas_por_os(inicio: date, fim: date, runtime: ToolRuntime) -> dict`: Retorna INDICADOR_INDISPONIVEL enquanto faltam contagens necessárias no BI.
- Auxiliares internos (reutilização deve preservar o contexto deste arquivo): `_Argumentos`, `_ArgumentosPeriodo`.
  `_ArgumentosPeriodo`: `inicio: date`, `fim: date`.

### [problema.py](problema.py)

Tools gerenciais para métricas e KPIs de problemas/solicitações.

- `async obter_total_solicitacoes(inicio: date, fim: date, runtime: ToolRuntime) -> dict`: Conta solicitações criadas em [início, fim) na unidade autenticada.
- `async obter_solicitacoes_pendentes(inicio: date, fim: date, runtime: ToolRuntime) -> dict`: Conta solicitações do período pendentes na última atualização da unidade.
- `async obter_solicitacoes_aprovadas(inicio: date, fim: date, runtime: ToolRuntime) -> dict`: Conta solicitações do período aprovadas na última atualização da unidade.
- `async obter_solicitacoes_reprovadas(inicio: date, fim: date, runtime: ToolRuntime) -> dict`: Conta solicitações do período reprovadas na última atualização da unidade.
- `async obter_taxa_aprovacao_solicitacoes(inicio: date, fim: date, runtime: ToolRuntime) -> dict`: Calcula aprovações como percentual de toda a demanda criada no período.
- `async obter_taxa_reprovacao_solicitacoes(inicio: date, fim: date, runtime: ToolRuntime) -> dict`: Calcula reprovações como percentual de toda a demanda criada no período.
- `async obter_taxa_conversao_solicitacoes_os(inicio: date, fim: date, runtime: ToolRuntime) -> dict`: Calcula a parcela das solicitações da coorte que gerou OS.
- `async obter_solicitacoes_por_unidade(inicio: date, fim: date, runtime: ToolRuntime) -> dict`: Retorna o volume do período somente da unidade autenticada, sem nome.
- `async obter_solicitacoes_por_local(inicio: date, fim: date, runtime: ToolRuntime) -> dict`: Lista o volume da coorte por local_id; a gold não fornece nomes ou tipos.
- `async obter_solicitacoes_por_categoria_equipamento(inicio: date, fim: date, runtime: ToolRuntime) -> dict`: Lista solicitações por categoria de equipamento, não de problema.
- `async obter_solicitacoes_por_periodo(inicio: date, fim: date, granularidade: Literal['dia', 'mes', 'ano'], runtime: ToolRuntime) -> dict`: Agrupa solicitações por início de dia, mês ou ano.
- `async obter_taxa_recorrencia_local_categoria(inicio: date, fim: date, runtime: ToolRuntime) -> dict`: Consulta recorrência do BI por local/categoria da unidade, pelo início do episódio.
- Auxiliares internos (reutilização deve preservar o contexto deste arquivo): `_ArgumentosPeriodoGranularidade`.
  `_ArgumentosPeriodoGranularidade`: `granularidade: Literal['dia', 'mes', 'ano']`.

### [registro.py](registro.py)

Tools de métricas e KPIs para o agente de indicadores.

- Constantes, aliases e estado de módulo: `FERRAMENTAS_INDICADORES`.

## Dependências internas observadas

Importações existentes nos arquivos desta pasta; não representam uma arquitetura desejada nem autorização para ampliar escopos.

- [app/core](../../core/RESPONSABILIDADE.md).
- [app/schemas](../../schemas/RESPONSABILIDADE.md).
- [app/services/gerais](../../services/gerais/RESPONSABILIDADE.md).
- [app/services/indicadores](../../services/indicadores/RESPONSABILIDADE.md).
- [app/services/indicadores/gerais](../../services/indicadores/gerais/RESPONSABILIDADE.md).
- [app/tools](../RESPONSABILIDADE.md).
