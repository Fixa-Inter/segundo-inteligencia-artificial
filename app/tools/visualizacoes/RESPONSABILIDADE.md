# Responsabilidade: app/tools/visualizacoes

## Objetivo do módulo

Adaptar seis ferramentas aos serviços canônicos.

## O que deve ser armazenado aqui

Fábrica de tools, filtros, acesso e resolução de unidade.

## Comportamento e limites atuais

registro.py reúne seis ferramentas; fábrica, acesso e filtros mantêm módulos específicos. ArgumentosComRuntime é compartilhado; schemas preservam campos/limites. O agente limita três consultas e bloqueia mobile antes de acessar o warehouse.

Módulo pai: [app/tools](../RESPONSABILIDADE.md).

## Funcionalidades disponíveis e arquivos

O catálogo registra os recursos existentes. Funções assíncronas usam `await`; ferramentas LangChain devem receber o contexto injetado. Símbolos com `_` são detalhes internos, cuja assinatura e regras devem ser conferidas antes de reutilizar.

### [__init__.py](__init__.py)

Interface do pacote: reúne importações públicas e recursos descritos abaixo.

- Auxiliares internos (reutilização deve preservar o contexto deste arquivo): `__getattr__`, `__dir__`.
- Constantes, aliases e estado de módulo: `_EXPORTACOES`.
- Importações/reexportações existentes: `from app.core.interfaces import resolver_exportacao as _resolver_exportacao`.

Exportações e proprietários (carregados sob demanda):

- `FERRAMENTAS_VISUALIZACOES` → `.registro` (`FERRAMENTAS_VISUALIZACOES`).
- `FILTROS_POR_FONTE` → `.filtros` (`FILTROS_POR_FONTE`).
- `consultar_visualizacao_ocorrencia` → `.consultas` (`consultar_visualizacao_ocorrencia`).
- `consultar_visualizacao_os_atual` → `.consultas` (`consultar_visualizacao_os_atual`).
- `consultar_visualizacao_os_conclusao` → `.consultas` (`consultar_visualizacao_os_conclusao`).
- `consultar_visualizacao_os_criacao` → `.consultas` (`consultar_visualizacao_os_criacao`).
- `consultar_visualizacao_recorrencia` → `.consultas` (`consultar_visualizacao_recorrencia`).
- `consultar_visualizacao_solicitacao` → `.consultas` (`consultar_visualizacao_solicitacao`).
- `criar_tool` → `.execucao` (`criar_tool`).
- `resolver_unidade` → `.contexto` (`resolver_unidade`).
- `validar_acesso` → `.contexto` (`validar_acesso`).
- `validar_campos_filtro` → `.filtros` (`validar_campos_filtro`).
- `validar_consulta` → `.filtros` (`validar_consulta`).

### [consultas.py](consultas.py)

Seis tools vinculadas aos serviços de domínio de visualização.

- Constantes, aliases e estado de módulo: `consultar_visualizacao_os_criacao`, `consultar_visualizacao_os_conclusao`, `consultar_visualizacao_os_atual`, `consultar_visualizacao_solicitacao`, `consultar_visualizacao_recorrencia`, `consultar_visualizacao_ocorrencia`.

### [contexto.py](contexto.py)

Adapta a política gerencial existente ao contrato das visualizações.

- `validar_acesso(runtime) -> ResultadoConsultaVisualizacao | None`: Confere acesso gerencial e plataforma autorizada das visualizações.
- `async resolver_unidade(runtime) -> int | ResultadoConsultaVisualizacao`: Resolve unidade autorizada para visualização.

### [execucao.py](execucao.py)

Adaptação de schemas e execução das tools; regras analíticas ficam nos serviços.

- `criar_tool(dominio)`: Vincula uma tool a referências canônicas, sem duplicar o catálogo.
- Auxiliares internos (reutilização deve preservar o contexto deste arquivo): `_RuntimeInjetado`, `_erro_validacao`, `_tratar_validacao`, `_executar`.
- Constantes, aliases e estado de módulo: `registrador`.

### [filtros.py](filtros.py)

Validação dos argumentos das tools, compartilhada com os serviços.

- `validar_campos_filtro(analise_id: str, campos: Iterable[str]) -> None`: Rejeita campos não autorizados; não substitui a autorização do usuário.
- `validar_consulta(consulta: ConsultaVisualizacaoPeriodo | ConsultaVisualizacaoSnapshot, *, fonte_id: str) -> Analise`: Restringe a análise à fonte da tool e reutiliza a validação do serviço.
- Constantes, aliases e estado de módulo: `FILTROS_POR_FONTE`.

### [registro.py](registro.py)

Tools analíticas de visualização e validação dos seus argumentos.

- Constantes, aliases e estado de módulo: `FERRAMENTAS_VISUALIZACOES`.

## Dependências internas observadas

Importações existentes nos arquivos desta pasta; não representam uma arquitetura desejada nem autorização para ampliar escopos.

- [app/core](../../core/RESPONSABILIDADE.md).
- [app/core/apresentacao](../../core/apresentacao/RESPONSABILIDADE.md).
- [app/observability](../../observability/RESPONSABILIDADE.md).
- [app/schemas](../../schemas/RESPONSABILIDADE.md).
- [app/services/visualizacoes](../../services/visualizacoes/RESPONSABILIDADE.md).
- [app/tools](../RESPONSABILIDADE.md).
- [app/tools/metricas_kpis](../metricas_kpis/RESPONSABILIDADE.md).
