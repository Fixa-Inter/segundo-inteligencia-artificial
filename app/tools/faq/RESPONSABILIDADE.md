# Responsabilidade: app/tools/faq

## Objetivo do módulo

Recuperar trechos FAQ do perfil autenticado.

## O que deve ser armazenado aqui

Ferramenta de busca semântica e formatação dos trechos.

## Comportamento e limites atuais

Perfil vem do contexto. Gera embedding e consulta Qdrant. Administrador usa FAQ de gestor. Não executa ações de manutenção.

Módulo pai: [app/tools](../RESPONSABILIDADE.md).

## Funcionalidades disponíveis e arquivos

O catálogo registra os recursos existentes. Funções assíncronas usam `await`; ferramentas LangChain devem receber o contexto injetado. Símbolos com `_` são detalhes internos, cuja assinatura e regras devem ser conferidas antes de reutilizar.

### [__init__.py](__init__.py)

Interface do pacote: reúne importações públicas e recursos descritos abaixo.

- Auxiliares internos (reutilização deve preservar o contexto deste arquivo): `__getattr__`, `__dir__`.
- Constantes, aliases e estado de módulo: `_EXPORTACOES`.
- Importações/reexportações existentes: `from app.core.interfaces import resolver_exportacao as _resolver_exportacao`.

Exportações e proprietários (carregados sob demanda):

- `buscar_faq` → `.buscar` (`buscar_faq`).

### [buscar.py](buscar.py)

Recursos deste arquivo: Busca trechos do FAQ exclusivo do perfil autenticado para responder à pergunta.

- `async buscar_faq(pergunta: str, runtime: ToolRuntime) -> str`: Busca trechos do FAQ exclusivo do perfil autenticado para responder à pergunta.

## Dependências internas observadas

Importações existentes nos arquivos desta pasta; não representam uma arquitetura desejada nem autorização para ampliar escopos.

- [app/core](../../core/RESPONSABILIDADE.md).
- [app/core/clients](../../core/clients/RESPONSABILIDADE.md).
- [app/memory/embedding](../../memory/embedding/RESPONSABILIDADE.md).
- [app/schemas](../../schemas/RESPONSABILIDADE.md).
