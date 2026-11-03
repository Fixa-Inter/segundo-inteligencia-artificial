# Responsabilidade: app/services/tecnicos

## Objetivo do módulo

Consultar técnicos disponíveis ou com menor carga.

## O que deve ser armazenado aqui

SQL de seleção no endereço/unidade autenticados.

## Comportamento e limites atuais

Prioriza técnicos livres; sem livres, seleciona menor carga de OS não concluídas. Não atribui ordens/tarefas.

Módulo pai: [app/services](../RESPONSABILIDADE.md).

## Funcionalidades disponíveis e arquivos

O catálogo registra os recursos existentes. Funções assíncronas usam `await`; ferramentas LangChain devem receber o contexto injetado. Símbolos com `_` são detalhes internos, cuja assinatura e regras devem ser conferidas antes de reutilizar.

### [__init__.py](__init__.py)

Interface do pacote: reúne importações públicas e recursos descritos abaixo.

- Auxiliares internos (reutilização deve preservar o contexto deste arquivo): `__getattr__`, `__dir__`.
- Constantes, aliases e estado de módulo: `_EXPORTACOES`.
- Importações/reexportações existentes: `from app.core.interfaces import resolver_exportacao as _resolver_exportacao`.

Exportações e proprietários (carregados sob demanda):

- `buscar_tecnicos_disponiveis` → `.buscarTecnicosDisponiveis` (`buscar_tecnicos_disponiveis`).

### [buscarTecnicosDisponiveis.py](buscarTecnicosDisponiveis.py)

Recursos deste arquivo: Seleciona tecnicos livres ou, se nao houver, os de menor carga aberta.

- `async buscar_tecnicos_disponiveis(usuario: UsuarioContexto) -> dict`: Seleciona tecnicos livres ou, se nao houver, os de menor carga aberta.
- Constantes, aliases e estado de módulo: `registrador`, `_SQL_TECNICOS_DISPONIVEIS`.

## Dependências internas observadas

Importações existentes nos arquivos desta pasta; não representam uma arquitetura desejada nem autorização para ampliar escopos.

- [app/core](../../core/RESPONSABILIDADE.md).
- [app/core/clients](../../core/clients/RESPONSABILIDADE.md).
- [app/schemas](../../schemas/RESPONSABILIDADE.md).
