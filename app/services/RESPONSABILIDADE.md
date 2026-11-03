# Responsabilidade: app/services

## Objetivo do módulo

Implementar casos de uso, consultas e gravações.

## O que deve ser armazenado aqui

Serviços de domínio, chat/sessão e preparação de operações aprováveis.

## Comportamento e limites atuais

Serviços preservam SQL/HTTP e regras específicas dos domínios. Contratos são importados de schemas. Classificação foi retirada do handler HTTP. Projeções puras de operação vêm de core; preparação, hash e execução durável mantêm seus serviços próprios.

Módulo pai: [app](../RESPONSABILIDADE.md).

## Submódulos

| Pasta | Responsabilidade |
| --- | --- |
| [ajuda_geral](ajuda_geral/RESPONSABILIDADE.md) | Consultar registros operacionais e efetivar edições restritas. |
| [eventos](eventos/RESPONSABILIDADE.md) | Enviar cadastro de evento à API FIXA. |
| [feedback](feedback/RESPONSABILIDADE.md) | Gravar e consultar feedback próprio. |
| [gerais](gerais/RESPONSABILIDADE.md) | Oferecer serviços de identidade, unidade e decisão JEV. |
| [indicadores](indicadores/RESPONSABILIDADE.md) | Consultar indicadores gerenciais no Databricks. |
| [ocorrencias](ocorrencias/RESPONSABILIDADE.md) | Consultar, cadastrar e atualizar ocorrências. |
| [ordensServico](ordensServico/RESPONSABILIDADE.md) | Consultar ordens de serviço autorizadas. |
| [sessoes](sessoes/RESPONSABILIDADE.md) | Consultar e ocultar conversas do histórico. |
| [solicitacoes](solicitacoes/RESPONSABILIDADE.md) | Consultar, cadastrar e atualizar solicitações. |
| [tecnicos](tecnicos/RESPONSABILIDADE.md) | Consultar técnicos disponíveis ou com menor carga. |
| [visualizacoes](visualizacoes/RESPONSABILIDADE.md) | Definir/executar 27 análises e liberar dados aprovados. |

## Funcionalidades disponíveis e arquivos

O catálogo registra os recursos existentes. Funções assíncronas usam `await`; ferramentas LangChain devem receber o contexto injetado. Símbolos com `_` são detalhes internos, cuja assinatura e regras devem ser conferidas antes de reutilizar.

### [__init__.py](__init__.py)

Interface do pacote: reúne importações públicas e recursos descritos abaixo.

- Auxiliares internos (reutilização deve preservar o contexto deste arquivo): `__getattr__`, `__dir__`.
- Constantes, aliases e estado de módulo: `_EXPORTACOES`.
- Importações/reexportações existentes: `from app.core.interfaces import resolver_exportacao as _resolver_exportacao`.

Exportações e proprietários (carregados sob demanda):

- `TIPOS` → `.operacoes` (`TIPOS`).
- `ajuda_geral` → `.ajuda_geral` (submódulo).
- `aprovacao_operacoes` → `.operacoes` (`aprovacao_operacoes`).
- `calcular_hash` → `.operacoes` (`calcular_hash`).
- `classificar_problema_dados` → `.classificacao_problema` (`classificar_problema_dados`).
- `eventos` → `.eventos` (submódulo).
- `feedback` → `.feedback` (submódulo).
- `finalizar_sessao_chat` → `.sessao` (`finalizar_sessao_chat`).
- `gerais` → `.gerais` (submódulo).
- `indicadores` → `.indicadores` (submódulo).
- `ocorrencias` → `.ocorrencias` (submódulo).
- `ordensServico` → `.ordensServico` (submódulo).
- `preparar_operacao` → `.operacoes` (`preparar_operacao`).
- `processar_chat` → `.chat` (`processar_chat`).
- `resumo` → `.operacoes` (`resumo`).
- `sessoes` → `.sessoes` (submódulo).
- `solicitacoes` → `.solicitacoes` (submódulo).
- `tecnicos` → `.tecnicos` (submódulo).
- `visualizacoes` → `.visualizacoes` (submódulo).

### [chat.py](chat.py)

Valida sessão, inicia conversa, chama executor e mede duração/resultado/custo por requisição.

- `async processar_chat(dados: ConversaEntrada, usuario: UsuarioContexto) -> ConversaSaida`: Coordena chat e isolamento de métricas de resultado/custo/resoluções por requisição.
- Auxiliares internos (reutilização deve preservar o contexto deste arquivo): `_processar_chat`.

### [classificacao_problema.py](classificacao_problema.py)

Classificação de problemas: regras JEV separadas do transporte HTTP.

- `async classificar_problema_dados(classificar_problema: ClassificarProblemaRequest) -> ClassificarProblemaResponse`: Endpoint para classificar um problema com base no título, descrição e categoria do equipamento.

### [operacoes.py](operacoes.py)

Prepara operação durável e calcula hash para vincular conteúdo e contexto à aprovação.

- `calcular_hash(dados: dict) -> str`: Calcula SHA-256 do JSON canônico dos dados.
- `resumo(documento: dict) -> dict`: Projeta id, tipo e dados do documento durável para o estado do fluxo.
- `async preparar_operacao(contexto: dict, tipo: str, referencia: str, dados: dict) -> dict`: Persiste operação derivada do contexto e a registra para julgamento.
- `aprovacao_operacoes(operacoes: list[dict], contexto: dict) -> dict`: Vincula conjunto de operações ao contexto e ao conteúdo avaliado.
- Constantes, aliases e estado de módulo: `TIPOS`.

### [sessao.py](sessao.py)

Coordena encerramento persistido e remoção do checkpoint LangGraph.

- `async finalizar_sessao_chat(thread_id: str, usuario: UsuarioContexto) -> EncerrarSessaoSaida`: Encerra persistência da sessão própria e remove seu checkpoint quando disponível.

## Dependências internas observadas

Importações existentes nos arquivos desta pasta; não representam uma arquitetura desejada nem autorização para ampliar escopos.

- [app/agents/prompts/especialistas](../agents/prompts/especialistas/RESPONSABILIDADE.md).
- [app/core](../core/RESPONSABILIDADE.md).
- [app/graph](../graph/RESPONSABILIDADE.md).
- [app/memory/persistencia](../memory/persistencia/RESPONSABILIDADE.md).
- [app/memory/persistencia/sessoes](../memory/persistencia/sessoes/RESPONSABILIDADE.md).
- [app/observability](../observability/RESPONSABILIDADE.md).
- [app/schemas](../schemas/RESPONSABILIDADE.md).
- [app/services/gerais](gerais/RESPONSABILIDADE.md).
- [app/services/visualizacoes](visualizacoes/RESPONSABILIDADE.md).
