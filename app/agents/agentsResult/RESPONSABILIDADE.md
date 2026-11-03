# Responsabilidade: app/agents/agentsResult

## Objetivo do módulo

Preservar importações históricas dos resultados estruturados.

## O que deve ser armazenado aqui

Modelos Pydantic com agente, resposta, status e referência de visualização.

## Comportamento e limites atuais

Compatibilidade: reexporta os mesmos contratos de schemas/resultados_agentes, sem duplicar classes ou validadores.

Módulo pai: [app/agents](../RESPONSABILIDADE.md).

## Funcionalidades disponíveis e arquivos

O catálogo registra os recursos existentes. Funções assíncronas usam `await`; ferramentas LangChain devem receber o contexto injetado. Símbolos com `_` são detalhes internos, cuja assinatura e regras devem ser conferidas antes de reutilizar.

### [FAQResultado.py](FAQResultado.py)

Reexportação de compatibilidade; a definição e os validadores estão no pacote canônico schemas.

### [IndicadoresResultado.py](IndicadoresResultado.py)

Reexportação de compatibilidade; a definição e os validadores estão no pacote canônico schemas.

### [RetornoUsuarioResultado.py](RetornoUsuarioResultado.py)

Reexportação de compatibilidade; a definição e os validadores estão no pacote canônico schemas.

### [SolicitacaoOcorrenciaResultado.py](SolicitacaoOcorrenciaResultado.py)

Reexportação de compatibilidade; a definição e os validadores estão no pacote canônico schemas.

### [VisualizacaoResultado.py](VisualizacaoResultado.py)

Reexportação de compatibilidade; a definição e os validadores estão no pacote canônico schemas.

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
- [app/schemas/resultados_agentes](../../schemas/resultados_agentes/RESPONSABILIDADE.md).
