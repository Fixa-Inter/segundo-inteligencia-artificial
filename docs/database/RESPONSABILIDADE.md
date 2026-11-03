# Responsabilidade: docs/database

## Objetivo do módulo

Documentar estrutura relacional e permissões.

## O que deve ser armazenado aqui

DDL e complemento de GRANT para atualização de ocorrência.

## Comportamento e limites atuais

Scripts não rodam no startup. GRANT complementar não cria roles/RLS; aplicação verifica autoria/unidade/atividade.

Módulo pai: [docs](../RESPONSABILIDADE.md).

## Funcionalidades disponíveis e arquivos

Os arquivos abaixo são referências ou configuração; não expõem métodos Python.

### [permissoes_atualizacao_ocorrencias.sql](permissoes_atualizacao_ocorrencias.sql)

Complemento de permissões de ocorrência/foto para manu_tecnico e manu_gestor.

### [script_completo.sql](script_completo.sql)

DDL de tabelas, chaves, restrições e relacionamentos do PostgreSQL FIXA.

Tabelas declaradas: `super_admin`, `instituicao`, `unidade`, `plano`, `contrato`, `pagamento`, `usuario`, `aptidao`, `feedback`, `local_unidade`, `evento`, `categoria_equipamento`, `marca_equipamento`, `modelo_equipamento`, `equipamento`, `problema`, `ocorrencia`, `ordem_servico`, `ordem_servico_status_auditoria`, `ordem_servico_tecnico_auditoria`, `tarefa`, `observacao_conclusao`, `foto`, `turno`, `turno_usuario`.
