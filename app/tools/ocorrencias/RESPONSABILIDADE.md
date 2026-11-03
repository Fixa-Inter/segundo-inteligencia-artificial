# Responsabilidade: app/tools/ocorrencias

## Objetivo do módulo

Adaptar criação, consulta própria e atualização.

## O que deve ser armazenado aqui

Busca de opções, rascunhos, confirmação, preparação e tabelas.

## Comportamento e limites atuais

Criação exige foto antes do envio. Atualização própria ativa exige aceite de identificação e depois da proposta. processar_* efetiva escrita somente ao receber operação aprovada.

Módulo pai: [app/tools](../RESPONSABILIDADE.md).

## Funcionalidades disponíveis e arquivos

O catálogo registra os recursos existentes. Funções assíncronas usam `await`; ferramentas LangChain devem receber o contexto injetado. Símbolos com `_` são detalhes internos, cuja assinatura e regras devem ser conferidas antes de reutilizar.

### [__init__.py](__init__.py)

Interface do pacote: reúne importações públicas e recursos descritos abaixo.

- Auxiliares internos (reutilização deve preservar o contexto deste arquivo): `__getattr__`, `__dir__`.
- Constantes, aliases e estado de módulo: `_EXPORTACOES`.
- Importações/reexportações existentes: `from app.core.interfaces import resolver_exportacao as _resolver_exportacao`.

Exportações e proprietários (carregados sob demanda):

- `atualizar_ocorrencia` → `.atualizarOcorrencia` (`atualizar_ocorrencia`).
- `buscar_ocorrencias_para_atualizar` → `.atualizarOcorrencia` (`buscar_ocorrencias_para_atualizar`).
- `buscar_opcoes_ocorrencia` → `.buscarOpcoesOcorrencia` (`buscar_opcoes_ocorrencia`).
- `criar_ocorrencia` → `.criarOcorrencia` (`criar_ocorrencia`).
- `listar_minhas_ocorrencias` → `.listarMinhasOcorrencias` (`listar_minhas_ocorrencias`).
- `montar_tabela` → `.utilitarios` (`montar_tabela`).
- `processar_atualizacao` → `.atualizarOcorrencia` (`processar_atualizacao`).
- `processar_ocorrencia` → `.criarOcorrencia` (`processar_ocorrencia`).
- `salvar_rascunho_ocorrencia` → `.criarOcorrencia` (`salvar_rascunho_ocorrencia`).

### [atualizarOcorrencia.py](atualizarOcorrencia.py)

Seleção, proposta e aceite de atualização no mesmo rascunho de ocorrência.

- `async buscar_ocorrencias_para_atualizar(descricao: str, runtime: ToolRuntime) -> dict`: Busca no Qdrant ocorrências próprias e ativas pelo significado da descrição.
- `async atualizar_ocorrencia(runtime: ToolRuntime, ocorrencia_id: int | None=None, titulo: str | None=None, descricao_ocorrencia: str | None=None, descricao_local: str | None=None, local_unidade_id: int | None=None, categoria_equipamento_id: int | None=None, categoria_problema: CategoriaProblema | None=None, prioridade: Prioridade | None=None, acao_fotos: Literal['adicionar', 'substituir'] | None=None) -> dict`: Seleciona uma ocorrência encontrada, coleta várias alterações e prepara atualização após dois aceites.
- `async processar_atualizacao(runtime, *, operacao_aprovada: dict | None=None) -> dict`: Confere proposta final de atualização; prepara operação ou efetiva pelo serviço quando já aprovada.
- Auxiliares internos (reutilização deve preservar o contexto deste arquivo): `_contexto`, `_salvar`, `_resposta`, `_erro`.

### [buscarOpcoesOcorrencia.py](buscarOpcoesOcorrencia.py)

Busca categoria/local sem pedir código ou ID de equipamento ao usuário.

- `async buscar_opcoes_ocorrencia(equipamento: str, local: str, runtime: ToolRuntime) -> dict`: Busca categoria do equipamento e local no Qdrant da sede autenticada.

### [criarOcorrencia.py](criarOcorrencia.py)

Salva proposta, exige confirmação/fotos e prepara operação; processar_ocorrencia atende execução aprovada.

- `async salvar_rascunho_ocorrencia(local_endereco_id: int, categoria_equipamento_id: int, categoria_problema_id: CategoriaProblema, titulo: str, descricao_ocorrencia: str, descricao_local: str, prioridade: Prioridade, runtime: ToolRuntime) -> dict`: Salva a proposta e associa fotos recebidas antes de pedir confirmação.
- `async criar_ocorrencia(runtime: ToolRuntime) -> dict`: Prepara a ocorrência confirmada e suas fotos para aprovação interna.
- `async processar_ocorrencia(runtime: ToolRuntime, *, operacao_aprovada: dict | None=None) -> dict`: Confere proposta/aceite/fotos e prepara operação, ou envia a operação já aprovada.
- Auxiliares internos (reutilização deve preservar o contexto deste arquivo): `_ArgumentosCriarOcorrencia`.
- Constantes, aliases e estado de módulo: `registrador`.

### [listarMinhasOcorrencias.py](listarMinhasOcorrencias.py)

Wrapper de três ocorrências próprias recentes e tabela Markdown.

- `async listar_minhas_ocorrencias(runtime: ToolRuntime) -> dict`: Lista ate tres ocorrencias recentes do tecnico ou gestor nos ultimos tres meses.

### [utilitarios.py](utilitarios.py)

Adapta colunas/política de data da ocorrência ao renderizador comum, preservando ordem dos registros.

- `montar_tabela(ocorrencias: list[dict]) -> str`: Apresenta as ocorrências na mesma ordem retornada pela API.
- Auxiliares internos (reutilização deve preservar o contexto deste arquivo): `_celula`.

## Dependências internas observadas

Importações existentes nos arquivos desta pasta; não representam uma arquitetura desejada nem autorização para ampliar escopos.

- [app/core](../../core/RESPONSABILIDADE.md).
- [app/core/apresentacao](../../core/apresentacao/RESPONSABILIDADE.md).
- [app/core/clients](../../core/clients/RESPONSABILIDADE.md).
- [app/memory/persistencia](../../memory/persistencia/RESPONSABILIDADE.md).
- [app/memory/vectorSearch](../../memory/vectorSearch/RESPONSABILIDADE.md).
- [app/observability](../../observability/RESPONSABILIDADE.md).
- [app/schemas](../../schemas/RESPONSABILIDADE.md).
- [app/schemas/cadastros](../../schemas/cadastros/RESPONSABILIDADE.md).
- [app/services](../../services/RESPONSABILIDADE.md).
- [app/services/gerais](../../services/gerais/RESPONSABILIDADE.md).
- [app/services/ocorrencias](../../services/ocorrencias/RESPONSABILIDADE.md).
- [app/tools](../RESPONSABILIDADE.md).
- [app/tools/ajuda_geral](../ajuda_geral/RESPONSABILIDADE.md).
