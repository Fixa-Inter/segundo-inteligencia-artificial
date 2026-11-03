# Responsabilidade: app/api/routes

## Objetivo do módulo

Expor chat, sessões, saúde, métricas e classificação.

## O que deve ser armazenado aqui

Handlers HTTP, contratos de resposta e tradução de erros.

## Comportamento e limites atuais

Handlers expõem HTTP e delegam casos de uso. Classificação agora usa services/classificacao_problema.py. Prefixos, contratos, tags e descrições HTTP foram preservados. Chat/histórico usam autenticação; saúde, métricas e classificação preservam suas dependências anteriores.

Módulo pai: [app/api](../RESPONSABILIDADE.md).

## Funcionalidades disponíveis e arquivos

O catálogo registra os recursos existentes. Funções assíncronas usam `await`; ferramentas LangChain devem receber o contexto injetado. Símbolos com `_` são detalhes internos, cuja assinatura e regras devem ser conferidas antes de reutilizar.

### [__init__.py](__init__.py)

Interface do pacote: reúne importações públicas e recursos descritos abaixo.

- Auxiliares internos (reutilização deve preservar o contexto deste arquivo): `__getattr__`, `__dir__`.
- Constantes, aliases e estado de módulo: `_EXPORTACOES`.
- Importações/reexportações existentes: `from app.core.interfaces import resolver_exportacao as _resolver_exportacao`.

Exportações e proprietários (carregados sob demanda):

- `classificar_problema` → `.classificacao_problema` (`classificar_problema`).
- `conversar` → `.chat` (`conversar`).
- `encerrar_conversa` → `.chat` (`encerrar_conversa`).
- `excluir_conversa_historico` → `.sessoes` (`excluir_conversa_historico`).
- `health_check` → `.health` (`health_check`).
- `metrics` → `.metrics` (`metrics`).
- `pegar_conversa_especifica` → `.sessoes` (`pegar_conversa_especifica`).
- `pegar_todas_conversas_usuario` → `.sessoes` (`pegar_todas_conversas_usuario`).
- `router_CHAT` → `.chat` (`router`).
- `router_CLASSIFICACAO_PROBLEMA` → `.classificacao_problema` (`router`).
- `router_HEALTH` → `.health` (`router`).
- `router_METRICS` → `.metrics` (`router`).
- `router_SESSOES` → `.sessoes` (`router`).

### [chat.py](chat.py)

POST /chat processa conversa; DELETE /chat/sessions/{thread_id} encerra a sessão.

- `async conversar(dados: ConversaEntrada, usuario: Annotated[UsuarioContexto, Depends(obter_usuario_atual)]) -> ConversaSaida`: Handler de chat que delega dados e usuário autenticado a processar_chat.
- `async encerrar_conversa(thread_id: IdSessaoCaminho, usuario: Annotated[UsuarioContexto, Depends(obter_usuario_atual)]) -> EncerrarSessaoSaida`: Handler que encerra sessão própria e traduz erro de ID para HTTP 422.
- Constantes, aliases e estado de módulo: `router`.

### [classificacao_problema.py](classificacao_problema.py)

Handler HTTP que delega classificação ao serviço preservando o OpenAPI original.

- `async classificar_problema(classificar_problema: ClassificarProblemaRequest) -> ClassificarProblemaResponse`: Endpoint para classificar um problema com base no título, descrição e categoria do equipamento.
- Constantes, aliases e estado de módulo: `router`.

### [health.py](health.py)

GET /health informa status/nome do serviço; não verifica bancos.

- `async health_check() -> HealthResponse`: Devolve status ok e nome do serviço, sem verificar dependências externas.
- Constantes, aliases e estado de módulo: `router`.

### [metrics.py](metrics.py)

GET /metrics expõe Prometheus, fora do schema público.

- `async metrics() -> Response`: Devolve as métricas agregadas no formato Prometheus.
- Constantes, aliases e estado de módulo: `router`.

### [sessoes.py](sessoes.py)

GET /sessoes, POST /sessoes/conversa e DELETE /sessoes/conversa/{session_id} consultam/ocultam histórico próprio.

- `async pegar_todas_conversas_usuario(usuario: Annotated[UsuarioContexto, Depends(obter_usuario_atual)]) -> TodasConversasSaida`: Consulta e formata histórico próprio, com visualizações somente para perfil permitido.
- `async pegar_conversa_especifica(dados: ConversaEspecificaEntrada, usuario: Annotated[UsuarioContexto, Depends(obter_usuario_atual)]) -> ConversaEspecificaSaida`: Consulta conversa própria por ID ou devolve HTTP 404.
- `async excluir_conversa_historico(session_id: IdSessaoCaminho, usuario: Annotated[UsuarioContexto, Depends(obter_usuario_atual)]) -> ExcluirConversaSaida`: Solicita exclusão lógica de conversa própria ou devolve HTTP 404.
- Auxiliares internos (reutilização deve preservar o contexto deste arquivo): `_traduzir_erro`.
- Constantes, aliases e estado de módulo: `router`.

## Dependências internas observadas

Importações existentes nos arquivos desta pasta; não representam uma arquitetura desejada nem autorização para ampliar escopos.

- [app/api/dependencies](../dependencies/RESPONSABILIDADE.md).
- [app/core](../../core/RESPONSABILIDADE.md).
- [app/observability](../../observability/RESPONSABILIDADE.md).
- [app/schemas](../../schemas/RESPONSABILIDADE.md).
- [app/services](../../services/RESPONSABILIDADE.md).
- [app/services/sessoes](../../services/sessoes/RESPONSABILIDADE.md).
- [app/services/visualizacoes](../../services/visualizacoes/RESPONSABILIDADE.md).
