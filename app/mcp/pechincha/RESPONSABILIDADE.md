# Responsabilidade: app/mcp/pechincha

## Objetivo do módulo

Consultar promoções no MCP público Pechincha.ai.

## O que deve ser armazenado aqui

Streamable HTTP/JSON-RPC, argumentos de busca e normalização.

## Comportamento e limites atuais

Wrappers de search_deals, list_stores e list_categories. Inicializa sessão, interpreta JSON/SSE, trata erros e emite métricas. O endpoint público é usado sem chave de API.

Módulo pai: [app/mcp](../RESPONSABILIDADE.md).

## Funcionalidades disponíveis e arquivos

O catálogo registra os recursos existentes. Funções assíncronas usam `await`; ferramentas LangChain devem receber o contexto injetado. Símbolos com `_` são detalhes internos, cuja assinatura e regras devem ser conferidas antes de reutilizar.

### [__init__.py](__init__.py)

Interface do pacote: reúne importações públicas e recursos descritos abaixo.

- Auxiliares internos (reutilização deve preservar o contexto deste arquivo): `__getattr__`, `__dir__`.
- Constantes, aliases e estado de módulo: `_EXPORTACOES`.
- Importações/reexportações existentes: `from app.core.interfaces import resolver_exportacao as _resolver_exportacao`.

Exportações e proprietários (carregados sob demanda):

- `BuscaOfertas` → `.modelos` (`BuscaOfertas`).
- `ErroPechincha` → `.transporte` (`ErroPechincha`).
- `buscar_ofertas` → `.ferramentas` (`buscar_ofertas`).
- `chamar_ferramenta` → `.transporte` (`chamar_ferramenta`).
- `listar_categorias` → `.ferramentas` (`listar_categorias`).
- `listar_lojas` → `.ferramentas` (`listar_lojas`).
- `normalizar_ofertas` → `.modelos` (`normalizar_ofertas`).

### [ferramentas.py](ferramentas.py)

Chamadas às três ferramentas Pechincha.ai usadas no FIXA.

- `async buscar_ofertas(busca: BuscaOfertas) -> dict`: Chama search_deals e normaliza ofertas e metadados de busca.
- `async listar_lojas(query: str | None=None) -> list[dict]`: Chama list_stores e valida a lista de lojas recebida.
- `async listar_categorias() -> list[dict]`: Chama list_categories e valida a lista de categorias recebida.

### [modelos.py](modelos.py)

Contrato de entrada e normalização das respostas de promoções.

- Classe `BuscaOfertas` (`BaseModel`).
  Campos/atributos declarados: `query: str`, `store: str | None`, `category: str | None`, `min_price: float | None`, `max_price: float | None`, `page: int`.
  Métodos/validadores: `validar_faixa(self)`.
- `normalizar_ofertas(conteudo: dict) -> dict`: Valida formato e projeta título, preço, loja, descrição e URL das promoções recebidas.
- Auxiliares internos (reutilização deve preservar o contexto deste arquivo): `_texto`, `_url`.

### [transporte.py](transporte.py)

Transporte Streamable HTTP e tratamento dos erros do MCP.

- Classe `ErroPechincha` (`RuntimeError`).
  Métodos/validadores: `__init__(self, codigo: str, mensagem: str)`.
- `async chamar_ferramenta(nome: str, argumentos: dict) -> dict`: Abre uma sessão MCP, chama uma ferramenta e devolve seu conteúdo estruturado.
- Auxiliares internos (reutilização deve preservar o contexto deste arquivo): `_ler_resposta`, `_post`.

## Dependências internas observadas

Importações existentes nos arquivos desta pasta; não representam uma arquitetura desejada nem autorização para ampliar escopos.

- [app/core](../../core/RESPONSABILIDADE.md).
- [app/observability](../../observability/RESPONSABILIDADE.md).
