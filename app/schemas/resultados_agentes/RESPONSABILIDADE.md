# Responsabilidade: app/schemas/resultados_agentes

## Objetivo do módulo

Definir saídas estruturadas dos especialistas.

## O que deve ser armazenado aqui

Modelos Pydantic de FAQ/ajuda, indicadores, feedback, cadastros e referência de visualização.

## Comportamento e limites atuais

Os agentes e o grafo usam estes contratos; agents/agentsResult reexporta as mesmas classes. Visualização estruturada contém uma referência, não dados fabricados pelo modelo.

Módulo pai: [app/schemas](../RESPONSABILIDADE.md).

## Funcionalidades disponíveis e arquivos

O catálogo registra os recursos existentes. Funções assíncronas usam `await`; ferramentas LangChain devem receber o contexto injetado. Símbolos com `_` são detalhes internos, cuja assinatura e regras devem ser conferidas antes de reutilizar.

### [FAQResultado.py](FAQResultado.py)

Contrato canônico de resposta/status do FAQ e do agente de ajuda geral.

- Classe `FAQResultado` (`BaseModel`).
  Campos/atributos declarados: `agente: str`, `resposta: str`, `status: Literal['OPERACAO_PREPARADA', 'SUCESSO', 'SUCESSO_PARCIAL', 'AGUARDANDO_INFORMACAO', 'SEM_RESULTADO', 'FERRAMENTA_INDISPONIVEL', 'ERRO_VALIDACAO', 'ERRO_FERRAMENTA', 'ERRO_MODELO', 'TIMEOUT']`.

### [IndicadoresResultado.py](IndicadoresResultado.py)

Contrato canônico de resposta/status do especialista de indicadores.

- Classe `IndicadoresResultado` (`BaseModel`).
  Campos/atributos declarados: `agente: str`, `resposta: str`, `status: Literal['SUCESSO', 'SUCESSO_PARCIAL', 'AGUARDANDO_INFORMACAO', 'SEM_RESULTADO', 'ERRO_VALIDACAO', 'ERRO_FERRAMENTA', 'ERRO_MODELO', 'TIMEOUT']`.

### [RetornoUsuarioResultado.py](RetornoUsuarioResultado.py)

Contrato canônico do especialista de feedback e operações preparadas.

- Classe `RetornoUsuarioResultado` (`BaseModel`).
  Campos/atributos declarados: `agente: str`, `resposta: str`, `status: Literal['OPERACAO_PREPARADA', 'SUCESSO', 'SUCESSO_PARCIAL', 'AGUARDANDO_INFORMACAO', 'SEM_RESULTADO', 'ERRO_VALIDACAO', 'ERRO_FERRAMENTA', 'ERRO_MODELO', 'TIMEOUT']`.

### [SolicitacaoOcorrenciaResultado.py](SolicitacaoOcorrenciaResultado.py)

Contrato canônico compartilhado de solicitações, ocorrências e eventos.

- Classe `SolicitacaoOcorrenciaResultado` (`BaseModel`).
  Campos/atributos declarados: `agente: str`, `resposta: str`, `status: Literal['OPERACAO_PREPARADA', 'SUCESSO', 'SUCESSO_PARCIAL', 'AGUARDANDO_INFORMACAO', 'SEM_RESULTADO', 'FERRAMENTA_INDISPONIVEL', 'ERRO_VALIDACAO', 'ERRO_FERRAMENTA', 'ERRO_MODELO', 'TIMEOUT']`.

### [VisualizacaoResultado.py](VisualizacaoResultado.py)

Recursos deste arquivo: Texto e uma referência à consulta; não é o payload público do gráfico.

- Classe `VisualizacaoResultado` (`BaseModel`): Texto e uma referência à consulta; não é o payload público do gráfico.
  Campos/atributos declarados: `agente: Literal['visualizacao']`, `resposta: str`, `status: StatusVisualizacao`, `visualizacao: ReferenciaVisualizacao | None`.
  Métodos/validadores: `validar_texto(cls, valor)`; `validar_selecao(self)`.

### [__init__.py](__init__.py)

Interface do pacote: reúne importações públicas e recursos descritos abaixo.

- Auxiliares internos (reutilização deve preservar o contexto deste arquivo): `__getattr__`, `__dir__`.
- Constantes, aliases e estado de módulo: `_EXPORTACOES`.
- Importações/reexportações existentes: `from app.core.interfaces import resolver_exportacao as _resolver_exportacao`.

Exportações e proprietários (carregados sob demanda):

- `FAQResultado` → `.FAQResultado` (`FAQResultado`).
- `IndicadoresResultado` → `.IndicadoresResultado` (`IndicadoresResultado`).
- `RetornoUsuarioResultado` → `.RetornoUsuarioResultado` (`RetornoUsuarioResultado`).
- `SolicitacaoOcorrenciaResultado` → `.SolicitacaoOcorrenciaResultado` (`SolicitacaoOcorrenciaResultado`).
- `VisualizacaoResultado` → `.VisualizacaoResultado` (`VisualizacaoResultado`).

## Dependências internas observadas

Importações existentes nos arquivos desta pasta; não representam uma arquitetura desejada nem autorização para ampliar escopos.

- [app/core](../../core/RESPONSABILIDADE.md).
- [app/schemas](../RESPONSABILIDADE.md).
