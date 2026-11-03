# Responsabilidade: app/agents/prompts/reutilizaveis/usuarios

## Objetivo do módulo

Adaptar instruções ao papel do usuário autenticado.

## O que deve ser armazenado aqui

Blocos de solicitante, técnico, gestor e administrador.

## Comportamento e limites atuais

ADMINISTRADOR_INSTRUCAO herda GESTOR_INSTRUCAO. Objetivos descritos nos perfis não significam que existam ferramentas para todas as ações.

Módulo pai: [app/agents/prompts/reutilizaveis](../RESPONSABILIDADE.md).

## Funcionalidades disponíveis e arquivos

O catálogo registra os recursos existentes. Funções assíncronas usam `await`; ferramentas LangChain devem receber o contexto injetado. Símbolos com `_` são detalhes internos, cuja assinatura e regras devem ser conferidas antes de reutilizar.

### [__init__.py](__init__.py)

Interface do pacote: reúne importações públicas e recursos descritos abaixo.

- Auxiliares internos (reutilização deve preservar o contexto deste arquivo): `__getattr__`, `__dir__`.
- Constantes, aliases e estado de módulo: `_EXPORTACOES`.
- Importações/reexportações existentes: `from app.core.interfaces import resolver_exportacao as _resolver_exportacao`.

Exportações e proprietários (carregados sob demanda):

- `ADMINISTRADOR_INSTRUCAO` → `.administrador` (`ADMINISTRADOR_INSTRUCAO`).
- `GESTOR_INSTRUCAO` → `.gestor` (`GESTOR_INSTRUCAO`).
- `SOLICITANTE_INSTRUCAO` → `.solicitante` (`SOLICITANTE_INSTRUCAO`).
- `TECNICO_INSTRUCAO` → `.tecnico` (`TECNICO_INSTRUCAO`).

### [administrador.py](administrador.py)

Herda o bloco de gestor e preserva identidade/limites do administrador.

- Constantes, aliases e estado de módulo: `ADMINISTRADOR_INSTRUCAO`.

### [gestor.py](gestor.py)

Papel e comunicação gerencial, interpretação de dados e limites de escopo.

- Constantes, aliases e estado de módulo: `GESTOR_INSTRUCAO`.

### [solicitante.py](solicitante.py)

Papel, comunicação e limites do solicitante.

- Constantes, aliases e estado de módulo: `SOLICITANTE_INSTRUCAO`.

### [tecnico.py](tecnico.py)

Papel, comunicação prática e limites do técnico.

- Constantes, aliases e estado de módulo: `TECNICO_INSTRUCAO`.

## Dependências internas observadas

Importações existentes nos arquivos desta pasta; não representam uma arquitetura desejada nem autorização para ampliar escopos.

- [app/core](../../../../core/RESPONSABILIDADE.md).
