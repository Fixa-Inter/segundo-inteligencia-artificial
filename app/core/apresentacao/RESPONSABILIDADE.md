# Responsabilidade: app/core/apresentacao

## Objetivo do módulo

Renderizar textos determinísticos compartilhados sem depender da orquestração.

## O que deve ser armazenado aqui

Templates de mensagens, propostas, promoções e avisos analíticos separados por assunto.

## Comportamento e limites atuais

Grafo, tools e serviços usam a mesma implementação. Este pacote não decide rotas, autentica usuários ou executa gravações. graph/respostas_padrao mantém os nomes históricos e a seleção específica do fluxo.

Módulo pai: [app/core](../RESPONSABILIDADE.md).

## Funcionalidades disponíveis e arquivos

O catálogo registra os recursos existentes. Funções assíncronas usam `await`; ferramentas LangChain devem receber o contexto injetado. Símbolos com `_` são detalhes internos, cuja assinatura e regras devem ser conferidas antes de reutilizar.

### [__init__.py](__init__.py)

Interface do pacote: reúne importações públicas e recursos descritos abaixo.

- Auxiliares internos (reutilização deve preservar o contexto deste arquivo): `__getattr__`, `__dir__`.
- Constantes, aliases e estado de módulo: `_EXPORTACOES`.
- Importações/reexportações existentes: `from app.core.interfaces import resolver_exportacao as _resolver_exportacao`.

Exportações e proprietários (carregados sob demanda):

- `_avisos_base` → `.visualizacoes` (`_avisos_base`).
- `avisos_base` → `.visualizacoes` (`_avisos_base`).
- `escolher_resposta` → `.textos` (`escolher_resposta`).
- `formatar_resposta` → `.textos` (`formatar_resposta`).
- `pergunta_opcionais_compra` → `.compras` (`pergunta_opcionais_compra`).
- `resposta_bloqueio_seguranca` → `.textos` (`resposta_bloqueio_seguranca`).
- `resposta_busca_compra` → `.compras` (`resposta_busca_compra`).
- `resposta_cobertura_lojas` → `.compras` (`resposta_cobertura_lojas`).
- `resposta_consulta_visualizacao` → `.visualizacoes` (`resposta_consulta_visualizacao`).
- `resposta_erro_compra` → `.compras` (`resposta_erro_compra`).
- `resposta_ofertas` → `.compras` (`resposta_ofertas`).
- `resultado_indeterminado` → `.textos` (`resultado_indeterminado`).
- `resumo_atualizacao` → `.propostas` (`resumo_atualizacao`).
- `resumo_confirmacao` → `.propostas` (`resumo_confirmacao`).
- `texto_resultados` → `.textos` (`texto_resultados`).

### [compras.py](compras.py)

Renderização determinística de compras, usada pelo grafo, tools e serviços.

- `resposta_ofertas(ofertas: list[dict], diferencas: str) -> str`: Renderiza ofertas e ressalvas com os dados reais recebidos.
- `resposta_cobertura_lojas(nomes: list[str]) -> str`: Apresenta lojas cadastradas sem afirmar oferta ativa para o item.
- `pergunta_opcionais_compra(campos: list[str], questao_compatibilidade: str | None) -> str`: Renderiza campos opcionais de compra e questão de compatibilidade.
- `resposta_busca_compra(produtos: list[dict], ofertas: list[dict], diferencas: str) -> str`: Escolhe apresentação de ofertas ou ausência de promoções ativas.
- `resposta_erro_compra(codigo: str, erro) -> str`: Seleciona mensagem conforme código de falha da pesquisa.

### [propostas.py](propostas.py)

Renderização determinística de propostas, usada pelo grafo, tools e serviços.

- `resumo_confirmacao(rascunho: dict) -> str`: Renderiza resumo determinístico dos dados/alterações da proposta.
- `resumo_atualizacao(rascunho: dict) -> str`: Renderiza identificação do registro ou proposta final das alterações/fotos.

### [textos.py](textos.py)

Renderização determinística de textos, usada pelo grafo, tools e serviços.

- `formatar_resposta(chave: str, **valores) -> str`: Interpola somente um template conhecido do catálogo de mensagens.
- `escolher_resposta(condicao, quando_sim: str, quando_nao: str) -> str`: Seleciona um texto do catálogo a partir de um resultado já apurado.
- `resposta_bloqueio_seguranca(categoria: str) -> dict | None`: Obtém motivo/texto padronizados para a categoria de segurança.
- `resultado_indeterminado() -> dict`: Retorna orientação que impede declarar sucesso/falha definitiva ou repetir envio incerto.
- `texto_resultados(resultados: list[dict]) -> str`: Renderiza resultados separados de operações, preservando sucessos e falhas parciais.

### [visualizacoes.py](visualizacoes.py)

Renderização determinística de visualizacoes, usada pelo grafo, tools e serviços.

- `resposta_consulta_visualizacao(periodos_parciais: bool) -> str`: Seleciona texto de consulta concluída, incluindo referência a períodos parciais quando necessário.
- Auxiliares internos (reutilização deve preservar o contexto deste arquivo): `_avisos_base`.

## Dependências internas observadas

Importações existentes nos arquivos desta pasta; não representam uma arquitetura desejada nem autorização para ampliar escopos.

- [app/core](../RESPONSABILIDADE.md).
