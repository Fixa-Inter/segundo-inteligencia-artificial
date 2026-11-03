# Responsabilidade: app/agents/prompts

## Objetivo do módulo

Compor instruções dos especialistas para cada perfil.

## O que deve ser armazenado aqui

Construtores de prompts e suas partes reutilizáveis.

## Comportamento e limites atuais

construtor.py combina contexto, glossário, perfil e especialidade. A referência temporal é renovada por turno.

Módulo pai: [app/agents](../RESPONSABILIDADE.md).

## Submódulos

| Pasta | Responsabilidade |
| --- | --- |
| [especialistas](especialistas/RESPONSABILIDADE.md) | Definir atuação e uso de ferramentas de cada especialidade. |
| [reutilizaveis](reutilizaveis/RESPONSABILIDADE.md) | Expor blocos de instruções compartilhados. |

## Funcionalidades disponíveis e arquivos

O catálogo registra os recursos existentes. Funções assíncronas usam `await`; ferramentas LangChain devem receber o contexto injetado. Símbolos com `_` são detalhes internos, cuja assinatura e regras devem ser conferidas antes de reutilizar.

### [__init__.py](__init__.py)

Interface do pacote: reúne importações públicas e recursos descritos abaixo.

- Auxiliares internos (reutilização deve preservar o contexto deste arquivo): `__getattr__`, `__dir__`.
- Constantes, aliases e estado de módulo: `_EXPORTACOES`.
- Importações/reexportações existentes: `from app.core.interfaces import resolver_exportacao as _resolver_exportacao`.

Exportações e proprietários (carregados sob demanda):

- `construir_ajuda_geral_administrador` → `.construtor` (`construir_ajuda_geral_administrador`).
- `construir_ajuda_geral_gestor` → `.construtor` (`construir_ajuda_geral_gestor`).
- `construir_ajuda_geral_solicitante` → `.construtor` (`construir_ajuda_geral_solicitante`).
- `construir_ajuda_geral_tecnico` → `.construtor` (`construir_ajuda_geral_tecnico`).
- `construir_faq_administrador` → `.construtor` (`construir_faq_administrador`).
- `construir_faq_gestor` → `.construtor` (`construir_faq_gestor`).
- `construir_faq_solicitante` → `.construtor` (`construir_faq_solicitante`).
- `construir_faq_tecnico` → `.construtor` (`construir_faq_tecnico`).
- `construir_indicadores_administrador` → `.construtor` (`construir_indicadores_administrador`).
- `construir_indicadores_gestor` → `.construtor` (`construir_indicadores_gestor`).
- `construir_retorno_usuario` → `.construtor` (`construir_retorno_usuario`).
- `construir_solicitacoes_administrador` → `.construtor` (`construir_solicitacoes_administrador`).
- `construir_solicitacoes_gestor` → `.construtor` (`construir_solicitacoes_gestor`).
- `construir_solicitacoes_solicitante` → `.construtor` (`construir_solicitacoes_solicitante`).
- `construir_solicitacoes_tecnico` → `.construtor` (`construir_solicitacoes_tecnico`).
- `construir_visualizacoes_administrador` → `.construtor` (`construir_visualizacoes_administrador`).
- `construir_visualizacoes_gestor` → `.construtor` (`construir_visualizacoes_gestor`).
- `especialistas` → `.especialistas` (submódulo).
- `reutilizaveis` → `.reutilizaveis` (submódulo).

### [construtor.py](construtor.py)

Combina blocos de contexto/glossário/perfil/especialidade nos prompts finais.

- `construir_ajuda_geral_solicitante() -> str`: Compõe instrução de ajuda geral solicitante usando os blocos compartilhados.
- `construir_ajuda_geral_tecnico() -> str`: Compõe instrução de ajuda geral tecnico usando os blocos compartilhados.
- `construir_ajuda_geral_gestor() -> str`: Compõe instrução de ajuda geral gestor usando os blocos compartilhados.
- `construir_ajuda_geral_administrador() -> str`: Compõe instrução de ajuda geral administrador usando os blocos compartilhados.
- `construir_retorno_usuario() -> str`: Compõe instrução de retorno usuario usando os blocos compartilhados.
- `construir_faq_solicitante() -> str`: Compõe instrução de faq solicitante usando os blocos compartilhados.
- `construir_faq_tecnico() -> str`: Compõe instrução de faq tecnico usando os blocos compartilhados.
- `construir_faq_gestor() -> str`: Compõe instrução de faq gestor usando os blocos compartilhados.
- `construir_faq_administrador() -> str`: Compõe instrução de faq administrador usando os blocos compartilhados.
- `construir_solicitacoes_solicitante() -> str`: Compõe instrução de solicitacoes solicitante usando os blocos compartilhados.
- `construir_solicitacoes_tecnico() -> str`: Compõe instrução de solicitacoes tecnico usando os blocos compartilhados.
- `construir_solicitacoes_gestor() -> str`: Compõe instrução de solicitacoes gestor usando os blocos compartilhados.
- `construir_solicitacoes_administrador() -> str`: Compõe instrução de solicitacoes administrador usando os blocos compartilhados.
- `construir_indicadores_gestor() -> str`: Compõe instrução de indicadores gestor usando os blocos compartilhados.
- `construir_indicadores_administrador() -> str`: Compõe instrução de indicadores administrador usando os blocos compartilhados.
- `construir_visualizacoes_gestor() -> str`: Compõe instrução de visualizacoes gestor usando os blocos compartilhados.
- `construir_visualizacoes_administrador() -> str`: Compõe instrução de visualizacoes administrador usando os blocos compartilhados.

## Dependências internas observadas

Importações existentes nos arquivos desta pasta; não representam uma arquitetura desejada nem autorização para ampliar escopos.

- [app/agents/prompts/especialistas](especialistas/RESPONSABILIDADE.md).
- [app/agents/prompts/reutilizaveis](reutilizaveis/RESPONSABILIDADE.md).
- [app/core](../../core/RESPONSABILIDADE.md).
