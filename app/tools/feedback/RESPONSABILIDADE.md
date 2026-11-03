# Responsabilidade: app/tools/feedback

## Objetivo do módulo

Preparar registro e listar feedback próprio.

## O que deve ser armazenado aqui

Ferramentas de comentário/ideia central e consulta sem identidade editável.

## Comportamento e limites atuais

criar_nome_feedback prepara operação; gravação ocorre após aprovação. listar_meus_feedbacks consulta apenas o usuário autenticado.

Módulo pai: [app/tools](../RESPONSABILIDADE.md).

## Funcionalidades disponíveis e arquivos

O catálogo registra os recursos existentes. Funções assíncronas usam `await`; ferramentas LangChain devem receber o contexto injetado. Símbolos com `_` são detalhes internos, cuja assinatura e regras devem ser conferidas antes de reutilizar.

### [__init__.py](__init__.py)

Interface do pacote: reúne importações públicas e recursos descritos abaixo.

- Auxiliares internos (reutilização deve preservar o contexto deste arquivo): `__getattr__`, `__dir__`.
- Constantes, aliases e estado de módulo: `_EXPORTACOES`.
- Importações/reexportações existentes: `from app.core.interfaces import resolver_exportacao as _resolver_exportacao`.

Exportações e proprietários (carregados sob demanda):

- `criar_nome_feedback` → `.criarFeedback` (`criar_nome_feedback`).
- `listar_meus_feedbacks` → `.listarFeedbacks` (`listar_meus_feedbacks`).

### [criarFeedback.py](criarFeedback.py)

Recursos deste arquivo: Prepara feedback para aprovação interna. Ainda não grava no PostgreSQL.

- `async criar_nome_feedback(comentario: str, ideia_central: str, runtime: ToolRuntime) -> dict`: Prepara feedback para aprovação interna. Ainda não grava no PostgreSQL.
- Auxiliares internos (reutilização deve preservar o contexto deste arquivo): `_ArgumentosCriarFeedback`.
  `_ArgumentosCriarFeedback`: `comentario: str`, `ideia_central: str`.

### [listarFeedbacks.py](listarFeedbacks.py)

Ferramenta de leitura sem argumentos de identidade fornecidos pelo modelo.

- `async listar_meus_feedbacks(runtime: ToolRuntime) -> dict`: Lista os feedbacks do usuário autenticado, do mais recente ao mais antigo.

## Dependências internas observadas

Importações existentes nos arquivos desta pasta; não representam uma arquitetura desejada nem autorização para ampliar escopos.

- [app/core](../../core/RESPONSABILIDADE.md).
- [app/schemas](../../schemas/RESPONSABILIDADE.md).
- [app/services](../../services/RESPONSABILIDADE.md).
- [app/services/feedback](../../services/feedback/RESPONSABILIDADE.md).
- [app/tools](../RESPONSABILIDADE.md).
