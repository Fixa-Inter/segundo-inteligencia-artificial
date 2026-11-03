# Responsabilidade: app/tools/tecnicos

## Objetivo do módulo

Expor disponibilidade de técnicos ao agente.

## O que deve ser armazenado aqui

Wrapper LangChain com usuário do runtime.

## Comportamento e limites atuais

Disponibilidade e menor carga são calculadas por services/tecnicos. A IA não fornece identidade.

Módulo pai: [app/tools](../RESPONSABILIDADE.md).

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

Extrai usuário do runtime e consulta técnicos livres ou com menor carga.

- `async buscar_tecnicos_disponiveis(runtime: ToolRuntime) -> dict`: Busca técnicos do endereço do gestor com menor carga de OS fora de Concluída (ID 4).

## Dependências internas observadas

Importações existentes nos arquivos desta pasta; não representam uma arquitetura desejada nem autorização para ampliar escopos.

- [app/core](../../core/RESPONSABILIDADE.md).
- [app/schemas](../../schemas/RESPONSABILIDADE.md).
- [app/services/tecnicos](../../services/tecnicos/RESPONSABILIDADE.md).
