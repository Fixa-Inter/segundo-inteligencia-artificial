# Responsabilidade: app/schemas/cadastros

## Objetivo do módulo

Definir contratos canônicos dos cadastros FIXA.

## O que deve ser armazenado aqui

Modelos Pydantic de solicitação, ocorrência e evento e enums textuais de ocorrência.

## Comportamento e limites atuais

Serviços e ferramentas importam estes tipos por __init__.py. tools/toolsRequest reexporta as mesmas classes para compatibilidade. Não recebe identidade ou token da IA.

Módulo pai: [app/schemas](../RESPONSABILIDADE.md).

## Funcionalidades disponíveis e arquivos

O catálogo registra os recursos existentes. Funções assíncronas usam `await`; ferramentas LangChain devem receber o contexto injetado. Símbolos com `_` são detalhes internos, cuja assinatura e regras devem ser conferidas antes de reutilizar.

### [CriarEventoEntrada.py](CriarEventoEntrada.py)

Dados do evento fornecidos pela IA; identidade e token vêm do backend.

- Classe `CriarEventoEntrada` (`BaseModel`).
  Campos/atributos declarados: `local_unidade_id: int`, `titulo: str`, `descricao: str`, `data_hora_inicio: datetime`, `data_hora_fim: datetime`, `descricao_local: str`, `observacao: str`.
  Métodos/validadores: `limitar_palavras(cls, valor: str) -> str`; `normalizar_horario(cls, valor) -> datetime`; `validar_periodo(self)`.

### [CriarOcorrenciaEntrada.py](CriarOcorrenciaEntrada.py)

Recursos deste arquivo: Dados da proposta; nomes dos enums seguem docs/enum e o Swagger.

- Classe `CriarOcorrenciaEntrada` (`BaseModel`): Dados da proposta; nomes dos enums seguem docs/enum e o Swagger.
  Campos/atributos declarados: `local_endereco_id: int`, `categoria_equipamento_id: int`, `categoria_problema_id: CategoriaProblema`, `prioridade: Prioridade`, `titulo: str`, `descricao_ocorrencia: str`, `descricao_local: str`.
- Constantes, aliases e estado de módulo: `CategoriaProblema`, `Prioridade`.

### [CriarSolicitacaoEntrada.py](CriarSolicitacaoEntrada.py)

Recursos deste arquivo: Dados da solicitação preenchidos pela IA, base para o args_schema da tool.

- Classe `CriarSolicitacaoEntrada` (`BaseModel`): Dados da solicitação preenchidos pela IA, base para o args_schema da tool.
  Campos/atributos declarados: `categoria_equipamento_id: int`, `local_endereco_id: int`, `titulo: str`, `descricao_problema: str`, `descricao_local: str`.

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
