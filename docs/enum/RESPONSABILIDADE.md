# Responsabilidade: docs/enum

## Objetivo do módulo

Documentar códigos/nomes dos enums FIXA.

## O que deve ser armazenado aqui

Acesso, instituição, local, categorias, prioridade, dificuldade e status.

## Comportamento e limites atuais

statusProblema inclui OS_CRIADA=4; CHECK de problema no DDL cobre 0 a 3. Divergência registrada sem alterar contratos.

Módulo pai: [docs](../RESPONSABILIDADE.md).

## Funcionalidades disponíveis e arquivos

Os arquivos abaixo são referências ou configuração; não expõem métodos Python.

### [categoriaProblema.txt](categoriaProblema.txt)

Referência de nomes, rótulos e códigos de categoriaProblema.

```text
ELETRICA("Elétrica", 1),
HIDRAULICA("Hidráulica", 2),
MECANICA("Mecânica", 3),
INFORMATICA("Informática", 4),
MOBILIARIO("Mobiliário", 5),
CLIMATIZACAO("Climatização", 6),
REDE_CONECTIVIDADE("Rede e Conectividade", 7),
SEGURANCA("Segurança", 8),
ILUMINACAO("Iluminação", 9),
LIMPEZA_CONSERVACAO("Limpeza e Conservação", 10);
```

### [dificuldade.txt](dificuldade.txt)

Referência de nomes, rótulos e códigos de dificuldade.

```text
FACIL("Fácil", 1),
MEDIO("Médio", 2),
DIFICIL("Difícil", 3);
```

### [prioridade.txt](prioridade.txt)

Referência de nomes, rótulos e códigos de prioridade.

```text
ALTA("Alta", 0),
MEDIA("Média", 1),
BAIXA("Baixa", 2);
```

### [statusOrdemServico.txt](statusOrdemServico.txt)

Referência de nomes, rótulos e códigos de statusOrdemServico.

```text
NAO_INICIADA("Não Iniciada", 0),
ATRASADA("Atrasada", 1),
PAUSADA("Pausada", 2),
EM_ANDAMENTO("Em andamento", 3),
CONCLUIDA("Concluída", 4);
```

### [statusProblema.txt](statusProblema.txt)

Referência de nomes, rótulos e códigos de statusProblema.

```text
PENDENTE("Pendente", 0),
REPROVADO("Reprovado", 1),
APROVADO("Aprovado", 2),
CONCLUIDO("Concluído", 3),
OS_CRIADA("OS Criada", 4);
```

### [tipoAcesso.txt](tipoAcesso.txt)

Referência de nomes, rótulos e códigos de tipoAcesso.

```text
ADMINISTRADOR("Administrador", 1),
GESTOR("Gestor", 2),
TECNICO("Técnico", 3),
SOLICITANTE("Solicitante", 4);
```

### [tipoInstituicao.txt](tipoInstituicao.txt)

Referência de nomes, rótulos e códigos de tipoInstituicao.

```text
ESCOLA("Escola", 1),
FACULDADE("Faculdade", 2),
EMPRESA("Empresa", 3),
ORGAO_PUBLICO("Órgão Público", 4);
```

### [tipoLocalEndereco.txt](tipoLocalEndereco.txt)

Referência de nomes, rótulos e códigos de tipoLocalEndereco.

```text
SALA_AULA("Sala de Aula", 1),
LABORATORIO("Laboratório", 2),
DEPTO_ADMINISTRATIVO("Depto. Administrativo", 3),
AUDITORIO("Auditório", 4),
ALMOXAFIRADO("Almoxarifado", 5),
AREA_COMUM("Área Comum", 6);
```
