# Responsabilidade: app/guardrails

## Objetivo do módulo

Validar mensagens e proteger dados pessoais.

## O que deve ser armazenado aqui

Anonimização, detecção de pedidos bloqueados e sanitização de saída.

## Comportamento e limites atuais

Regras e modelo de segurança preservados; cliente LLM compartilhado vem de core/clients. Anonimização/proteção de saída não substituem autenticação/autorização de dados.

Módulo pai: [app](../RESPONSABILIDADE.md).

## Funcionalidades disponíveis e arquivos

O catálogo registra os recursos existentes. Funções assíncronas usam `await`; ferramentas LangChain devem receber o contexto injetado. Símbolos com `_` são detalhes internos, cuja assinatura e regras devem ser conferidas antes de reutilizar.

### [__init__.py](__init__.py)

Interface do pacote: reúne importações públicas e recursos descritos abaixo.

- Auxiliares internos (reutilização deve preservar o contexto deste arquivo): `__getattr__`, `__dir__`.
- Constantes, aliases e estado de módulo: `_EXPORTACOES`.
- Importações/reexportações existentes: `from app.core.interfaces import resolver_exportacao as _resolver_exportacao`.

Exportações e proprietários (carregados sob demanda):

- `ClassificacaoSeguranca` → `.validacao` (`ClassificacaoSeguranca`).
- `PADROES_DADOS_INTERNOS` → `.validacao` (`PADROES_DADOS_INTERNOS`).
- `PADROES_INJECAO` → `.validacao` (`PADROES_INJECAO`).
- `PII` → `.validacao` (`PII`).
- `PROMPT_CLASSIFICADOR` → `.validacao` (`PROMPT_CLASSIFICADOR`).
- `anonimizar_entrada` → `.validacao` (`anonimizar_entrada`).
- `aprovar` → `.validacao` (`aprovar`).
- `bloquear` → `.validacao` (`bloquear`).
- `classificador_seguranca` → `.validacao` (`classificador_seguranca`).
- `desanonimizar_saida` → `.validacao` (`desanonimizar_saida`).
- `proteger_entrada` → `.validacao` (`proteger_entrada`).
- `proteger_saida` → `.validacao` (`proteger_saida`).
- `remover_dados_pessoais_saida` → `.validacao` (`remover_dados_pessoais_saida`).

### [validacao.py](validacao.py)

Anonimiza PII, detecta injeção/extração de segredos, classifica segurança e protege saída.

- Classe `ClassificacaoSeguranca` (`BaseModel`).
  Campos/atributos declarados: `categoria: Literal['APROVADO', 'PERIGOSO', 'ILICITO']`, `justificativa: str`.
- `bloquear(motivo: str, mensagem: str) -> dict`: Monta resultado estruturado de entrada bloqueada com motivo/mensagem.
- `aprovar() -> dict`: Monta resultado estruturado de entrada aprovada.
- `anonimizar_entrada(texto: str) -> tuple[str, dict[str, str]]`: Substitui PII por tokens temporários e devolve mapa das substituições.
- `desanonimizar_saida(texto: str, mapa: dict[str, str], *, restaurar: bool=False) -> str`: Omite tokens de PII por padrão ou restaura valores quando explicitamente habilitado.
- `remover_dados_pessoais_saida(texto: str) -> str`: Remove padrões de PII ainda presentes no texto de saída.
- `proteger_entrada(mensagem_anonimizada: str) -> dict`: Combina regras de injeção/dados internos com classificação de segurança do modelo.
- `proteger_saida(resposta: str, mapa_pii: dict[str, str], *, restaurar_pii: bool=False) -> dict`: Aplica tratamento de tokens e remoção de dados pessoais na resposta.
- Constantes, aliases e estado de módulo: `PII`, `PADROES_INJECAO`, `PADROES_DADOS_INTERNOS`, `classificador_seguranca`, `PROMPT_CLASSIFICADOR`.

## Dependências internas observadas

Importações existentes nos arquivos desta pasta; não representam uma arquitetura desejada nem autorização para ampliar escopos.

- [app/core](../core/RESPONSABILIDADE.md).
- [app/core/apresentacao](../core/apresentacao/RESPONSABILIDADE.md).
- [app/core/clients](../core/clients/RESPONSABILIDADE.md).
