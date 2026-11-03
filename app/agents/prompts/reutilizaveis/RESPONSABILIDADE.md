# Responsabilidade: app/agents/prompts/reutilizaveis

## Objetivo do módulo

Expor blocos de instruções compartilhados.

## O que deve ser armazenado aqui

Contexto, glossário, categorias, referência temporal e regras por perfil.

## Comportamento e limites atuais

__init__.py reexporta blocos de gerais e usuarios para construtores e juiz.

Módulo pai: [app/agents/prompts](../RESPONSABILIDADE.md).

## Submódulos

| Pasta | Responsabilidade |
| --- | --- |
| [gerais](gerais/RESPONSABILIDADE.md) | Descrever contexto e vocabulário comuns do FIXA. |
| [usuarios](usuarios/RESPONSABILIDADE.md) | Adaptar instruções ao papel do usuário autenticado. |

## Funcionalidades disponíveis e arquivos

O catálogo registra os recursos existentes. Funções assíncronas usam `await`; ferramentas LangChain devem receber o contexto injetado. Símbolos com `_` são detalhes internos, cuja assinatura e regras devem ser conferidas antes de reutilizar.

### [__init__.py](__init__.py)

Interface do pacote: reúne importações públicas e recursos descritos abaixo.

- Auxiliares internos (reutilização deve preservar o contexto deste arquivo): `__getattr__`, `__dir__`.
- Constantes, aliases e estado de módulo: `_EXPORTACOES`.
- Importações/reexportações existentes: `from app.core.interfaces import resolver_exportacao as _resolver_exportacao`.

Exportações e proprietários (carregados sob demanda):

- `ADMINISTRADOR_INSTRUCAO` → `app.agents.prompts.reutilizaveis.usuarios.administrador` (`ADMINISTRADOR_INSTRUCAO`).
- `CONTEXTO_INSTRUCAO` → `app.agents.prompts.reutilizaveis.gerais.contexto` (`CONTEXTO_INSTRUCAO`).
- `GESTOR_INSTRUCAO` → `app.agents.prompts.reutilizaveis.usuarios.gestor` (`GESTOR_INSTRUCAO`).
- `GLOSSARIO_INSTRUCAO` → `app.agents.prompts.reutilizaveis.gerais.glossario` (`GLOSSARIO_INSTRUCAO`).
- `MAPEAMENTO_CATEGORIA_PROBLEMA_INSTRUCAO` → `app.agents.prompts.reutilizaveis.gerais.mapeamento_categoria_problema` (`MAPEAMENTO_CATEGORIA_PROBLEMA_INSTRUCAO`).
- `SOLICITANTE_INSTRUCAO` → `app.agents.prompts.reutilizaveis.usuarios.solicitante` (`SOLICITANTE_INSTRUCAO`).
- `TECNICO_INSTRUCAO` → `app.agents.prompts.reutilizaveis.usuarios.tecnico` (`TECNICO_INSTRUCAO`).
- `construir_contexto_temporal` → `app.agents.prompts.reutilizaveis.gerais.contexto_temporal` (`construir_contexto_temporal`).
- `gerais` → `.gerais` (submódulo).
- `usuarios` → `.usuarios` (submódulo).

## Dependências internas observadas

Importações existentes nos arquivos desta pasta; não representam uma arquitetura desejada nem autorização para ampliar escopos.

- [app/core](../../../core/RESPONSABILIDADE.md).
