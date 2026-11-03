# Responsabilidade: app/services/sessoes

## Objetivo do módulo

Consultar e ocultar conversas do histórico.

## O que deve ser armazenado aqui

Formatação, consultas MongoDB por proprietário e exclusão lógica.

## Comportamento e limites atuais

Excluir marca esta_ativo=false e limpa cache; é diferente de encerrar sessão. Visualizações são revalidadas e incluídas quando autorizado pelo chamador.

Módulo pai: [app/services](../RESPONSABILIDADE.md).

## Funcionalidades disponíveis e arquivos

O catálogo registra os recursos existentes. Funções assíncronas usam `await`; ferramentas LangChain devem receber o contexto injetado. Símbolos com `_` são detalhes internos, cuja assinatura e regras devem ser conferidas antes de reutilizar.

### [__init__.py](__init__.py)

Interface do pacote: reúne importações públicas e recursos descritos abaixo.

- Auxiliares internos (reutilização deve preservar o contexto deste arquivo): `__getattr__`, `__dir__`.
- Constantes, aliases e estado de módulo: `_EXPORTACOES`.
- Importações/reexportações existentes: `from app.core.interfaces import resolver_exportacao as _resolver_exportacao`.

Exportações e proprietários (carregados sob demanda):

- `ErroConsultaHistorico` → `.historico` (`ErroConsultaHistorico`).
- `buscar_conversa` → `.historico` (`buscar_conversa`).
- `buscar_conversas_usuario` → `.historico` (`buscar_conversas_usuario`).
- `excluir_conversa` → `.historico` (`excluir_conversa`).

### [historico.py](historico.py)

Formata mensagens/conversas, consulta histórico próprio e faz exclusão lógica com erros próprios do serviço.

- Classe `ErroConsultaHistorico` (`Exception`).
  Métodos/validadores: `__init__(self, status_code: int, mensagem: str)`.
- `async excluir_conversa(session_id: str, usuario_id: int) -> bool`: Oculta conversa própria com exclusão lógica e remove cache da sessão.
- `async buscar_conversas_usuario(usuario_id: int, *, incluir_visualizacoes: bool=False) -> list[dict[str, Any]]`: Consulta conversas ativas do usuário e formata mensagens/payloads históricos.
- `async buscar_conversa(session_id: str, usuario_id: int, *, incluir_visualizacoes: bool=False) -> dict[str, Any] | None`: Obtém conversa ativa por proprietário e ID, com visualização quando permitido.
- Auxiliares internos (reutilização deve preservar o contexto deste arquivo): `_formatar_mensagens`, `_formatar_conversa`.
- Constantes, aliases e estado de módulo: `_PROJECAO`.

## Dependências internas observadas

Importações existentes nos arquivos desta pasta; não representam uma arquitetura desejada nem autorização para ampliar escopos.

- [app/core](../../core/RESPONSABILIDADE.md).
- [app/core/clients](../../core/clients/RESPONSABILIDADE.md).
- [app/memory/persistencia](../../memory/persistencia/RESPONSABILIDADE.md).
- [app/services/visualizacoes](../visualizacoes/RESPONSABILIDADE.md).
