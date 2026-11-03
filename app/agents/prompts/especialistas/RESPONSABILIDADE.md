# Responsabilidade: app/agents/prompts/especialistas

## Objetivo do módulo

Definir atuação e uso de ferramentas de cada especialidade.

## O que deve ser armazenado aqui

Instruções textuais de FAQ, ajuda, cadastros, indicadores, visualizações, feedback e classificação.

## Comportamento e limites atuais

Os textos orientam o modelo; o código também verifica permissões e execução. O catálogo de visualizações vem de services/visualizacoes.

Módulo pai: [app/agents/prompts](../RESPONSABILIDADE.md).

## Funcionalidades disponíveis e arquivos

O catálogo registra os recursos existentes. Funções assíncronas usam `await`; ferramentas LangChain devem receber o contexto injetado. Símbolos com `_` são detalhes internos, cuja assinatura e regras devem ser conferidas antes de reutilizar.

### [__init__.py](__init__.py)

Interface do pacote: reúne importações públicas e recursos descritos abaixo.

- Auxiliares internos (reutilização deve preservar o contexto deste arquivo): `__getattr__`, `__dir__`.
- Constantes, aliases e estado de módulo: `_EXPORTACOES`.
- Importações/reexportações existentes: `from app.core.interfaces import resolver_exportacao as _resolver_exportacao`.

Exportações e proprietários (carregados sob demanda):

- `AJUDA_GERAL_INSTRUCAO` → `.ajuda_geral` (`AJUDA_GERAL_INSTRUCAO`).
- `AJUDA_GERAL_INSTRUCAO_GESTOR` → `.ajuda_geral` (`AJUDA_GERAL_INSTRUCAO_GESTOR`).
- `AJUDA_GERAL_INSTRUCAO_SOLICITANTE_TECNICO` → `.ajuda_geral` (`AJUDA_GERAL_INSTRUCAO_SOLICITANTE_TECNICO`).
- `AJUDA_GERAL_INSTRUCAO_TECNICO_GESTOR` → `.ajuda_geral` (`AJUDA_GERAL_INSTRUCAO_TECNICO_GESTOR`).
- `CLASSIFICADOR_PROMPT_COMPLETO` → `.classificador` (`CLASSIFICADOR_PROMPT_COMPLETO`).
- `FAQ_INSTRUCAO` → `.faq` (`FAQ_INSTRUCAO`).
- `INDICADORES_INSTRUCAO` → `.indicadores` (`INDICADORES_INSTRUCAO`).
- `RETORNO_USUARIO_INSTRUCAO` → `.retorno_usuario` (`RETORNO_USUARIO_INSTRUCAO`).
- `SOLICITACOES_INSTRUCAO` → `.solicitacoes` (`SOLICITACOES_INSTRUCAO`).
- `VISUALIZACOES_INSTRUCAO` → `.visualizacoes` (`VISUALIZACOES_INSTRUCAO`).

### [ajuda_geral.py](ajuda_geral.py)

Regras de consultas/edições e complementos por perfil.

- Constantes, aliases e estado de módulo: `AJUDA_GERAL_INSTRUCAO`, `AJUDA_GERAL_INSTRUCAO_SOLICITANTE_TECNICO`, `AJUDA_GERAL_INSTRUCAO_TECNICO_GESTOR`, `AJUDA_GERAL_INSTRUCAO_GESTOR`.

### [classificador.py](classificador.py)

Classificação fechada em categoria de problema ou NAO_CLASSIFICAVEL.

- Constantes, aliases e estado de módulo: `CLASSIFICADOR_PROMPT_COMPLETO`.

### [faq.py](faq.py)

Resposta baseada no FAQ e tratamento de informação ausente.

- Constantes, aliases e estado de módulo: `FAQ_INSTRUCAO`.

### [indicadores.py](indicadores.py)

Escolha de ferramentas KPI, interpretação de períodos/bases e indicadores indisponíveis.

- Constantes, aliases e estado de módulo: `INDICADORES_INSTRUCAO`.

### [retorno_usuario.py](retorno_usuario.py)

Coleta fiel do comentário e categorização/preparação do feedback.

- Constantes, aliases e estado de módulo: `RETORNO_USUARIO_INSTRUCAO`.

### [solicitacoes.py](solicitacoes.py)

Coleta, opções, confirmações, anexos e criação/atualização de registros.

- Constantes, aliases e estado de módulo: `SOLICITACOES_INSTRUCAO`.

### [visualizacoes.py](visualizacoes.py)

Consulta e seleção por referência; incorpora catálogo das 27 análises.

- Constantes, aliases e estado de módulo: `VISUALIZACOES_INSTRUCAO`.

## Dependências internas observadas

Importações existentes nos arquivos desta pasta; não representam uma arquitetura desejada nem autorização para ampliar escopos.

- [app/core](../../../core/RESPONSABILIDADE.md).
- [app/services/visualizacoes](../../../services/visualizacoes/RESPONSABILIDADE.md).
