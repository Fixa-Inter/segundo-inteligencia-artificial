# Responsabilidade: app/scripts

## Objetivo do módulo

Disponibilizar comandos operacionais explícitos.

## O que deve ser armazenado aqui

Entradas de scripts que coordenam recursos existentes.

## Comportamento e limites atuais

Comandos explícitos: ingerir_faq e migrar_timestamps_mensagens. Ingestão altera FAQ vetorial por perfil. Migração preenche somente timestamps ausentes com null, preservando horários reais. Nenhum comando é disparado automaticamente no startup.

Módulo pai: [app](../RESPONSABILIDADE.md).

## Funcionalidades disponíveis e arquivos

O catálogo registra os recursos existentes. Funções assíncronas usam `await`; ferramentas LangChain devem receber o contexto injetado. Símbolos com `_` são detalhes internos, cuja assinatura e regras devem ser conferidas antes de reutilizar.

### [__init__.py](__init__.py)

Interface do pacote: reúne importações públicas e recursos descritos abaixo.

- Auxiliares internos (reutilização deve preservar o contexto deste arquivo): `__getattr__`, `__dir__`.
- Constantes, aliases e estado de módulo: `_EXPORTACOES`.
- Importações/reexportações existentes: `from app.core.interfaces import resolver_exportacao as _resolver_exportacao`.

Exportações e proprietários (carregados sob demanda):

- `main` → `.ingerir_faq` (`main`).
- `descobrir_documentos_faq` → `.ingerir_faq`: monta o corpus completo de cada perfil antes da ingestão.
- `DIRETORIO_DOCUMENTOS_FAQ` e `PERFIS_FAQ` → `.ingerir_faq`: raiz `dados/` e perfis indexados; administrador reutiliza gestor na busca.
- `migrar_timestamps_mensagens` → `.migrar_timestamps_mensagens` (`migrar_timestamps_mensagens`).

### [ingerir_faq.py](ingerir_faq.py)

Seleção de fontes Markdown e entrada assíncrona de ingestão por perfil. Usa `dados/`, não `docs/`, independentemente da pasta de execução. Não inclui `RESPONSABILIDADE.md` nem formatos diferentes de Markdown na descoberta automática.

- `descobrir_documentos_faq(diretorio_dados=...)`: retorna, para cada perfil, todos os Markdown de `fixa/` e somente os de `mobile/<perfil>/`, incluindo subpastas. Rejeita ausência de documentos comuns ou de qualquer perfil antes de iniciar atualizações.
- `async main()`: chama `ingerir_faq` uma vez por perfil com seu corpus completo, para que os arquivos não substituam uns aos outros.

### [migrar_timestamps_mensagens.py](migrar_timestamps_mensagens.py)

Migração explícita e idempotente de mensagens antigas sem horário conhecido.

- `async migrar_timestamps_mensagens() -> int`: Preenche somente timestamps ausentes com null; preserva os horários reais.

## Comandos explícitos

- `python -m app.scripts.ingerir_faq`: ingere `dados/fixa/*.md` para solicitante, técnico e gestor, somando os manuais da pasta mobile de cada perfil. O administrador acessa o FAQ do gestor pela regra existente. O comando atualiza o Qdrant e gera embeddings pelo provedor configurado; não roda no startup. Os antigos caminhos `CAMINHO_PDF_FAQ_*` não são usados por este comando.
- `python -m app.scripts.migrar_timestamps_mensagens`: preenche apenas horários ausentes com null e retorna quantidade de documentos alterados. É idempotente e preserva timestamps existentes.

A ingestão é testada sem rede com vetores simulados e Qdrant em memória, incluindo isolamento, substituição e falhas. A migração de timestamps é testada com MongoDB simulado. Testar esses recursos não executa comandos nos bancos reais.

## Dependências internas observadas

Importações existentes nos arquivos desta pasta; não representam uma arquitetura desejada nem autorização para ampliar escopos.

- [app/core](../core/RESPONSABILIDADE.md).
- [app/core/clients](../core/clients/RESPONSABILIDADE.md).
- [app/memory/embedding](../memory/embedding/RESPONSABILIDADE.md).
