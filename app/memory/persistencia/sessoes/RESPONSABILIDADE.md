# Responsabilidade: app/memory/persistencia/sessoes

## Objetivo do módulo

Iniciar e encerrar sessões persistidas.

## O que deve ser armazenado aqui

Criação de documento, encerramento, resumo e indexação vetorial.

## Comportamento e limites atuais

__init__.py carrega funções sob demanda. Encerrar pode gerar título/resumo e indexar Qdrant. services/sessao.py coordena limpeza do checkpoint.

Módulo pai: [app/memory/persistencia](../RESPONSABILIDADE.md).

## Funcionalidades disponíveis e arquivos

O catálogo registra os recursos existentes. Funções assíncronas usam `await`; ferramentas LangChain devem receber o contexto injetado. Símbolos com `_` são detalhes internos, cuja assinatura e regras devem ser conferidas antes de reutilizar.

### [__init__.py](__init__.py)

Interface do pacote: reúne importações públicas e recursos descritos abaixo.

- Auxiliares internos (reutilização deve preservar o contexto deste arquivo): `__getattr__`, `__dir__`.
- Constantes, aliases e estado de módulo: `_EXPORTACOES`.
- Importações/reexportações existentes: `from app.core.interfaces import resolver_exportacao as _resolver_exportacao`.

Exportações e proprietários (carregados sob demanda):

- `encerrar_sessao` → `.encerramento` (`encerrar_sessao`).
- `iniciar_sessao` → `.inicio` (`iniciar_sessao`).

### [encerramento.py](encerramento.py)

Encerra sessão própria, persiste título/resumo e indexa histórico no Qdrant.

- `async encerrar_sessao(sessao_id: str, usuario_id: int) -> dict[str, str] | None`: Encerra conversa própria e persiste/indexa resumo quando aplicável.

### [inicio.py](inicio.py)

Cria sessão MongoDB e registra seu ID no cache local.

- `async iniciar_sessao(sessao_id: str, usuario_id: int) -> None`: Cria documento da conversa e registra seu ID no cache local.

## Dependências internas observadas

Importações existentes nos arquivos desta pasta; não representam uma arquitetura desejada nem autorização para ampliar escopos.

- [app/core](../../../core/RESPONSABILIDADE.md).
- [app/core/clients](../../../core/clients/RESPONSABILIDADE.md).
- [app/memory/embedding](../../embedding/RESPONSABILIDADE.md).
- [app/memory/persistencia](../RESPONSABILIDADE.md).
