# Responsabilidade: app/services/ordensServico

## Objetivo do módulo

Consultar ordens de serviço autorizadas.

## O que deve ser armazenado aqui

SQL de busca/listagem, filtros, janela de três meses e enums.

## Comportamento e limites atuais

Consulta até três OS recentes com filtros e escopo preservados. Calendário, códigos e ordenação reutilizam core/tempo e core/manutencao. O módulo histórico mantém os nomes antigos. Não há escrita de OS neste pacote.

Módulo pai: [app/services](../RESPONSABILIDADE.md).

## Funcionalidades disponíveis e arquivos

O catálogo registra os recursos existentes. Funções assíncronas usam `await`; ferramentas LangChain devem receber o contexto injetado. Símbolos com `_` são detalhes internos, cuja assinatura e regras devem ser conferidas antes de reutilizar.

### [__init__.py](__init__.py)

Interface do pacote: reúne importações públicas e recursos descritos abaixo.

- Auxiliares internos (reutilização deve preservar o contexto deste arquivo): `__getattr__`, `__dir__`.
- Constantes, aliases e estado de módulo: `_EXPORTACOES`.
- Importações/reexportações existentes: `from app.core.interfaces import resolver_exportacao as _resolver_exportacao`.

Exportações e proprietários (carregados sob demanda):

- `buscar_ordens_servico` → `.buscarOrdensServico` (`buscar_ordens_servico`).
- `consultar_minhas_ordens_servico` → `.buscarOrdensServico` (`consultar_minhas_ordens_servico`).
- `consultar_todas_ordens_servico` → `.buscarOrdensServico` (`consultar_todas_ordens_servico`).

### [buscarOrdensServico.py](buscarOrdensServico.py)

SQL de consulta de OS com filtros/escopo originais; enums/calendário são reutilizados de core.

- `async buscar_ordens_servico(usuario: UsuarioContexto, *, status: str | None=None, prioridade: str | None=None, categoria_problema: str | None=None, categoria_equipamento: str | None=None, local: str | None=None, termo: str | None=None, data_criacao_inicio: date | None=None, data_criacao_fim: date | None=None, data_prevista_inicio: date | None=None, data_prevista_fim: date | None=None) -> dict`: Busca OS com filtros opcionais dentro do escopo do usuario autenticado.
- `async consultar_minhas_ordens_servico(usuario: UsuarioContexto) -> dict`: Consulta OS atribuidas ao tecnico autenticado nos ultimos tres meses.
- `async consultar_todas_ordens_servico(usuario: UsuarioContexto) -> dict`: Consulta OS do endereco do gestor nos ultimos tres meses.
- Auxiliares internos (reutilização deve preservar o contexto deste arquivo): `_data_iso`, `_consultar_ordens_servico`.
- Constantes, aliases e estado de módulo: `registrador`.

## Dependências internas observadas

Importações existentes nos arquivos desta pasta; não representam uma arquitetura desejada nem autorização para ampliar escopos.

- [app/core](../../core/RESPONSABILIDADE.md).
- [app/core/apresentacao](../../core/apresentacao/RESPONSABILIDADE.md).
- [app/core/clients](../../core/clients/RESPONSABILIDADE.md).
- [app/schemas](../../schemas/RESPONSABILIDADE.md).
