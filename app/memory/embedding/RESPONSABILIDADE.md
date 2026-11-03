# Responsabilidade: app/memory/embedding

## Objetivo do módulo

Gerar embeddings e ingerir a base de FAQ.

## O que deve ser armazenado aqui

Vetorizadores sob demanda, IDs determinísticos e leitura/ingestão de corpus Markdown ou PDF por perfil.

## Comportamento e limites atuais

Reutiliza modelos por dimensão. Ingestão recebe todos os documentos de um perfil juntos, substitui somente esse perfil e não roda no startup. A seleção de fontes e distribuição de conteúdo pertencem ao comando de `app/scripts`, que usa `dados/`.

Todos os documentos e embeddings são preparados antes de alterar o Qdrant. Após publicar os lotes, a limpeza remove somente pontos do perfil que não pertencem à nova ingestão. Se um lote falhar, os antigos não são apagados. A troca não é transacional: versões podem coexistir durante publicação ou após falha de envio/limpeza; uma nova execução completa remove os pontos obsoletos. Não executar duas ingestões simultâneas do mesmo perfil.

Módulo pai: [app/memory](../RESPONSABILIDADE.md).

## Funcionalidades disponíveis e arquivos

O catálogo registra os recursos existentes. Funções assíncronas usam `await`; ferramentas LangChain devem receber o contexto injetado. Símbolos com `_` são detalhes internos, cuja assinatura e regras devem ser conferidas antes de reutilizar.

### [__init__.py](__init__.py)

Interface do pacote: reúne importações públicas e recursos descritos abaixo.

- Auxiliares internos (reutilização deve preservar o contexto deste arquivo): `__getattr__`, `__dir__`.
- Constantes, aliases e estado de módulo: `_EXPORTACOES`.
- Importações/reexportações existentes: `from app.core.interfaces import resolver_exportacao as _resolver_exportacao`.

Exportações e proprietários (carregados sob demanda):

- `SOBREPOSICAO_TRECHOS` → `.popular_banco_vetorial` (`SOBREPOSICAO_TRECHOS`).
- `TAMANHO_LOTE` → `.popular_banco_vetorial` (`TAMANHO_LOTE`).
- `TAMANHO_TRECHO` → `.popular_banco_vetorial` (`TAMANHO_TRECHO`).
- `carregar_documentos_faq` → `.popular_banco_vetorial` (`carregar_documentos_faq`).
- `gerar_ponto_id` → `.configuracao` (`gerar_ponto_id`).
- `gerar_vetor_documento` → `.configuracao` (`gerar_vetor_documento`).
- `gerar_vetor_operacional` → `.configuracao` (`gerar_vetor_operacional`).
- `gerar_vetores_documentos` → `.configuracao` (`gerar_vetores_documentos`).
- `ingerir_faq` → `.popular_banco_vetorial` (`ingerir_faq`).
- `obter_vetorizador` → `.configuracao` (`obter_vetorizador`).
- `obter_vetorizador_operacional` → `.configuracao` (`obter_vetorizador_operacional`).

### [configuracao.py](configuracao.py)

Recursos deste arquivo: Inicialização sob demanda: importar o projeto não exige credenciais. Gera embedding de texto de FAQ/histórico. Usado pelo fluxo de embedding.

- `obter_vetorizador() -> OpenAIEmbeddings`: Inicialização sob demanda: importar o projeto não exige credenciais.
- `async gerar_vetor_documento(texto: str) -> list[float]`: Gera embedding de texto de FAQ/histórico.
- `async gerar_vetores_documentos(textos: list[str]) -> list[list[float]]`: Gera embeddings de lote de documentos.
- `obter_vetorizador_operacional() -> OpenAIEmbeddings`: Reutiliza vetorizador com a dimensão configurada para dados operacionais.
- `async gerar_vetor_operacional(texto: str) -> list[float]`: Gera/valida vetor de texto operacional.
- `gerar_ponto_id(cnpj_endereco: str, campo_id: int) -> str`: Contrato para o indexador: UUID5(NAMESPACE_URL, 'sede:id_operacional').

### [popular_banco_vetorial.py](popular_banco_vetorial.py)

Leitura e indexação vetorial do corpus completo de um perfil. Preserva tamanho de chunk 700, sobreposição 150 e lotes de 50. O payload mantém `page_content`, `perfil`, `page_number` e `source`, compatíveis com a busca existente.

- `carregar_documentos_faq(caminhos) -> list[Document]`: recebe um caminho ou iterável de caminhos, deduplica arquivos e lê Markdown UTF-8 com ou sem BOM, ou PDF pelo carregador existente. Preserva origem e páginas. Recusa lista vazia, arquivo ausente, conteúdo vazio e formato não suportado antes da gravação.
- `async ingerir_faq(caminho_pdf, perfil: str) -> int`: aceita caminho único ou iterável, prepara todos os vetores, publica o corpus e limpa pontos antigos apenas de solicitante, técnico ou gestor. Retorna o total de chunks. O argumento `caminho_pdf` mantém seu nome para compatibilidade com chamadas legadas, embora também aceite Markdown e vários arquivos. Falha ou divergência na quantidade de embeddings impede mutações; falha de publicação impede a limpeza; falha de limpeza é propagada.
- Constantes, aliases e estado de módulo: `TAMANHO_TRECHO`, `SOBREPOSICAO_TRECHOS`, `TAMANHO_LOTE`.

## Dependências internas observadas

Importações existentes nos arquivos desta pasta; não representam uma arquitetura desejada nem autorização para ampliar escopos.

- [app/core](../../core/RESPONSABILIDADE.md).
- [app/core/clients](../../core/clients/RESPONSABILIDADE.md).
