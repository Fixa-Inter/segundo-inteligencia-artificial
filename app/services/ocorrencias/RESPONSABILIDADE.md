# Responsabilidade: app/services/ocorrencias

## Objetivo do módulo

Consultar, cadastrar e atualizar ocorrências.

## O que deve ser armazenado aqui

SQL, POST FIXA e busca/edição transacional própria.

## Comportamento e limites atuais

Atualização exige autoria, unidade e atividade para técnico/gestor/administrador, sem filtro de status. Confere snapshot sob trava e altera textos, enums e fotos na mesma transação.

Módulo pai: [app/services](../RESPONSABILIDADE.md).

## Funcionalidades disponíveis e arquivos

O catálogo registra os recursos existentes. Funções assíncronas usam `await`; ferramentas LangChain devem receber o contexto injetado. Símbolos com `_` são detalhes internos, cuja assinatura e regras devem ser conferidas antes de reutilizar.

### [__init__.py](__init__.py)

Interface do pacote: reúne importações públicas e recursos descritos abaixo.

- Auxiliares internos (reutilização deve preservar o contexto deste arquivo): `__getattr__`, `__dir__`.
- Constantes, aliases e estado de módulo: `_EXPORTACOES`.
- Importações/reexportações existentes: `from app.core.interfaces import resolver_exportacao as _resolver_exportacao`.

Exportações e proprietários (carregados sob demanda):

- `CAMPOS` → `.atualizarOcorrencia` (`CAMPOS`).
- `ENUMS` → `.atualizarOcorrencia` (`ENUMS`).
- `PERFIS` → `.atualizarOcorrencia` (`PERFIS`).
- `adicionar_ocorrencia` → `.criarOcorrencia` (`adicionar_ocorrencia`).
- `atualizar_propria_ativa` → `.atualizarOcorrencia` (`atualizar_propria_ativa`).
- `buscar_equipamento_por_codigo` → `.buscarOcorrencias` (`buscar_equipamento_por_codigo`).
- `buscar_proprias_ativas` → `.atualizarOcorrencia` (`buscar_proprias_ativas`).
- `consultar_minhas_ocorrencias` → `.buscarOcorrencias` (`consultar_minhas_ocorrencias`).
- `consultar_propria_ativa` → `.atualizarOcorrencia` (`consultar_propria_ativa`).
- `rotulos_enums` → `.atualizarOcorrencia` (`rotulos_enums`).
- `snapshot` → `.atualizarOcorrencia` (`snapshot`).
- `validar_alteracoes` → `.atualizarOcorrencia` (`validar_alteracoes`).
- `validar_usuario` → `.atualizarOcorrencia` (`validar_usuario`).

### [atualizarOcorrencia.py](atualizarOcorrencia.py)

Busca e edição transacional de ocorrências próprias e ativas.

- `validar_usuario(usuario: UsuarioContexto) -> None`: Confere perfil autorizado no fluxo de ocorrência.
- `validar_alteracoes(alteracoes: dict) -> dict`: Valida campos permitidos da atualização do domínio.
- `rotulos_enums(dados: dict) -> dict`: Resolve rótulos de categoria de problema/prioridade.
- `async buscar_proprias_ativas(usuario: UsuarioContexto, descricao: str) -> list[dict]`: Cruza busca vetorial com IDs de ocorrências próprias ativas na unidade.
- `async consultar_propria_ativa(usuario: UsuarioContexto, registro_id: int) -> dict | None`: Lê ocorrência/fotos atuais conferindo autoria, unidade e atividade.
- `snapshot(registro: dict) -> dict`: Extrai dados originais para detectar mudança antes da escrita.
- `async atualizar_propria_ativa(usuario: UsuarioContexto, dados: dict) -> dict | None`: Trava e revalida ocorrência/snapshot e grava alterações/enums/fotos na mesma transação.
- Auxiliares internos (reutilização deve preservar o contexto deste arquivo): `_ler`.
- Constantes, aliases e estado de módulo: `PERFIS`, `CAMPOS`, `ENUMS`.

### [buscarOcorrencias.py](buscarOcorrencias.py)

Equipamento por código e ocorrências próprias recentes em SQL.

- `async buscar_equipamento_por_codigo(codigo: str, usuario: UsuarioContexto) -> dict`: Resolve codigo de equipamento ativo no endereco do usuario autenticado.
- `async consultar_minhas_ocorrencias(usuario: UsuarioContexto) -> dict`: Consulta ocorrencias do usuario no endereco dele nos ultimos tres meses.
- Constantes, aliases e estado de módulo: `registrador`.

### [criarOcorrencia.py](criarOcorrencia.py)

Recursos deste arquivo: Envia uma única requisição conforme OcorrenciaCadastrarInputDTO.

- `async adicionar_ocorrencia(ocorrencia: CriarOcorrenciaEntrada, access_token: str, *, usuario_id: int, imagens: list[str]) -> dict`: Envia uma única requisição conforme OcorrenciaCadastrarInputDTO.

## Dependências internas observadas

Importações existentes nos arquivos desta pasta; não representam uma arquitetura desejada nem autorização para ampliar escopos.

- [app/core](../../core/RESPONSABILIDADE.md).
- [app/core/apresentacao](../../core/apresentacao/RESPONSABILIDADE.md).
- [app/core/clients](../../core/clients/RESPONSABILIDADE.md).
- [app/memory/embedding](../../memory/embedding/RESPONSABILIDADE.md).
- [app/memory/vectorSearch](../../memory/vectorSearch/RESPONSABILIDADE.md).
- [app/schemas](../../schemas/RESPONSABILIDADE.md).
- [app/schemas/cadastros](../../schemas/cadastros/RESPONSABILIDADE.md).
- [app/services/ajuda_geral](../ajuda_geral/RESPONSABILIDADE.md).
- [app/services/gerais](../gerais/RESPONSABILIDADE.md).
