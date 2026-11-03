# Responsabilidade: app/services/indicadores/gerais

## Objetivo do módulo

Executar consultas analíticas e validar escopo comum.

## O que deve ser armazenado aqui

Statement Execution Databricks, exceções e validação de unidade.

## Comportamento e limites atuais

consultas.py centraliza validação de datas e tratamento de falhas; cada domínio injeta executor/parâmetros. databricks.py aceita SELECT parametrizado, faz polling/chunks e cancela no timeout, usando core/clients. Unidade inválida produz erro estruturado.

Módulo pai: [app/services/indicadores](../RESPONSABILIDADE.md).

## Funcionalidades disponíveis e arquivos

O catálogo registra os recursos existentes. Funções assíncronas usam `await`; ferramentas LangChain devem receber o contexto injetado. Símbolos com `_` são detalhes internos, cuja assinatura e regras devem ser conferidas antes de reutilizar.

### [__init__.py](__init__.py)

Interface do pacote: reúne importações públicas e recursos descritos abaixo.

- Auxiliares internos (reutilização deve preservar o contexto deste arquivo): `__getattr__`, `__dir__`.
- Constantes, aliases e estado de módulo: `_EXPORTACOES`.
- Importações/reexportações existentes: `from app.core.interfaces import resolver_exportacao as _resolver_exportacao`.

Exportações e proprietários (carregados sob demanda):

- `ConfiguracaoDatabricksAusente` → `.databricks` (`ConfiguracaoDatabricksAusente`).
- `ErroConsultaDatabricks` → `.databricks` (`ErroConsultaDatabricks`).
- `ErroDatabricks` → `.databricks` (`ErroDatabricks`).
- `ErroHTTPDatabricks` → `.databricks` (`ErroHTTPDatabricks`).
- `ResultadoDatabricksTruncado` → `.databricks` (`ResultadoDatabricksTruncado`).
- `TimeoutConsultaDatabricks` → `.databricks` (`TimeoutConsultaDatabricks`).
- `consultar_linhas_indicador` → `.consultas` (`consultar_linhas_indicador`).
- `executar_consulta` → `.databricks` (`executar_consulta`).
- `validar_periodo_indicadores` → `.consultas` (`validar_periodo_indicadores`).
- `validar_unidade_id` → `.unidade` (`validar_unidade_id`).

### [consultas.py](consultas.py)

Execução e tratamento comuns dos KPIs; SQL/população ficam em cada domínio.

- `validar_periodo_indicadores(inicio: date, fim: date) -> dict | None`: Valida datas estritas e intervalo [início, fim) usado pelos três domínios.
- `async consultar_linhas_indicador(sql, parametros, *, executor, registrador, tipos_parametros=None)`: Converte falhas/ausência de linhas em status, preservando o executor injetado.

### [databricks.py](databricks.py)

Validação e execução de consultas de indicadores na API Databricks.

- Classe `ErroDatabricks` (`RuntimeError`): Erro base para falhas de configuração ou consulta no Databricks.
- Classe `ConfiguracaoDatabricksAusente` (`ErroDatabricks`): Uma variável necessária para consultar o workspace está ausente.
- Classe `ErroHTTPDatabricks` (`ErroDatabricks`): A API Databricks recusou ou não respondeu à requisição.
- Classe `ErroConsultaDatabricks` (`ErroDatabricks`): O warehouse não conseguiu executar o SQL enviado.
- Classe `TimeoutConsultaDatabricks` (`ErroDatabricks`): A consulta não terminou dentro do tempo limite configurado.
- Classe `ResultadoDatabricksTruncado` (`ErroDatabricks`): O limite de resultado configurado cortou linhas da resposta.
- `async executar_consulta(sql: str, parametros: dict[str, Any] | None=None, *, tipos_parametros: dict[str, str] | None=None, limite_linhas: int=_LIMITE_LINHAS_PADRAO, limite_bytes: int=_LIMITE_BYTES_PADRAO, tempo_limite_segundos: float=_TEMPO_MAXIMO_EXECUCAO_SEGUNDOS) -> list[dict[str, Any]]`: Executa um SELECT parametrizado no warehouse e devolve linhas como dicionários.
- Auxiliares internos (reutilização deve preservar o contexto deste arquivo): `_configuracoes`, `_validar_sql`, `_valor_parametro`, `_parametros_api`, `_dados_erro`, `_linhas_resultado`, `_requisicao_json`, `_cancelar_statement`.
- Constantes, aliases e estado de módulo: `_WAIT_TIMEOUT`, `_TEMPO_MAXIMO_EXECUCAO_SEGUNDOS`, `_INTERVALO_POLL_SEGUNDOS`, `_LIMITE_LINHAS_PADRAO`, `_LIMITE_BYTES_PADRAO`, `_MARCADOR_SQL`.

### [unidade.py](unidade.py)

Validação do escopo obrigatório das consultas de indicadores.

- `validar_unidade_id(unidade_id: int) -> dict | None`: Rejeita IDs inválidos; booleanos não representam uma unidade.

## Dependências internas observadas

Importações existentes nos arquivos desta pasta; não representam uma arquitetura desejada nem autorização para ampliar escopos.

- [app/core](../../../core/RESPONSABILIDADE.md).
- [app/core/apresentacao](../../../core/apresentacao/RESPONSABILIDADE.md).
- [app/core/clients](../../../core/clients/RESPONSABILIDADE.md).
