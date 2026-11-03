# Responsabilidade: app/tools/toolsRequest

## Objetivo do módulo

Preservar importações históricas dos contratos de cadastro.

## O que deve ser armazenado aqui

CriarSolicitacaoEntrada, CriarOcorrenciaEntrada, CriarEventoEntrada e enums.

## Comportamento e limites atuais

Pacote de compatibilidade para schemas/cadastros. Os arquivos não duplicam contratos: reexportam a mesma classe/enum canônica. Identidade e token continuam fora dos argumentos da IA.

Módulo pai: [app/tools](../RESPONSABILIDADE.md).

## Funcionalidades disponíveis e arquivos

O catálogo registra os recursos existentes. Funções assíncronas usam `await`; ferramentas LangChain devem receber o contexto injetado. Símbolos com `_` são detalhes internos, cuja assinatura e regras devem ser conferidas antes de reutilizar.

### [CriarEventoEntrada.py](CriarEventoEntrada.py)

Reexportação de compatibilidade; a definição e os validadores estão no pacote canônico schemas.

### [CriarOcorrenciaEntrada.py](CriarOcorrenciaEntrada.py)

Reexportação de compatibilidade; a definição e os validadores estão no pacote canônico schemas.

### [CriarSolicitacaoEntrada.py](CriarSolicitacaoEntrada.py)

Reexportação de compatibilidade; a definição e os validadores estão no pacote canônico schemas.

### [__init__.py](__init__.py)

Interface do pacote: reúne importações públicas e recursos descritos abaixo.

- Auxiliares internos (reutilização deve preservar o contexto deste arquivo): `__getattr__`, `__dir__`.
- Constantes, aliases e estado de módulo: `_EXPORTACOES`.
- Importações/reexportações existentes: `from app.core.interfaces import resolver_exportacao as _resolver_exportacao`.

Exportações e proprietários (carregados sob demanda):

- `CategoriaProblema` → `.CriarOcorrenciaEntrada` (`CategoriaProblema`).
- `CriarEventoEntrada` → `.CriarEventoEntrada` (`CriarEventoEntrada`).
- `CriarOcorrenciaEntrada` → `.CriarOcorrenciaEntrada` (`CriarOcorrenciaEntrada`).
- `CriarSolicitacaoEntrada` → `.CriarSolicitacaoEntrada` (`CriarSolicitacaoEntrada`).
- `Prioridade` → `.CriarOcorrenciaEntrada` (`Prioridade`).

## Dependências internas observadas

Importações existentes nos arquivos desta pasta; não representam uma arquitetura desejada nem autorização para ampliar escopos.

- [app/core](../../core/RESPONSABILIDADE.md).
- [app/schemas/cadastros](../../schemas/cadastros/RESPONSABILIDADE.md).
