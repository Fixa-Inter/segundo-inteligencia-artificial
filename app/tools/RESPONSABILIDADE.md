# Responsabilidade: app/tools

## Objetivo do módulo

Expor capacidades como ferramentas para agentes.

## O que deve ser armazenado aqui

Adaptadores LangChain, argumentos/contexto e preparação de propostas.

## Comportamento e limites atuais

ArgumentosComRuntime separa contexto confiável dos argumentos do modelo; contexto.py valida cadastros sem depender de uma tool específica. Tools usam schemas canônicos, serviços e projeções core. Gravações continuam preparadas para o executor aprovado.

Módulo pai: [app](../RESPONSABILIDADE.md).

## Submódulos

| Pasta | Responsabilidade |
| --- | --- |
| [ajuda_geral](ajuda_geral/RESPONSABILIDADE.md) | Adaptar consultas e edições para ajuda geral. |
| [eventos](eventos/RESPONSABILIDADE.md) | Coletar e confirmar propostas de eventos. |
| [faq](faq/RESPONSABILIDADE.md) | Recuperar trechos FAQ do perfil autenticado. |
| [feedback](feedback/RESPONSABILIDADE.md) | Preparar registro e listar feedback próprio. |
| [memoria](memoria/RESPONSABILIDADE.md) | Expor recuperação de conversas aos agentes. |
| [metricas_kpis](metricas_kpis/RESPONSABILIDADE.md) | Expor 36 ferramentas gerenciais de indicadores. |
| [ocorrencias](ocorrencias/RESPONSABILIDADE.md) | Adaptar criação, consulta própria e atualização. |
| [ordensServico](ordensServico/RESPONSABILIDADE.md) | Disponibilizar busca/listagem de OS aos agentes. |
| [solicitacoes](solicitacoes/RESPONSABILIDADE.md) | Adaptar cadastro, consulta e atualização. |
| [tecnicos](tecnicos/RESPONSABILIDADE.md) | Expor disponibilidade de técnicos ao agente. |
| [toolsRequest](toolsRequest/RESPONSABILIDADE.md) | Preservar importações históricas dos contratos de cadastro. |
| [visualizacoes](visualizacoes/RESPONSABILIDADE.md) | Adaptar seis ferramentas aos serviços canônicos. |

## Funcionalidades disponíveis e arquivos

O catálogo registra os recursos existentes. Funções assíncronas usam `await`; ferramentas LangChain devem receber o contexto injetado. Símbolos com `_` são detalhes internos, cuja assinatura e regras devem ser conferidas antes de reutilizar.

### [__init__.py](__init__.py)

Interface do pacote: reúne importações públicas e recursos descritos abaixo.

- Auxiliares internos (reutilização deve preservar o contexto deste arquivo): `__getattr__`, `__dir__`.
- Constantes, aliases e estado de módulo: `_EXPORTACOES`.
- Importações/reexportações existentes: `from app.core.interfaces import resolver_exportacao as _resolver_exportacao`.

Exportações e proprietários (carregados sob demanda):

- `ArgumentosComRuntime` → `.argumentos` (`ArgumentosComRuntime`).
- `ajuda_geral` → `.ajuda_geral` (submódulo).
- `confirmou_selecao` → `.atualizacoes` (`confirmou_selecao`).
- `eventos` → `.eventos` (submódulo).
- `faq` → `.faq` (submódulo).
- `feedback` → `.feedback` (submódulo).
- `memoria` → `.memoria` (submódulo).
- `metricas_kpis` → `.metricas_kpis` (submódulo).
- `obter_contexto_cadastro` → `.contexto` (`obter_contexto_cadastro`).
- `ocorrencias` → `.ocorrencias` (submódulo).
- `ordensServico` → `.ordensServico` (submódulo).
- `resolver_rotulos` → `.propostas` (`resolver_rotulos`).
- `salvar_proposta` → `.atualizacoes` (`salvar_proposta`).
- `solicitacoes` → `.solicitacoes` (submódulo).
- `tecnicos` → `.tecnicos` (submódulo).
- `toolsRequest` → `.toolsRequest` (submódulo).
- `visualizacoes` → `.visualizacoes` (submódulo).

### [argumentos.py](argumentos.py)

Validação compartilhada da fronteira entre argumentos do modelo e ToolRuntime.

- Classe `ArgumentosComRuntime` (`BaseModel`): Remove somente o ToolRuntime Python injetado pelo SDK nos schemas de tools.
  Métodos/validadores: `separar_runtime_injetado(cls, dados)`.

### [atualizacoes.py](atualizacoes.py)

Regras compartilhadas de versionamento e identificação de registros.

- `async salvar_proposta(contexto: dict, rascunho: dict, atualizar, **campos) -> dict`: Salva versão de proposta e invalida conferência anterior quando os dados mudam.
- `confirmou_selecao(texto: str) -> bool`: Identificar o registro não autoriza gravar a proposta final.

### [contexto.py](contexto.py)

Contexto autenticado das ferramentas de cadastro; compartilhado entre domínios.

- `obter_contexto_cadastro(runtime: ToolRuntime) -> tuple[dict[str, Any], UsuarioContexto, str]`: Executa a etapa obter contexto cadastro no escopo de contexto. Usado pelo fluxo de tools.

### [propostas.py](propostas.py)

Resolve rótulos verificáveis de categoria/local para apresentar propostas.

- `async resolver_rotulos(dados: dict, usuario) -> dict[str, str]`: Confere IDs Qdrant e resolve rótulos de categoria/local da unidade.

## Dependências internas observadas

Importações existentes nos arquivos desta pasta; não representam uma arquitetura desejada nem autorização para ampliar escopos.

- [app/core](../core/RESPONSABILIDADE.md).
- [app/core/clients](../core/clients/RESPONSABILIDADE.md).
- [app/memory/vectorSearch](../memory/vectorSearch/RESPONSABILIDADE.md).
- [app/schemas](../schemas/RESPONSABILIDADE.md).
- [app/services/gerais](../services/gerais/RESPONSABILIDADE.md).
