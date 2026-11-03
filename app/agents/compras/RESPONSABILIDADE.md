# Responsabilidade: app/agents/compras

## Objetivo do módulo

Separar as etapas de coleta e comparação de promoções.

## O que deve ser armazenado aqui

Extração de requisitos, conversão de filtros, avaliação e apresentação de ofertas.

## Comportamento e limites atuais

Somente o item é obrigatório. Requisitos são conferidos contra trechos dos anúncios. A coordenação fica em agents/analista_compras.py; persistência em memory/persistencia/analise_compra.py.

Módulo pai: [app/agents](../RESPONSABILIDADE.md).

## Funcionalidades disponíveis e arquivos

O catálogo registra os recursos existentes. Funções assíncronas usam `await`; ferramentas LangChain devem receber o contexto injetado. Símbolos com `_` são detalhes internos, cuja assinatura e regras devem ser conferidas antes de reutilizar.

### [__init__.py](__init__.py)

Interface do pacote: reúne importações públicas e recursos descritos abaixo.

- Auxiliares internos (reutilização deve preservar o contexto deste arquivo): `__getattr__`, `__dir__`.
- Constantes, aliases e estado de módulo: `_EXPORTACOES`.
- Importações/reexportações existentes: `from app.core.interfaces import resolver_exportacao as _resolver_exportacao`.

Exportações e proprietários (carregados sob demanda):

- `AvaliacaoOferta` → `.avaliacao` (`AvaliacaoOferta`).
- `AvaliacoesOfertas` → `.avaliacao` (`AvaliacoesOfertas`).
- `DadosCompra` → `.coleta` (`DadosCompra`).
- `Verificacao` → `.avaliacao` (`Verificacao`).
- `avaliar` → `.avaliacao` (`avaliar`).
- `campos_prioritarios_ausentes` → `.coleta` (`campos_prioritarios_ausentes`).
- `consultar` → `.consulta` (`consultar`).
- `dados_persistiveis` → `.coleta` (`dados_persistiveis`).
- `extrair` → `.coleta` (`extrair`).
- `normalizar` → `.avaliacao` (`normalizar`).
- `oferta_sem_avaliacao` → `.avaliacao` (`oferta_sem_avaliacao`).
- `opcionais_ausentes` → `.coleta` (`opcionais_ausentes`).
- `pergunta_opcionais` → `.coleta` (`pergunta_opcionais`).
- `resposta_ofertas` → `.respostas` (`resposta_ofertas`).
- `texto_curto` → `.avaliacao` (`texto_curto`).
- `url_produto` → `.avaliacao` (`url_produto`).

### [avaliacao.py](avaliacao.py)

Confere requisitos somente contra o texto das promoções recebidas.

- Classe `Verificacao` (`BaseModel`).
  Campos/atributos declarados: `requisito: str`, `trecho_anuncio: str`.
- Classe `AvaliacaoOferta` (`BaseModel`).
  Campos/atributos declarados: `indice: int`, `confirmados: list[Verificacao]`, `incompativeis: list[Verificacao]`.
- Classe `AvaliacoesOfertas` (`BaseModel`).
  Campos/atributos declarados: `ofertas: list[AvaliacaoOferta]`, `diferencas: str`.
- `normalizar(texto: str) -> str`: Normaliza texto de anúncio/requisito para comparação sem acentos e espaços redundantes.
- `url_produto(valor: object) -> str | None`: Aceita link HTTP(S) válido da oferta ou devolve None.
- `texto_curto(valor: object, limite: int) -> str`: Normaliza espaços e limita texto de apresentação da oferta.
- `oferta_sem_avaliacao(dados: DadosCompra, produto: dict) -> dict | None`: Projeta campos da oferta recebida sem inventar compatibilidade.
- `async avaliar(dados: DadosCompra, produtos: list[dict]) -> tuple[list[dict], str]`: Compara requisitos às ofertas e valida trechos citados contra anúncios recebidos.

### [coleta.py](coleta.py)

Extração e validação dos dados declarados na conversa de compra.

- Classe `DadosCompra` (`BaseModel`).
  Campos/atributos declarados: `item: str | None`, `requisitos_obrigatorios: list[str] | None`, `quantidade: str | None`, `aplicacao: str | None`, `loja: str | None`, `categoria: str | None`, `min_price: float | None`, `max_price: float | None`, `preferencias: str | None`, `exclusoes: str | None`, `recusou_opcionais: bool`, `questao_compatibilidade: str | None`.
- `dados_persistiveis(dados: DadosCompra) -> dict`: Projeta dados declarados da compra para o rascunho.
- `campos_prioritarios_ausentes(dados: DadosCompra) -> list[str]`: Identifica ausência do nome do item, único campo obrigatório.
- `opcionais_ausentes(dados: DadosCompra) -> list[str]`: Lista filtros/detalhes opcionais ainda não informados.
- `pergunta_opcionais(dados: DadosCompra) -> str`: Renderiza pergunta opcional de filtros/detalhes da compra.
- `async extrair(mensagem: str, anterior: dict | None, pergunta_feita: bool) -> DadosCompra`: Extrai DadosCompra da mensagem usando dados anteriores como contexto.

### [consulta.py](consulta.py)

Converte filtros informados pela pessoa nos parâmetros aceitos pelo MCP.

- `async consultar(dados: DadosCompra) -> dict`: Resolve loja/categoria para slugs conhecidos e chama busca de ofertas.
- Auxiliares internos (reutilização deve preservar o contexto deste arquivo): `_normalizar`, `_slug_exato`.

### [respostas.py](respostas.py)

Apresentação de promoções e ressalvas ao usuário.

- `resposta_ofertas(ofertas: list[dict], diferencas: str) -> str`: Renderiza ofertas e ressalvas com os dados reais recebidos.

## Dependências internas observadas

Importações existentes nos arquivos desta pasta; não representam uma arquitetura desejada nem autorização para ampliar escopos.

- [app/agents](../RESPONSABILIDADE.md).
- [app/core](../../core/RESPONSABILIDADE.md).
- [app/core/apresentacao](../../core/apresentacao/RESPONSABILIDADE.md).
- [app/mcp/pechincha](../../mcp/pechincha/RESPONSABILIDADE.md).
