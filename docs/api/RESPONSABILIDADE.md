# Responsabilidade: docs/api

## Objetivo do módulo

Guardar contrato de referência da API FIXA.

## O que deve ser armazenado aqui

Snapshot OpenAPI swagger.json com endpoints, DTOs e schemas.

## Comportamento e limites atuais

Descreve o sistema externo; não é o OpenAPI FastAPI local. Endpoint documentado não implica ferramenta implementada.

Módulo pai: [docs](../RESPONSABILIDADE.md).

## Funcionalidades disponíveis e arquivos

Os arquivos abaixo são referências ou configuração; não expõem métodos Python.

### [swagger.json](swagger.json)

Snapshot do contrato OpenAPI da API FIXA externa.

### Endpoints de referência

| Caminho externo | Métodos |
| --- | --- |
| `/api/v1/tarefas` | POST, PATCH |
| `/api/v1/solicitacoes` | GET, POST, PATCH |
| `/api/v1/os` | GET, POST, PATCH |
| `/api/v1/ocorrencias` | GET, POST, PATCH |
| `/api/v1/observacoes-conclusao` | GET, POST, PATCH |
| `/api/v1/eventos` | GET, POST, PATCH |
| `/api/v1/equipamentos` | POST, PATCH |
| `/api/v1/equipamentos/modelos` | GET, POST, PATCH |
| `/api/v1/equipamentos/marcas` | GET, POST, PATCH |
| `/api/v1/equipamentos/categorias` | GET, POST, PATCH |
| `/api/v1/auth/validar-codigo` | POST |
| `/api/v1/auth/redefinir-senha` | POST |
| `/api/v1/auth/login` | POST |
| `/api/v1/auth/login/google` | POST |
| `/api/v1/auth/esqueceu-senha/{email}` | POST |
| `/api/v1/auth/cadastro` | POST |
| `/api/v1/tecnicos/competencias` | PATCH |
| `/api/v1/solicitacoes/status` | PATCH |
| `/api/v1/perfil` | GET, PATCH |
| `/api/v1/tecnicos` | GET |
| `/api/v1/tecnicos/recomendar/{categoriaProblema}` | GET |
| `/api/v1/tecnicos/os/{usuarioId}` | GET |
| `/api/v1/tecnicos/competencias/{usuarioId}` | GET |
| `/api/v1/tarefas/{ordemServicoId}` | GET |
| `/api/v1/tarefas/selecionar/{tarefaId}` | GET |
| `/api/v1/solicitacoes/selecionar/{problemaId}` | GET |
| `/api/v1/solicitacoes/minhas` | GET |
| `/api/v1/os/{ordemServicoId}` | GET, DELETE |
| `/api/v1/os/minhas` | GET |
| `/api/v1/ocorrencias/{ocorrenciaId}` | GET, DELETE |
| `/api/v1/ocorrencias/minhas` | GET |
| `/api/v1/observacoes-conclusao/{id}` | GET, DELETE |
| `/api/v1/observacoes-conclusao/minhas` | GET |
| `/api/v1/local-unidade` | GET |
| `/api/v1/eventos/{eventoId}` | GET, DELETE |
| `/api/v1/equipamentos/{equipamentoId}` | GET, DELETE |
| `/api/v1/equipamentos/modelos/{modeloEquipamentoId}` | GET, DELETE |
| `/api/v1/equipamentos/modelo/{modeloEquipamentoId}` | GET |
| `/api/v1/equipamentos/marcas/{marcaEquipamentoId}` | GET, DELETE |
| `/api/v1/equipamentos/categorias/{categoriaEquipamentoId}` | GET |
| `/api/v1/auth/instituicoes` | GET |
| `/api/v1/auth/instituicoes/{instituicaoId}/unidades` | GET |
| `/api/v1/tarefas/{tarefaId}` | DELETE |
| `/api/v1/solicitacoes/{problemaId}` | DELETE |
| `/api/v1/equipamentos/categorias/{categoriaId}` | DELETE |

### Schemas e campos de referência

Os tipos, obrigatoriedade, limites e descrições completos permanecem no Swagger. Estes nomes são um índice para localizar/reutilizar o contrato.

- `TarefaCriarInputDTO`: `ordemServicoId`, `statusOrdemServico`, `titulo`, `descricao`.
- `TarefaOutputDTO`: `id`, `titulo`, `descricao`, `status`, `usuarioResponsavel`, `dataCriacao`.
- `ProblemaCriarInputDTO`: `titulo`, `descricaoProblema`, `localUnidadeID`, `descricaoLocal`, `categoriaEquipamentoId`, `urlsFoto`.
- `FotoOutputDTO`: `id`, `url`.
- `ProblemaOutputDTO`: `id`, `titulo`, `descricaoProblema`, `categoriaEquipamento`, `localUnidade`, `descricaoLocal`, `status`, `usuario`, `tipoAcesso`, `dataCriacao`, `fotos`.
- `OrdemServicoCadastrarInputDTO`: `problemaId`, `usuarioId`, `statusOrdemServico`, `categoriaProblema`, `dataPrevista`, `prioridade`.
- `OrdemServicoOutputDTO`: `id`, `titulo`, `descricao`, `categoriaProblema`, `categoriaEquipamento`, `prioridade`, `dataPrevista`, `status`, `nomeUsuario`, `tipoAcesso`, `dataCriacao`.
- `OcorrenciaCadastrarInputDTO`: `localUnidadeId`, `categoriaEquipamentoId`, `categoriaProblemaId`, `titulo`, `descricaoOcorrencia`, `descricaoLocal`, `prioridade`, `urlsFoto`.
- `OcorrenciaOutputDTO`: `id`, `titulo`, `descricaoOcorrencia`, `categoriaProblema`, `prioridade`, `localUnidade`, `descricaoLocal`, `dataCriacao`, `categoriaEquipamento`, `nomeUsuario`, `tipoAcesso`, `fotos`.
- `ObservacaoConclusaoCriarInputDTO`: `ordemServicoId`, `dificuldade`, `observacao`, `fotos`.
- `ObservacaoConclusaoOutputDTO`: `id`, `titulo`, `descricaoProblema`, `categoriaProblema`, `categoriaEquipamento`, `localUnidade`, `descricaoLocal`, `statusProblema`, `prioridade`, `statusOrdemServico`, `nomeResponsavel`, `dificuldade`, `observacao`, `dataCriacao`, `fotos`.
- `EventoCadastrarInputDTO`: `usuarioId`, `localUnidadeId`, `titulo`, `descricao`, `descricaoLocal`, `observacao`, `dataHoraInicio`, `dataHoraFim`.
- `EventoOutputDTO`: `id`, `titulo`, `descricao`, `localUnidade`, `descricaoLocal`, `dataHoraInicio`, `dataHoraFim`, `observacao`, `usuario`, `dataCriacao`.
- `EquipamentoCadastrarInputDTO`: `usuarioId`, `modeloEquipamentoId`, `localUnidadeId`, `codigo`.
- `EquipamentoOutputDTO`: `id`, `codigo`, `modeloEquipamento`, `localUnidade`, `usuario`, `dataCriacao`, `estaAtivo`.
- `ModeloEquipamentoCadastrarInputDTO`: `id`, `marcaEquipamentoId`, `categoriaEquipamentoId`, `nome`, `descricao`.
- `ModeloEquipamentoOutputDTO`: `id`, `nome`, `descricao`, `marca`, `categoria`, `dataCriacao`, `estaAtivo`.
- `MarcaEquipamentoCadastrarInputDTO`: `nome`, `descricao`.
- `MarcaEquipamentoOutputDTO`: `id`, `nome`, `descricao`, `dataCriacao`, `estaAtivo`.
- `CategoriaEquipamentoCadastrarInputDTO`: `nome`, `descricao`.
- `CategoriaEquipamentoOutputDTO`: `id`, `nome`, `descricao`, `nomeUsuario`, `dataCriacao`, `estaAtivo`.
- `ValidarCodigoRequestDTO`: `email`, `codigo`.
- `RedefinirSenhaRequestDTO`: `email`, `codigo`, `novaSenha`.
- `LoginRequestDTO`: `email`, `senha`.
- `LoginResponseDTO`: `email`, `token`.
- `GoogleLoginRequestDTO`: `idToken`.
- `GoogleLoginResponseDTO`: `status`, `email`, `nome`, `token`.
- `RedefinirSenhaOutputDTO`: `nome`, `email`, `mensagem`.
- `CadastroUsuarioRequestDTO`: `nomeCompleto`, `email`, `senha`, `unidadeId`, `cargo`, `dataNascimento`.
- `AptidaoAtualizarInputDTO`: `id`, `nota`, `estaAtivo`.
- `AptidaoOutputDTO`: `id`, `categoriaProblema`, `nota`, `dataCriacao`, `estaAtivo`.
- `TarefaAtualizarInputDTO`: `id`, `titulo`, `descricao`, `statusOrdemServico`.
- `ProblemaAtualizarInputDTO`: `problemaId`, `titulo`, `descricaoProblema`, `localUnidadeId`, `descricaoLocal`, `categoriaEquipamentoId`, `fotosAdicionar`, `fotosExcluir`.
- `ProblemaAtualizarStatusDTO`: `problemaId`, `statusProblema`, `motivoRecusa`.
- `UsuarioAtualizarInputDTO`: `nomeCompleto`, `cargo`, `urlFotoPerfil`.
- `TurnoOutputDTO`: `id`, `nome`, `horaInicio`, `horaFim`, `atravessaMeiaNoite`, `dataCriacao`, `estaAtivo`.
- `UsuarioOutputDTO`: `id`, `nomeCompleto`, `email`, `cargo`, `tipoAcesso`, `dataNascimento`, `cnpjUnidade`, `dataCriacao`, `estaAtivo`, `turnos`, `urlFotoPerfil`.
- `OrdemServicoAtualizarInputDTO`: `id`, `usuarioId`, `statusOrdemServico`, `categoriaProblema`, `dataPrevista`, `prioridade`.
- `OcorrenciaAtualizarInputDTO`: `id`, `localUnidadeId`, `categoriaEquipamentoId`, `categoriaProblemaId`, `titulo`, `descricaoOcorrencia`, `descricaoLocal`, `prioridade`, `urlsFoto`.
- `ObservacaoConclusaoAtualizarInputDTO`: `id`, `dificuldade`, `observacao`, `fotos`.
- `EventoAtualizarInputDTO`: `id`, `localUnidadeId`, `titulo`, `descricao`, `descricaoLocal`, `observacao`, `dataHoraInicio`, `dataHoraFim`.
- `EquipamentoAtualizarInputDTO`: `id`, `modeloEquipamentoId`, `localUnidadeId`, `codigo`.
- `ModeloEquipamentoAtualizarInputDTO`: `id`, `marcaEquipamentoId`, `categoriaEquipamentoId`, `nome`, `descricao`, `estaAtivo`.
- `MarcaEquipamentoAtualizarInputDTO`: `id`, `nome`, `descricao`, `estaAtivo`.
- `CategoriaEquipamentoAtualizarInputDTO`: `id`, `nome`, `descricao`, `estaAtivo`.
- `FiltrosUsuarioQueryParam`: `nomeCompleto`, `email`, `cargo`, `tipoAcesso`, `cnpjUnidade`, `dataNascimento`, `estaAtivo`, `limite`, `campoOrdenacao`, `direcaoOrdenacao`.
- `FiltrosTarefaQueryParam`: `titulo`, `descricao`, `status`, `usuarioResponsavel`, `limite`, `campoOrdenacao`, `direcaoOrdenacao`.
- `FiltrosProblemaQueryParam`: `titulo`, `descricaoProblema`, `categoriaEquipamento`, `localUnidade`, `descricaoLocal`, `equipamentoCodigo`, `nomeUsuario`, `tipoAcesso`, `dataCriacaoMin`, `dataCriacaoMax`, `limite`, `campoOrdenacao`, `direcaoOrdenacao`.
- `FiltrosOrdemServicoQueryParam`: `titulo`, `descricao`, `categoriaProblema`, `categoriaEquipamento`, `prioridade`, `dataPrevistaMin`, `dataPrevistaMax`, `statusOrdemServico`, `nomeUsuario`, `tipoAcesso`, `limite`, `campoOrdenacao`, `direcaoOrdenacao`.
- `FiltrosOcorrenciaQueryParam`: `titulo`, `descricaoOcorrencia`, `categoriaProblema`, `prioridade`, `localUnidade`, `descricaoLocal`, `categoriaEquipamento`, `nomeUsuario`, `tipoAcesso`, `dataCriacaoMin`, `dataCriacaoMax`, `limite`, `campoOrdenacao`, `direcaoOrdenacao`.
- `FiltrosObservacaoConclusaoQueryParam`: `id`, `titulo`, `descricaoProblema`, `categoriaProblema`, `categoriaEquipamento`, `localUnidade`, `descricaoLocal`, `statusProblema`, `prioridade`, `nomeResponsavel`, `dificuldade`, `observacao`, `dataCriacao`.
- `LocalUnidadeOutputDTO`: `id`, `nome`.
- `FiltrosEventosQueryParam`: `titulo`, `descricao`, `localUnidade`, `descricaoLocal`, `dataHoraInicio`, `dataHoraFim`, `observacao`, `usuario`, `limite`, `campoOrdenacao`, `direcaoOrdenacao`.
- `FiltrosModeloEquipamentoQueryParam`: `nome`, `descricao`, `marca`, `categoria`, `limite`, `campoOrdenacao`, `direcaoOrdenacao`.
- `FiltrosEquipamentoQueryParam`: `codigo`, `localUnidade`, `usuario`, `limite`, `campoOrdenacao`, `direcaoOrdenacao`.
- `FiltrosMarcaEquipamentoQueryParam`: `nome`, `descricao`, `estaAtivo`, `limite`, `campoOrdenacao`, `direcaoOrdenacao`.
- `FiltrosCategoriaEquipamentoQueryParam`: `nome`, `descricao`, `nomeUsuario`, `limite`, `campoOrdenacao`, `direcaoOrdenacao`.
- `CadastroNomeOutputDTO`: `id`, `nome`.
