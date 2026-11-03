# Responsabilidade: app/agents/prompts/reutilizaveis/gerais

## Objetivo do módulo

Descrever contexto e vocabulário comuns do FIXA.

## O que deve ser armazenado aqui

Textos de domínio e construção de contexto temporal.

## Comportamento e limites atuais

Categoria de problema é enum textual, diferente de ID de categoria de equipamento. contexto.py tem uma referência a administrador como técnico; registro e bloco específico de administrador seguem gestor.

Módulo pai: [app/agents/prompts/reutilizaveis](../RESPONSABILIDADE.md).

## Funcionalidades disponíveis e arquivos

O catálogo registra os recursos existentes. Funções assíncronas usam `await`; ferramentas LangChain devem receber o contexto injetado. Símbolos com `_` são detalhes internos, cuja assinatura e regras devem ser conferidas antes de reutilizar.

### [__init__.py](__init__.py)

Interface do pacote: reúne importações públicas e recursos descritos abaixo.

- Auxiliares internos (reutilização deve preservar o contexto deste arquivo): `__getattr__`, `__dir__`.
- Constantes, aliases e estado de módulo: `_EXPORTACOES`.
- Importações/reexportações existentes: `from app.core.interfaces import resolver_exportacao as _resolver_exportacao`.

Exportações e proprietários (carregados sob demanda):

- `CONTEXTO_INSTRUCAO` → `.contexto` (`CONTEXTO_INSTRUCAO`).
- `GLOSSARIO_INSTRUCAO` → `.glossario` (`GLOSSARIO_INSTRUCAO`).
- `MAPEAMENTO_CATEGORIA_PROBLEMA_INSTRUCAO` → `.mapeamento_categoria_problema` (`MAPEAMENTO_CATEGORIA_PROBLEMA_INSTRUCAO`).
- `construir_contexto_temporal` → `.contexto_temporal` (`construir_contexto_temporal`).

### [contexto.py](contexto.py)

Contexto do produto, comunicação, limitações, operações preparadas e anexos sem interpretação visual.

- Constantes, aliases e estado de módulo: `CONTEXTO_INSTRUCAO`.

### [contexto_temporal.py](contexto_temporal.py)

Constrói referência do turno no fuso America/Sao_Paulo.

- `construir_contexto_temporal(instante: datetime | None=None) -> str`: Monta referência temporal do turno, convertendo instante informado para o fuso de negócio.

### [glossario.py](glossario.py)

Vocabulário de manutenção, solicitações, ocorrências, OS, tarefas e equipamentos.

- Constantes, aliases e estado de módulo: `GLOSSARIO_INSTRUCAO`.

### [mapeamento_categoria_problema.py](mapeamento_categoria_problema.py)

Enums textuais e orientação para confirmar categoria de problema.

- Constantes, aliases e estado de módulo: `MAPEAMENTO_CATEGORIA_PROBLEMA_INSTRUCAO`.

## Dependências internas observadas

Importações existentes nos arquivos desta pasta; não representam uma arquitetura desejada nem autorização para ampliar escopos.

- [app/core](../../../../core/RESPONSABILIDADE.md).
