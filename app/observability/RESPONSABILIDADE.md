# Responsabilidade: app/observability

## Objetivo do módulo

Instrumentar execução sem exportar conteúdo de conversa em traces.

## O que deve ser armazenado aqui

Métricas Prometheus, contexto de custo, callback de tokens e política de tracing.

## Comportamento e limites atuais

tracing.py desativa LangSmith no processo, nas chamadas diretas e no ASGI. observability na raiz configura os serviços de coleta/apresentação.

Módulo pai: [app](../RESPONSABILIDADE.md).

## Funcionalidades disponíveis e arquivos

O catálogo registra os recursos existentes. Funções assíncronas usam `await`; ferramentas LangChain devem receber o contexto injetado. Símbolos com `_` são detalhes internos, cuja assinatura e regras devem ser conferidas antes de reutilizar.

### [__init__.py](__init__.py)

Interface do pacote: reúne importações públicas e recursos descritos abaixo.

- Auxiliares internos (reutilização deve preservar o contexto deste arquivo): `__getattr__`, `__dir__`.
- Constantes, aliases e estado de módulo: `_EXPORTACOES`.
- Importações/reexportações existentes: `from app.core.interfaces import resolver_exportacao as _resolver_exportacao`.

Exportações e proprietários (carregados sob demanda):

- `BYTES_VISUALIZACAO` → `.metricas` (`BYTES_VISUALIZACAO`).
- `CONSULTAS_VISUALIZACAO` → `.metricas` (`CONSULTAS_VISUALIZACAO`).
- `CUSTO_MODELO_USD` → `.metricas` (`CUSTO_MODELO_USD`).
- `CUSTO_RESOLUCAO_USD` → `.metricas` (`CUSTO_RESOLUCAO_USD`).
- `CUSTO_SEMANAL_ESTIMADO_USD` → `.metricas` (`CUSTO_SEMANAL_ESTIMADO_USD`).
- `DURACAO_CONSULTAS_VISUALIZACAO` → `.metricas` (`DURACAO_CONSULTAS_VISUALIZACAO`).
- `DURACAO_JEV` → `.metricas` (`DURACAO_JEV`).
- `DURACAO_NO_GRAFO` → `.metricas` (`DURACAO_NO_GRAFO`).
- `DURACAO_RESPOSTA_CONVERSA` → `.metricas` (`DURACAO_RESPOSTA_CONVERSA`).
- `EXECUCOES_NO_GRAFO` → `.metricas` (`EXECUCOES_NO_GRAFO`).
- `EXECUCOES_OPERACAO` → `.metricas` (`EXECUCOES_OPERACAO`).
- `MonitorMetricas` → `.metricas` (`MonitorMetricas`).
- `REAIS_POR_DOLAR` → `.metricas` (`REAIS_POR_DOLAR`).
- `REQUISICOES_CONVERSA` → `.metricas` (`REQUISICOES_CONVERSA`).
- `REQUISICOES_JEV` → `.metricas` (`REQUISICOES_JEV`).
- `REQUISICOES_PECHINCHA` → `.metricas` (`REQUISICOES_PECHINCHA`).
- `RESOLUCOES` → `.metricas` (`RESOLUCOES`).
- `ROI_CONFIGURADO` → `.metricas` (`ROI_CONFIGURADO`).
- `SomenteMetricasMiddleware` → `.tracing` (`SomenteMetricasMiddleware`).
- `TOKENS_MODELO` → `.metricas` (`TOKENS_MODELO`).
- `VALOR_ROI_BRL` → `.metricas` (`VALOR_ROI_BRL`).
- `adicionar_resolucao_pendente` → `.metricas` (`adicionar_resolucao_pendente`).
- `configurar_indicadores_cenarios` → `.metricas` (`configurar_indicadores_cenarios`).
- `configurar_somente_metricas` → `.tracing` (`configurar_somente_metricas`).
- `finalizar_resolucoes` → `.metricas` (`finalizar_resolucoes`).
- `gerar_conteudo_prometheus` → `.metricas` (`gerar_conteudo_prometheus`).
- `marcar_falha_requisicao` → `.metricas` (`marcar_falha_requisicao`).
- `obter_custo_requisicao_usd` → `.metricas` (`obter_custo_requisicao_usd`).
- `registrar_operacao` → `.metricas` (`registrar_operacao`).
- `registrar_resolucao` → `.metricas` (`registrar_resolucao`).
- `registrar_uso_modelo` → `.metricas` (`registrar_uso_modelo`).
- `reiniciar_custo_requisicao` → `.metricas` (`reiniciar_custo_requisicao`).
- `reiniciar_resolucoes_pendentes` → `.metricas` (`reiniciar_resolucoes_pendentes`).
- `reiniciar_resultado_requisicao` → `.metricas` (`reiniciar_resultado_requisicao`).
- `requisicao_falhou` → `.metricas` (`requisicao_falhou`).
- `restaurar_custo_requisicao` → `.metricas` (`restaurar_custo_requisicao`).
- `restaurar_resolucoes_pendentes` → `.metricas` (`restaurar_resolucoes_pendentes`).
- `restaurar_resultado_requisicao` → `.metricas` (`restaurar_resultado_requisicao`).
- `somente_metricas` → `.tracing` (`somente_metricas`).

### [metricas.py](metricas.py)

Métricas Prometheus da API e do fluxo multiagente.

- `reiniciar_custo_requisicao() -> object`: Inicializa ContextVar de custo e retorna token de restauração.
- `restaurar_custo_requisicao(token: object) -> None`: Restaura ContextVar de custo pelo token.
- `obter_custo_requisicao_usd() -> float`: Lê custo estimado acumulado no contexto da requisição.
- `reiniciar_resultado_requisicao() -> object`: Inicializa indicador contextual de falha e retorna token.
- `marcar_falha_requisicao() -> None`: Marca falha no contexto da requisição atual.
- `requisicao_falhou() -> bool`: Consulta indicador contextual de falha.
- `restaurar_resultado_requisicao(token: object) -> None`: Restaura indicador de falha pelo token.
- `registrar_uso_modelo(provedor: str, modelo: str, tokens_entrada: int, tokens_saida: int) -> None`: Registra tokens/custo e acumula custo da requisição.
- `registrar_resolucao() -> None`: Contabiliza ocorrência registrada e custo da requisição.
- `reiniciar_resolucoes_pendentes() -> object`: Inicializa contagem contextual de resoluções pendentes.
- `restaurar_resolucoes_pendentes(token: object) -> None`: Restaura contagem contextual de resoluções pelo token.
- `adicionar_resolucao_pendente() -> None`: Acumula resolução para contabilizar ao final do fluxo.
- `finalizar_resolucoes() -> None`: Consolida resoluções pendentes no final do fluxo.
- `registrar_operacao(operacao: str, resultado_operacao: str) -> None`: Incrementa métrica agregada por operação/resultado.
- `configurar_indicadores_cenarios() -> None`: Atualiza projeções de custo semanal e parâmetros de ROI.
- `gerar_conteudo_prometheus() -> bytes`: Serializa métricas do registro Prometheus em bytes.
- Classe `MonitorMetricas` (`BaseCallbackHandler`): Lê tokens devolvidos pelo modelo sem guardar prompts ou respostas.
  Campos/atributos declarados: `run_inline`.
  Métodos/validadores: `on_llm_end(self, response, **kwargs) -> None`; `on_llm_error(self, error, **kwargs) -> None`.
- Auxiliares internos (reutilização deve preservar o contexto deste arquivo): `_preco_modelo`.
- Constantes, aliases e estado de módulo: `REQUISICOES_CONVERSA`, `DURACAO_RESPOSTA_CONVERSA`, `DURACAO_NO_GRAFO`, `EXECUCOES_NO_GRAFO`, `DURACAO_JEV`, `REQUISICOES_JEV`, `REQUISICOES_PECHINCHA`, `TOKENS_MODELO`, `CUSTO_MODELO_USD`, `EXECUCOES_OPERACAO`, `CONSULTAS_VISUALIZACAO`, `DURACAO_CONSULTAS_VISUALIZACAO`, `BYTES_VISUALIZACAO`, `RESOLUCOES`, `CUSTO_RESOLUCAO_USD`, `CUSTO_SEMANAL_ESTIMADO_USD`, `ROI_CONFIGURADO`, `VALOR_ROI_BRL`, `REAIS_POR_DOLAR`, `_CUSTO_REQUISICAO_USD: ContextVar[float]`, `_REQUISICAO_FALHOU: ContextVar[bool]`, `_RESOLUCOES_PENDENTES: ContextVar[int]`.

### [tracing.py](tracing.py)

Política da aplicação: métricas agregadas, sem exportar conteúdo ao LangSmith.

- `configurar_somente_metricas() -> None`: Aplica a política no processo, inclusive sobre flags carregadas do .env.
- `somente_metricas(funcao)`: Impede herdar tracing habilitado em entradas programáticas assíncronas.
- Classe `SomenteMetricasMiddleware`: Aplica a política também ao contexto de cada requisição ASGI.
  Métodos/validadores: `__init__(self, app)`; `__call__(self, scope, receive, send)`.

## Dependências internas observadas

Importações existentes nos arquivos desta pasta; não representam uma arquitetura desejada nem autorização para ampliar escopos.

- [app/core](../core/RESPONSABILIDADE.md).
