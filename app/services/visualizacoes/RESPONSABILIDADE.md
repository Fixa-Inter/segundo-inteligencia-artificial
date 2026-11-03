# Responsabilidade: app/services/visualizacoes

## Objetivo do módulo

Definir/executar 27 análises e liberar dados aprovados.

## O que deve ser armazenado aqui

Catálogo, validação, SQL, normalização, estatísticas, captura, aprovação e publicação.

## Comportamento e limites atuais

Catálogo canônico em catalogo.py, exposto pelo __init__.py sem lógica de montagem na fachada. Seis fontes preservam as 27 análises. Publicação exige captura real, aprovação vinculada e plataforma/perfil autorizados.

Módulo pai: [app/services](../RESPONSABILIDADE.md).

## Funcionalidades disponíveis e arquivos

O catálogo registra os recursos existentes. Funções assíncronas usam `await`; ferramentas LangChain devem receber o contexto injetado. Símbolos com `_` são detalhes internos, cuja assinatura e regras devem ser conferidas antes de reutilizar.

### [__init__.py](__init__.py)

Interface do pacote: reúne importações públicas e recursos descritos abaixo.

- Auxiliares internos (reutilização deve preservar o contexto deste arquivo): `__getattr__`, `__dir__`.
- Constantes, aliases e estado de módulo: `_EXPORTACOES`.
- Importações/reexportações existentes: `from app.core.interfaces import resolver_exportacao as _resolver_exportacao`.

Exportações e proprietários (carregados sob demanda):

- `ANALISES` → `.catalogo` (`ANALISES`).
- `ANALISES_CATALOGO` → `.catalogo` (`ANALISES`).
- `ANALISES_IMPLEMENTADAS_OCORRENCIA` → `.ocorrencia` (`ANALISES_IMPLEMENTADAS`).
- `ANALISES_IMPLEMENTADAS_OS_ATUAL` → `.os_atual` (`ANALISES_IMPLEMENTADAS`).
- `ANALISES_IMPLEMENTADAS_OS_CONCLUSAO` → `.os_conclusao` (`ANALISES_IMPLEMENTADAS`).
- `ANALISES_IMPLEMENTADAS_OS_CRIACAO` → `.os_criacao` (`ANALISES_IMPLEMENTADAS`).
- `ANALISES_IMPLEMENTADAS_RECORRENCIA` → `.recorrencia` (`ANALISES_IMPLEMENTADAS`).
- `ANALISES_IMPLEMENTADAS_SOLICITACAO` → `.solicitacao` (`ANALISES_IMPLEMENTADAS`).
- `ANALISES_OCORRENCIA` → `.ocorrencia` (`ANALISES`).
- `ANALISES_OS_ATUAL` → `.os_atual` (`ANALISES`).
- `ANALISES_OS_CONCLUSAO` → `.os_conclusao` (`ANALISES`).
- `ANALISES_OS_CRIACAO` → `.os_criacao` (`ANALISES`).
- `ANALISES_RECORRENCIA` → `.recorrencia` (`ANALISES`).
- `ANALISES_SOLICITACAO` → `.solicitacao` (`ANALISES`).
- `Analise` → `app.schemas.visualizacao` (`Analise`).
- `CapturaExecucaoVisualizacao` → `.captura` (`CapturaExecucaoVisualizacao`).
- `ErroRespostaDatabricks` → `.normalizacao` (`ErroRespostaDatabricks`).
- `FILTROS_OCORRENCIA` → `.ocorrencia` (`FILTROS`).
- `FILTROS_OS_ATUAL` → `.os_atual` (`FILTROS`).
- `FILTROS_OS_CONCLUSAO` → `.os_conclusao` (`FILTROS`).
- `FILTROS_OS_CRIACAO` → `.os_criacao` (`FILTROS`).
- `FILTROS_POR_FONTE` → `.catalogo` (`FILTROS_POR_FONTE`).
- `FILTROS_RECORRENCIA` → `.recorrencia` (`FILTROS`).
- `FILTROS_SOLICITACAO` → `.solicitacao` (`FILTROS`).
- `FONTES` → `.catalogo` (`FONTES`).
- `FONTE_OCORRENCIA` → `.ocorrencia` (`FONTE`).
- `FONTE_OS_ATUAL` → `.os_atual` (`FONTE`).
- `FONTE_OS_CONCLUSAO` → `.os_conclusao` (`FONTE`).
- `FONTE_OS_CRIACAO` → `.os_criacao` (`FONTE`).
- `FONTE_RECORRENCIA` → `.recorrencia` (`FONTE`).
- `FONTE_SOLICITACAO` → `.solicitacao` (`FONTE`).
- `Fonte` → `app.schemas.visualizacao` (`Fonte`).
- `LimiteBoxplotExcedido` → `.boxplots` (`LimiteBoxplotExcedido`).
- `LimiteVisualizacaoExcedido` → `.publicacao` (`LimiteVisualizacaoExcedido`).
- `MAXIMO_BYTES_CONVERSA_COM_VISUALIZACAO` → `.publicacao` (`MAXIMO_BYTES_CONVERSA_COM_VISUALIZACAO`).
- `MAXIMO_BYTES_VISUALIZACAO` → `.publicacao` (`MAXIMO_BYTES_VISUALIZACAO`).
- `MAXIMO_CONSULTAS_POR_EXECUCAO` → `.limites` (`MAXIMO_CONSULTAS_POR_EXECUCAO`).
- `MAXIMO_DIAS_PERIODO` → `.limites` (`MAXIMO_DIAS_PERIODO`).
- `MAXIMO_EXTREMOS_POR_GRAFICO` → `.limites` (`MAXIMO_EXTREMOS_POR_GRAFICO`).
- `MAXIMO_EXTREMOS_POR_GRUPO` → `.limites` (`MAXIMO_EXTREMOS_POR_GRUPO`).
- `MAXIMO_GRUPOS` → `.limites` (`MAXIMO_GRUPOS`).
- `MAXIMO_INTERVALOS_HISTOGRAMA` → `.limites` (`MAXIMO_INTERVALOS_HISTOGRAMA`).
- `MAXIMO_PONTOS_SERIE` → `.limites` (`MAXIMO_PONTOS_SERIE`).
- `MAXIMO_VALORES_POR_FILTRO` → `.validacao` (`MAXIMO_VALORES_POR_FILTRO`).
- `MENSAGENS` → `app.core.respostas` (`MENSAGENS`).
- `MINIMO_REGISTROS_BOXPLOT` → `.resumos` (`MINIMO_REGISTROS_BOXPLOT`).
- `PERFIS_VISUALIZACOES` → `.catalogo` (`PERFIS_VISUALIZACOES`).
- `_DOMINIOS` → `.catalogo` (`_DOMINIOS`).
- `calendario_consulta` → `.temporais` (`calendario_consulta`).
- `campo` → `.normalizacao` (`campo`).
- `construir_histograma` → `.histogramas` (`construir_histograma`).
- `consultar_OCORRENCIA` → `.ocorrencia` (`consultar`).
- `consultar_OS_ATUAL` → `.os_atual` (`consultar`).
- `consultar_OS_CONCLUSAO` → `.os_conclusao` (`consultar`).
- `consultar_OS_CRIACAO` → `.os_criacao` (`consultar`).
- `consultar_RECORRENCIA` → `.recorrencia` (`consultar`).
- `consultar_SOLICITACAO` → `.solicitacao` (`consultar`).
- `consultar_agregado` → `.consultas` (`consultar_agregado`).
- `contexto_julgamento` → `.aprovacao` (`contexto_julgamento`).
- `criar_aprovacao` → `.aprovacao` (`criar_aprovacao`).
- `expressao_periodo_sql` → `.temporais` (`expressao_periodo_sql`).
- `grupo` → `.normalizacao` (`grupo`).
- `inicio_periodo` → `.temporais` (`inicio_periodo`).
- `inteiro` → `.normalizacao` (`inteiro`).
- `liberar_visualizacao` → `.aprovacao` (`liberar_visualizacao`).
- `montar_sql_boxplot` → `.boxplots` (`montar_sql_boxplot`).
- `montar_sql_histograma` → `.histogramas` (`montar_sql_histograma`).
- `normalizar_boxplot` → `.boxplots` (`normalizar_boxplot`).
- `numero` → `.normalizacao` (`numero`).
- `obter_analise` → `.catalogo` (`obter_analise`).
- `ocorrencia` → `.ocorrencia` (submódulo).
- `os_atual` → `.os_atual` (submódulo).
- `os_conclusao` → `.os_conclusao` (submódulo).
- `os_criacao` → `.os_criacao` (submódulo).
- `possui_visualizacao` → `.aprovacao` (`possui_visualizacao`).
- `proximo_periodo` → `.temporais` (`proximo_periodo`).
- `publicar_visualizacao` → `.publicacao` (`publicar_visualizacao`).
- `recorrencia` → `.recorrencia` (submódulo).
- `resumir_grupo_pequeno` → `.resumos` (`resumir_grupo_pequeno`).
- `solicitacao` → `.solicitacao` (submódulo).
- `validar_argumentos_analise` → `.validacao` (`validar_argumentos_analise`).
- `validar_candidata` → `.aprovacao` (`validar_candidata`).
- `validar_limites_resultado` → `.limites` (`validar_limites_resultado`).
- `validar_periodo_consulta` → `.limites` (`validar_periodo_consulta`).
- `validar_resultado_consulta` → `.validacao` (`validar_resultado_consulta`).
- `validar_visualizacao_publica` → `.publicacao` (`validar_visualizacao_publica`).

### [aprovacao.py](aprovacao.py)

Conferência da captura e vínculo entre julgamento e liberação da visualização.

- `possui_visualizacao(estado) -> bool`: Detecta registros/seleção de visualização presentes no estado.
- `validar_candidata(estado, contexto) -> ConsultaVisualizacaoCapturada | None`: Revalida os registros do servidor e a seleção, sem consultar bancos ou modelos.
- `contexto_julgamento(estado, candidata, *, etapa='juiz') -> dict`: Envia o dado selecionado uma vez, sem identidade do usuário, sessão ou turno.
- `criar_aprovacao(candidata, status, texto) -> dict`: Calcula vínculo SHA-256 entre captura, status e texto avaliado.
- `liberar_visualizacao(estado, contexto) -> dict | None`: Revalida candidata/contexto e confere aprovação antes de liberar dados.
- Auxiliares internos (reutilização deve preservar o contexto deste arquivo): `_json`.

### [boxplots.py](boxplots.py)

SQL dos boxplots: população completa, resumos e extremos limitados.

- Classe `LimiteBoxplotExcedido` (`ValueError`): O conjunto completo de grupos não cabe no gráfico autorizado.
- `montar_sql_boxplot(analise: Analise, condicoes: list[str])`: Compõe SQL de estatísticas da população e seleção limitada dos extremos.
- `normalizar_boxplot(analise, linhas, filtros_permitidos, unidade_id)`: Valida estatísticas, cobertura e extremos e compõe boxplot/resumo/grupo sem base.

### [captura.py](captura.py)

Captura de retornos reais das tools, isolada por execução do especialista.

- Classe `CapturaExecucaoVisualizacao`.
  Campos/atributos declarados: `usuario_id: int`, `sessao_id: str`, `turno_id: str`, `ids_anteriores: frozenset[str]`, `execucao_id: str`, `_registros: list[ConsultaVisualizacaoCapturada]`, `_invalida: bool`.
  Métodos/validadores: `registrar(self, contexto, chamada_id, ferramenta, consulta, unidade_id, resultado)`; `registros(self) -> list[dict]`; `selecionar(self, referencia, status) -> dict`.

### [catalogo.py](catalogo.py)

Seleção das análises cujas regras são definidas pelos serviços de domínio.

- `obter_analise(analise_id: str, *, fonte_id: str | None=None) -> Analise`: Seleciona uma análise conhecida, opcionalmente restrita à fonte de uma tool.
- Auxiliares internos (reutilização deve preservar o contexto deste arquivo): `_reunir_analises`.
- Constantes, aliases e estado de módulo: `PERFIS_VISUALIZACOES`, `_DOMINIOS`, `FONTES: Mapping[str, Fonte]`, `FILTROS_POR_FONTE: Mapping[str, Mapping[str, str]]`, `ANALISES: Mapping[str, Analise]`.

### [consultas.py](consultas.py)

Execução compartilhada de agregados e séries temporais das fontes aprovadas.

- `async consultar_agregado(consulta: ConsultaVisualizacaoPeriodo | ConsultaVisualizacaoSnapshot, *, unidade_id: int, analises: tuple[Analise, ...], filtros_permitidos: Mapping[str, str], implementadas: frozenset[str]) -> ResultadoConsultaVisualizacao`: Instrumenta execução analítica e delega validação, SQL, normalização e limites.
- Auxiliares internos (reutilização deve preservar o contexto deste arquivo): `_LimiteSerieExcedido`, `_erro`, `_montar_escopo`, `_montar_sql`, `_data`, `_medida`, `_instante`, `_categorias`, `_serie_temporal`, `_metadados`, `_base_total`, `_histograma`, `_consultar_agregado`.
- Constantes, aliases e estado de módulo: `registrador`.

### [histogramas.py](histogramas.py)

Intervalos e agregação completa dos histogramas aprovados.

- `montar_sql_histograma(analise: Analise, condicoes: list[str])`: Retorna uma linha de contagens; não limita nem transporta observações.
- `construir_histograma(minimo, maximo, frequencias, quantidade)`: Usa os mesmos limites do SQL, sem arredondar observações ou fronteiras.
- Auxiliares internos (reutilização deve preservar o contexto deste arquivo): `_limite_sql`.

### [limites.py](limites.py)

Limites operacionais das análises; não corta resultados silenciosamente.

- `validar_periodo_consulta(periodo: PeriodoVisualizacao) -> None`: Rejeita período que excede o máximo permitido da consulta.
- `validar_limites_resultado(dados: DadosVisualizacao) -> None`: Valida o resultado completo, incluindo pontos de lacunas e resumos.
- Constantes, aliases e estado de módulo: `MAXIMO_DIAS_PERIODO`, `MAXIMO_GRUPOS`, `MAXIMO_PONTOS_SERIE`, `MAXIMO_INTERVALOS_HISTOGRAMA`, `MAXIMO_EXTREMOS_POR_GRUPO`, `MAXIMO_EXTREMOS_POR_GRAFICO`, `MAXIMO_CONSULTAS_POR_EXECUCAO`.

### [normalizacao.py](normalizacao.py)

Normalização estrita dos valores e dimensões publicados pelo Databricks.

- Classe `ErroRespostaDatabricks` (`RuntimeError`): Resultado incompatível com a consulta executada; não é erro do usuário.
- `campo(linha, campo)`: Exige coluna esperada na linha retornada pelo Databricks.
- `inteiro(valor, *, nao_negativo=True)`: Normaliza inteiro estritamente e verifica sinal quando exigido.
- `numero(valor)`: Normaliza valor numérico finito sem aceitar coerções incompatíveis.
- `grupo(analise, linha, filtros_permitidos, *, temporal=False)`: Normaliza dimensões autorizadas preservando IDs textuais e valores nulos.

### [ocorrencia.py](ocorrencia.py)

Regras e consultas disponíveis de visualização para ocorrencia.

- `async consultar(consulta: ConsultaVisualizacaoPeriodo | ConsultaVisualizacaoSnapshot, *, unidade_id: int) -> ResultadoConsultaVisualizacao`: Consulta apenas análises implementadas desta fonte e da unidade recebida do servidor.
- Constantes, aliases e estado de módulo: `FONTE`, `FILTROS`, `ANALISES: tuple[Analise, ...]`, `ANALISES_IMPLEMENTADAS`.

### [os_atual.py](os_atual.py)

Regras e consultas disponíveis de visualização para os_atual.

- `async consultar(consulta: ConsultaVisualizacaoPeriodo | ConsultaVisualizacaoSnapshot, *, unidade_id: int) -> ResultadoConsultaVisualizacao`: Consulta apenas análises implementadas desta fonte e da unidade recebida do servidor.
- Constantes, aliases e estado de módulo: `FONTE`, `FILTROS`, `ANALISES: tuple[Analise, ...]`, `ANALISES_IMPLEMENTADAS`.

### [os_conclusao.py](os_conclusao.py)

Regras e consultas disponíveis de visualização para os_conclusao.

- `async consultar(consulta: ConsultaVisualizacaoPeriodo | ConsultaVisualizacaoSnapshot, *, unidade_id: int) -> ResultadoConsultaVisualizacao`: Consulta apenas análises implementadas desta fonte e da unidade recebida do servidor.
- Constantes, aliases e estado de módulo: `FONTE`, `FILTROS`, `ANALISES: tuple[Analise, ...]`, `ANALISES_IMPLEMENTADAS`.

### [os_criacao.py](os_criacao.py)

Regras e consultas disponíveis de visualização para os_criacao.

- `async consultar(consulta: ConsultaVisualizacaoPeriodo | ConsultaVisualizacaoSnapshot, *, unidade_id: int) -> ResultadoConsultaVisualizacao`: Consulta apenas análises implementadas desta fonte e da unidade recebida do servidor.
- Constantes, aliases e estado de módulo: `FONTE`, `FILTROS`, `ANALISES: tuple[Analise, ...]`, `ANALISES_IMPLEMENTADAS`.

### [publicacao.py](publicacao.py)

Projeção do resultado aprovado para o contrato público e sua validação.

- Classe `LimiteVisualizacaoExcedido` (`ValueError`).
- `validar_visualizacao_publica(dados) -> VisualizacaoPublica`: Valida contrato, limites analíticos e tamanho UTF-8 do payload público.
- `publicar_visualizacao(estado, contexto) -> VisualizacaoPublica | None`: Projeta captura aprovada para payload público, protegendo texto e verificando limites.
- Constantes, aliases e estado de módulo: `MAXIMO_BYTES_VISUALIZACAO`, `MAXIMO_BYTES_CONVERSA_COM_VISUALIZACAO`.

### [recorrencia.py](recorrencia.py)

Regras e consultas disponíveis de visualização para recorrencia.

- `async consultar(consulta: ConsultaVisualizacaoPeriodo | ConsultaVisualizacaoSnapshot, *, unidade_id: int) -> ResultadoConsultaVisualizacao`: Consulta apenas análises implementadas desta fonte e da unidade recebida do servidor.
- Constantes, aliases e estado de módulo: `FONTE`, `FILTROS`, `ANALISES: tuple[Analise, ...]`, `ANALISES_IMPLEMENTADAS`.

### [resumos.py](resumos.py)

Resumo dos grupos pequenos das análises de boxplot, sem acesso a bancos.

- `resumir_grupo_pequeno(analise: Analise, *, grupo: Mapping[str, int | str | None], valores: Sequence[int | float | None]) -> ResumoGrupoPequeno | None`: Resume até quatro tempos não nulos; sem observações, não fabrica resumo.
- Constantes, aliases e estado de módulo: `MINIMO_REGISTROS_BOXPLOT`.

### [solicitacao.py](solicitacao.py)

Regras e consultas disponíveis de visualização para solicitacao.

- `async consultar(consulta: ConsultaVisualizacaoPeriodo | ConsultaVisualizacaoSnapshot, *, unidade_id: int) -> ResultadoConsultaVisualizacao`: Consulta apenas análises implementadas desta fonte e da unidade recebida do servidor.
- Constantes, aliases e estado de módulo: `FONTE`, `FILTROS`, `ANALISES: tuple[Analise, ...]`, `ANALISES_IMPLEMENTADAS`.

### [temporais.py](temporais.py)

Calendários e expressões SQL das granularidades temporais aprovadas.

- `inicio_periodo(referencia: date, granularidade: str) -> date`: Obtém início do dia, semana ou mês da referência.
- `proximo_periodo(referencia: date, granularidade: str) -> date`: Avança uma unidade da granularidade temporal autorizada.
- `expressao_periodo_sql(campo: str, granularidade: str) -> str`: Campo canônico do serviço; unidade SQL selecionada de uma lista fechada.
- `calendario_consulta(periodo: PeriodoVisualizacao, granularidade: str) -> dict[date, PeriodoSerieTemporal]`: Preserva o recorte solicitado, inclusive nas extremidades incompletas.

### [validacao.py](validacao.py)

Validação compartilhada por serviços analíticos e argumentos das tools.

- `validar_argumentos_analise(consulta: ConsultaVisualizacaoPeriodo | ConsultaVisualizacaoSnapshot, analise: Analise, filtros_permitidos: Mapping[str, str]) -> None`: Restringe campos e valores; não substitui a autorização do usuário.
- `validar_resultado_consulta(consulta: ConsultaVisualizacaoPeriodo | ConsultaVisualizacaoSnapshot, analise: Analise, unidade_id: int, resultado: ResultadoConsultaVisualizacao | dict) -> ResultadoConsultaVisualizacao`: Revalida o retorno e sua correspondência com a consulta autorizada.
- Constantes, aliases e estado de módulo: `MAXIMO_VALORES_POR_FILTRO`.

## Regras de reutilização

- `ANALISES`, `FONTES`, `FILTROS_POR_FONTE` e `obter_analise()` são o catálogo canônico. SQL, fonte, dimensões e população não são definidos pelo modelo.
- Cada um dos seis módulos de domínio declara `FONTE`, `FILTROS`, `ANALISES`, `ANALISES_IMPLEMENTADAS` e `consultar()`, delegando execução a `consultas.consultar_agregado()`.
- Período usa início inclusivo e fim exclusivo, com limite de 366 dias. Séries usam dia/semana/mês; snapshot de OS atual não recebe período.
- `limites.py` limita 50 grupos, 500 pontos de série, dez intervalos de histograma e extremos por grupo/gráfico. Não corta grupos silenciosamente para simular resultado completo.
- `histogramas.py` agrega toda a população no SQL. `boxplots.py` calcula quartis/bigodes e limita somente pontos extremos publicados, preservando estatísticas/contagens. Grupos de um a quatro valores usam `resumos.py`; grupos sem elegíveis não ganham estatísticas inventadas.
- `normalizacao.py` distingue null, zero, inteiros, decimais e IDs textuais. `temporais.py` representa também períodos parciais sem ampliar o recorte solicitado.
- `CapturaExecucaoVisualizacao` vincula resultado real à chamada, execução, turno, sessão, usuário e unidade. `aprovacao.py` verifica essa origem e vincula o hash ao conteúdo/texto julgado.
- `publicacao.py` projeta `VisualizacaoPublica`, revalida limites e restringe payload a 256 KiB; a persistência limita conversa com visualizações a 8 MiB. O histórico devolve o mesmo payload salvo, sem recalcular.

## Análises disponíveis por fonte

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

## Dependências internas observadas

Importações existentes nos arquivos desta pasta; não representam uma arquitetura desejada nem autorização para ampliar escopos.

- [app/core](../../core/RESPONSABILIDADE.md).
- [app/core/apresentacao](../../core/apresentacao/RESPONSABILIDADE.md).
- [app/guardrails](../../guardrails/RESPONSABILIDADE.md).
- [app/observability](../../observability/RESPONSABILIDADE.md).
- [app/schemas](../../schemas/RESPONSABILIDADE.md).
- [app/services/indicadores/gerais](../indicadores/gerais/RESPONSABILIDADE.md).
