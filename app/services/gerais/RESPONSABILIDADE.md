# Responsabilidade: app/services/gerais

## Objetivo do módulo

Oferecer serviços de identidade, unidade e decisão JEV.

## O que deve ser armazenado aqui

Perfil FIXA, resolução de unidade, cliente JEV e classificação/roteamento.

## Comportamento e limites atuais

rotear_jev existe; supervisor atual usa agents/orquestrador. consultar_jev centraliza transporte/métricas; ler_choice e ler_noul validam respostas.

Módulo pai: [app/services](../RESPONSABILIDADE.md).

## Funcionalidades disponíveis e arquivos

O catálogo registra os recursos existentes. Funções assíncronas usam `await`; ferramentas LangChain devem receber o contexto injetado. Símbolos com `_` são detalhes internos, cuja assinatura e regras devem ser conferidas antes de reutilizar.

### [__init__.py](__init__.py)

Interface do pacote: reúne importações públicas e recursos descritos abaixo.

- Auxiliares internos (reutilização deve preservar o contexto deste arquivo): `__getattr__`, `__dir__`.
- Constantes, aliases e estado de módulo: `_EXPORTACOES`.
- Importações/reexportações existentes: `from app.core.interfaces import resolver_exportacao as _resolver_exportacao`.

Exportações e proprietários (carregados sob demanda):

- `CRITERIOS_INTENCAO` → `.rotear` (`CRITERIOS_INTENCAO`).
- `DecisaoIncertaJEV` → `.jev` (`DecisaoIncertaJEV`).
- `ErroConsultaPerfil` → `.perfil` (`ErroConsultaPerfil`).
- `ErroJEV` → `.jev` (`ErroJEV`).
- `INSTRUCAO_INTENCAO` → `.rotear` (`INSTRUCAO_INTENCAO`).
- `consultar_jev` → `.jev` (`consultar_jev`).
- `consultar_perfil` → `.perfil` (`consultar_perfil`).
- `interpretar_cadastro` → `.cadastros` (`interpretar_cadastro`).
- `julgar_jev` → `.julgar` (`julgar_jev`).
- `ler_choice` → `.jev` (`ler_choice`).
- `ler_noul` → `.jev` (`ler_noul`).
- `obter_unidade_id` → `.unidade` (`obter_unidade_id`).
- `rotear_jev` → `.rotear` (`rotear_jev`).

### [cadastros.py](cadastros.py)

Interpretação comum de respostas de cadastro FIXA, sem executar/repetir POST.

- `interpretar_cadastro(resposta, *, access_token, titulo, mensagem_sucesso, mensagem_recusa, indeterminado, campo_id, incluir_status_backend=False, detalhes_indeterminado=True) -> dict`: Preserva diferenças explícitas entre solicitação, ocorrência e evento.

### [jev.py](jev.py)

Cliente e validação das decisões estruturadas do JEV.

- Classe `ErroJEV` (`RuntimeError`): A decisão não pôde ser obtida ou validada.
- Classe `DecisaoIncertaJEV` (`ErroJEV`): A resposta válida não teve certeza suficiente para alterar o fluxo.
- `async consultar_jev(estado: dict, perguntas: dict, *, operacao: str='outra') -> dict`: Consulta decisão estruturada JEV com tratamento de transporte, uso de tokens e métricas.
- `ler_choice(respostas: dict, nome: str, opcoes: set[str]) -> tuple[str, float]`: Valida opção/confiabilidade de uma decisão fechada do JEV.
- `ler_noul(respostas: dict, nome: str) -> float`: Valida estrutura e pontuação de uma avaliação noul do JEV.
- Constantes, aliases e estado de módulo: `registrador`.

### [julgar.py](julgar.py)

Classificação fechada pelo JEV usada pelo endpoint de problemas.

- `async julgar_jev(estado: dict, chave_texto: str, agente: str, prompt: str, instrucao: str, criterio: dict, nouls: dict, nao_classificavel: str | None=None) -> dict`: Aplica escolha de categoria e verificações noul para classificação do endpoint de problemas.
- Auxiliares internos (reutilização deve preservar o contexto deste arquivo): `_publicar`.

### [perfil.py](perfil.py)

Consulta HTTP do perfil FIXA e exceção com status/mensagem.

- Classe `ErroConsultaPerfil` (`Exception`).
  Métodos/validadores: `__init__(self, status_code: int, mensagem: str)`.
- `async consultar_perfil(access_token: str) -> dict`: Consulta perfil pela API FIXA usando Bearer e traduz falhas para ErroConsultaPerfil.

### [rotear.py](rotear.py)

Decisão de intenção do chat pelo JEV.

- `async rotear_jev(estado: dict, pergunta: str) -> dict`: Alternativa de roteamento estruturado via JEV; não é o roteador chamado pelo supervisor atual.
- Auxiliares internos (reutilização deve preservar o contexto deste arquivo): `_resumir_propostas`.
- Constantes, aliases e estado de módulo: `CRITERIOS_INTENCAO`, `INSTRUCAO_INTENCAO`.

### [unidade.py](unidade.py)

Resolve a unidade do usuário autenticado a partir do banco FIXA.

- `async obter_unidade_id(usuario: UsuarioContexto) -> int`: Resolve e valida a unidade atual do usuário autenticado por consulta PostgreSQL.

## Dependências internas observadas

Importações existentes nos arquivos desta pasta; não representam uma arquitetura desejada nem autorização para ampliar escopos.

- [app/core](../../core/RESPONSABILIDADE.md).
- [app/core/apresentacao](../../core/apresentacao/RESPONSABILIDADE.md).
- [app/core/clients](../../core/clients/RESPONSABILIDADE.md).
- [app/observability](../../observability/RESPONSABILIDADE.md).
- [app/schemas](../../schemas/RESPONSABILIDADE.md).
