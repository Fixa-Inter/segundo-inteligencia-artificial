-- ===============================================
-- DROPS
-- ===============================================

DROP TABLE IF EXISTS turno_usuario CASCADE;
DROP TABLE IF EXISTS turno CASCADE;
DROP TABLE IF EXISTS foto CASCADE;
DROP TABLE IF EXISTS observacao_conclusao CASCADE;
DROP TABLE IF EXISTS tarefa CASCADE;
DROP TABLE IF EXISTS ordem_servico_status_auditoria CASCADE;
DROP TABLE IF EXISTS ordem_servico_tecnico_auditoria CASCADE;
DROP TABLE IF EXISTS ordem_servico CASCADE;
DROP TABLE IF EXISTS ocorrencia CASCADE;
DROP TABLE IF EXISTS problema CASCADE;
DROP TABLE IF EXISTS equipamento CASCADE;
DROP TABLE IF EXISTS modelo_equipamento CASCADE;
DROP TABLE IF EXISTS marca_equipamento CASCADE;
DROP TABLE IF EXISTS categoria_equipamento CASCADE;
DROP TABLE IF EXISTS evento CASCADE;
DROP TABLE IF EXISTS local_unidade CASCADE;
DROP TABLE IF EXISTS feedback CASCADE;
DROP TABLE IF EXISTS aptidao CASCADE;
DROP TABLE IF EXISTS usuario CASCADE;
DROP TABLE IF EXISTS pagamento CASCADE;
DROP TABLE IF EXISTS contrato CASCADE;
DROP TABLE IF EXISTS plano CASCADE;
DROP TABLE IF EXISTS unidade CASCADE;
DROP TABLE IF EXISTS instituicao CASCADE;
DROP TABLE IF EXISTS super_admin CASCADE;


-- ===============================================
-- TABELAS
-- ===============================================

-- TABELA: super_admin
-- Descrição: Armazena os administradores globais da plataforma.
-- Dependências: -

CREATE TABLE super_admin (
    id          BIGSERIAL PRIMARY KEY,
    nome        VARCHAR(100) NOT NULL,
    email       VARCHAR(100) NOT NULL UNIQUE,
    senha_hash  VARCHAR(255) NOT NULL,
    esta_ativo  BOOLEAN NOT NULL DEFAULT TRUE
);

-- TABELA: instituicao
-- Descrição: Armazena as instituições cadastradas na plataforma.
-- Dependências: -

CREATE TABLE instituicao (
    id                 BIGSERIAL PRIMARY KEY,
    nome               VARCHAR(100) NOT NULL,
    tipo_instituicao   INTEGER NOT NULL,
    email_corporativo  VARCHAR(100) UNIQUE,
    dominio_email      VARCHAR(100) NOT NULL UNIQUE,
    data_criacao       TIMESTAMP NOT NULL DEFAULT NOW(),
    esta_ativo         BOOLEAN NOT NULL DEFAULT TRUE,
    CONSTRAINT ck_tipo_instituicao_1_a_4 CHECK (tipo_instituicao BETWEEN 1 AND 4)
);

/**
 * Tabela: unidade
 *
 * Descrição:
 * Armazena as unidades e seus endereços físicos das instituições.
 *
 * Dependências:
 * - instituicao
 */

CREATE TABLE unidade (
    id              BIGSERIAL PRIMARY KEY,
    instituicao_id  BIGINT NOT NULL REFERENCES instituicao(id),
    nome            VARCHAR(100) NOT NULL,
    cnpj            CHAR(14) NOT NULL UNIQUE,
    logradouro      VARCHAR(100) NOT NULL,
    numero          VARCHAR(10) NOT NULL,
    complemento     VARCHAR(100),
    bairro          VARCHAR(100) NOT NULL,
    cidade          VARCHAR(100) NOT NULL,
    estado          CHAR(2) NOT NULL,
    cep             CHAR(8) NOT NULL,
    data_criacao    TIMESTAMP NOT NULL DEFAULT NOW(),
    esta_ativo      BOOLEAN NOT NULL DEFAULT TRUE
);

-- TABELA: plano
-- Descrição: Define os planos disponíveis para contratação.
-- Dependências: -

CREATE TABLE plano (
    id             BIGSERIAL PRIMARY KEY,
    nome           VARCHAR(100) NOT NULL,
    valor          DECIMAL(10, 2) NOT NULL,
    descricao      VARCHAR(255),
    duracao_meses  INTEGER NOT NULL,
    data_criacao   TIMESTAMP NOT NULL DEFAULT NOW(),
    esta_ativo     BOOLEAN NOT NULL DEFAULT TRUE,
    CONSTRAINT ck_duracao_meses_positiva CHECK (duracao_meses > 0)
);

/**
 * Tabela: contrato
 *
 * Descrição:
 * Registra os contratos vinculados às unidades das instituições.
 *
 * Dependências:
 * - plano
 * - unidade
 */

CREATE TABLE contrato (
    id            BIGSERIAL PRIMARY KEY,
    plano_id      BIGINT NOT NULL REFERENCES plano(id),
    unidade_id   BIGINT NOT NULL REFERENCES unidade(id),
    data_inicio   DATE NOT NULL DEFAULT CURRENT_DATE,
    data_fim      DATE NOT NULL,
    status        INTEGER NOT NULL DEFAULT 1,
    data_criacao  TIMESTAMP NOT NULL DEFAULT NOW(),
    CONSTRAINT ck_status_contrato_1_a_3 CHECK (status BETWEEN 1 AND 3),
    CONSTRAINT ck_data_fim_maior_data_inicio CHECK (data_fim > data_inicio)
);

-- TABELA: pagamento
-- Descrição: Registra os pagamentos relacionados aos contratos.
-- Dependências: contrato

CREATE TABLE pagamento (
    id                BIGSERIAL PRIMARY KEY,
    contrato_id       BIGINT NOT NULL REFERENCES contrato(id),
    data_pagamento    TIMESTAMP NOT NULL,
    valor_pago        DECIMAL(10, 2) NOT NULL,
    status            INTEGER DEFAULT 1,
    metodo_pagamento  INTEGER NOT NULL,
    data_criacao      TIMESTAMP NOT NULL DEFAULT NOW(),
    CONSTRAINT ck_status_pagamento_1_a_3 CHECK (status BETWEEN 1 AND 3),
    CONSTRAINT ck_metodo_pagamento_1_a_3 CHECK (metodo_pagamento BETWEEN 1 AND 3)
);

/**
 * Tabela: usuario
 *
 * Descrição:
 * Armazena os usuários e suas informações de acesso.
 *
 * Dependências:
 * - unidade
 */

CREATE TABLE usuario (
    id               BIGSERIAL PRIMARY KEY,
    unidade_id      BIGINT NOT NULL REFERENCES unidade(id),
    nome_completo    VARCHAR(100) NOT NULL,
    email            VARCHAR(100) NOT NULL UNIQUE,
    tipo_acesso      INTEGER NOT NULL,
    senha_hash       VARCHAR(255) NOT NULL,
    cargo            VARCHAR(100) NOT NULL,
    data_nascimento  DATE NOT NULL,
    data_criacao     TIMESTAMP NOT NULL DEFAULT NOW(),
    data_atualizacao TIMESTAMP DEFAULT NOW(),
    esta_ativo       BOOLEAN NOT NULL DEFAULT FALSE,
    primeiro_acesso  BOOLEAN NOT NULL DEFAULT TRUE,
    CONSTRAINT uk_usuario_id_unidade UNIQUE (id, unidade_id),
    CONSTRAINT ck_tipo_acesso_usuario_1_a_4 CHECK (tipo_acesso BETWEEN 1 AND 4)
);

-- TABELA: aptidao
-- Descrição: Registra a aptidão dos técnicos para categorias de problemas.
-- Dependências: usuario

CREATE TABLE aptidao (
    id                  BIGSERIAL PRIMARY KEY,
    usuario_id          BIGINT NOT NULL REFERENCES usuario(id),
    categoria_problema  INTEGER NOT NULL,
    nota                DECIMAL(4, 2) NOT NULL,
    data_criacao        TIMESTAMP NOT NULL DEFAULT NOW(),
    esta_ativo          BOOLEAN NOT NULL DEFAULT TRUE,
    CONSTRAINT uk_usuario_categoria_aptidao UNIQUE (usuario_id, categoria_problema),
    CONSTRAINT ck_categoria_problema_aptidao_1_a_10 CHECK (categoria_problema BETWEEN 1 AND 10)
);

-- TABELA: feedback
-- Descrição: Registra o feedback do usuário em relação ao aplicativo.
-- Dependências: usuario

CREATE TABLE feedback (
    id             BIGSERIAL PRIMARY KEY,
    usuario_id     BIGINT NOT NULL REFERENCES usuario(id),
    comentario     VARCHAR(255),
    ideia_central  VARCHAR(255),
    data_criacao   TIMESTAMP NOT NULL DEFAULT NOW()
);

/**
 * Tabela: local_unidade
 *
 * Descrição:
 * Representa locais específicos dentro das unidades.
 *
 * Dependências:
 * - unidade
 */

CREATE TABLE local_unidade (
    id                   BIGSERIAL PRIMARY KEY,
    unidade_id          BIGINT NOT NULL REFERENCES unidade(id),
    nome                 VARCHAR(100) NOT NULL,
    tipo_local_unidade  INTEGER NOT NULL,
    descricao            VARCHAR(255) NOT NULL,
    data_criacao         TIMESTAMP NOT NULL DEFAULT NOW(),
    data_atualizacao     TIMESTAMP DEFAULT NOW(),
    esta_ativo           BOOLEAN NOT NULL DEFAULT TRUE,
    CONSTRAINT ck_tipo_local_unidade_1_a_6 CHECK (tipo_local_unidade BETWEEN 1 AND 6)
);

-- TABELA: evento
-- Descrição: Armazena eventos agendados em um endereço.
-- Dependências: usuario, local_unidade

CREATE TABLE evento (
    id                 BIGSERIAL PRIMARY KEY,
    usuario_id         BIGINT NOT NULL REFERENCES usuario(id),
    local_unidade_id  BIGINT NOT NULL REFERENCES local_unidade(id),
    titulo             VARCHAR(100) NOT NULL,
    descricao          VARCHAR(255) NOT NULL,
    descricao_local    VARCHAR(255) NOT NULL,
    observacao         VARCHAR(255),
    data_hora_inicio   TIMESTAMP NOT NULL,
    data_hora_fim      TIMESTAMP NOT NULL,
    data_criacao       TIMESTAMP NOT NULL DEFAULT NOW(),
    data_atualizacao   TIMESTAMP DEFAULT NOW(),
    esta_ativo         BOOLEAN NOT NULL DEFAULT TRUE
);

-- TABELA: categoria_equipamento
-- Descrição: Armazena as categorias utilizadas para classificar equipamentos.
-- Dependências: usuario

CREATE TABLE categoria_equipamento (
    id            BIGSERIAL PRIMARY KEY,
    usuario_id    BIGINT NOT NULL REFERENCES usuario(id),
    nome          VARCHAR(100) NOT NULL,
    descricao     VARCHAR(255) NOT NULL,
    data_criacao  TIMESTAMP NOT NULL DEFAULT NOW(),
    data_atualizacao TIMESTAMP DEFAULT NOW(),
    esta_ativo    BOOLEAN NOT NULL DEFAULT TRUE
);

-- TABELA: marca_equipamento
-- Descrição: Armazena as marcas dos equipamentos.
-- Dependências: -

CREATE TABLE marca_equipamento (
    id            BIGSERIAL PRIMARY KEY,
    nome          VARCHAR(100) NOT NULL,
    descricao     VARCHAR(255) NOT NULL,
    data_criacao  TIMESTAMP NOT NULL DEFAULT NOW(),
    data_atualizacao TIMESTAMP DEFAULT NOW(),
    esta_ativo    BOOLEAN NOT NULL DEFAULT TRUE
);

-- TABELA: modelo_equipamento
-- Descrição: Armazena os modelos de equipamentos, relacionando cada modelo à sua marca e categoria.
-- Dependências: marca_equipamento, categoria_equipamento

CREATE TABLE modelo_equipamento (
    id                       BIGSERIAL PRIMARY KEY,
    marca_equipamento_id     BIGINT NOT NULL REFERENCES marca_equipamento(id),
    categoria_equipamento_id BIGINT NOT NULL REFERENCES categoria_equipamento(id),
    nome                     VARCHAR(100) NOT NULL,
    descricao                VARCHAR(255) NOT NULL,
    data_criacao             TIMESTAMP NOT NULL DEFAULT NOW(),
    data_atualizacao         TIMESTAMP DEFAULT NOW(),
    esta_ativo               BOOLEAN NOT NULL DEFAULT TRUE
);

-- TABELA: equipamento
-- Descrição: Armazena os equipamentos e suas localizações.
-- Dependências: usuario, modelo_equipamento, local_unidade

CREATE TABLE equipamento (
    id                    BIGSERIAL PRIMARY KEY,
    usuario_id            BIGINT NOT NULL REFERENCES usuario(id),
    modelo_equipamento_id BIGINT NOT NULL REFERENCES modelo_equipamento(id),
    local_unidade_id     BIGINT NOT NULL REFERENCES local_unidade(id),
    codigo                VARCHAR(100) NOT NULL,
    data_criacao          TIMESTAMP NOT NULL DEFAULT NOW(),
    data_atualizacao      TIMESTAMP DEFAULT NOW(),
    esta_ativo            BOOLEAN NOT NULL DEFAULT TRUE
);

-- TABELA: problema
-- Descrição: Registra problemas identificados nas instituições.
-- Dependências: usuario, categoria_equipamento, local_unidade

CREATE TABLE problema (
    id                       BIGSERIAL PRIMARY KEY,
    usuario_id               BIGINT NOT NULL REFERENCES usuario(id),
    categoria_equipamento_id BIGINT NOT NULL REFERENCES categoria_equipamento(id),
    local_unidade_id        BIGINT NOT NULL REFERENCES local_unidade(id),
    titulo                   VARCHAR(100) NOT NULL,
    descricao_problema       VARCHAR(255) NOT NULL,
    descricao_local          VARCHAR(255) NOT NULL,
    motivo_recusa            VARCHAR(255) DEFAULT NULL,
    data_criacao             TIMESTAMP NOT NULL DEFAULT NOW(),
    data_atualizacao         TIMESTAMP DEFAULT NOW(),
    esta_ativo               BOOLEAN NOT NULL DEFAULT TRUE,
    status                   INTEGER NOT NULL DEFAULT 0,
    CONSTRAINT ck_status_problema_0_a_3 CHECK (status BETWEEN 0 AND 3),
    CONSTRAINT ck_motivo_recusa_status_recusado CHECK (
        (status = 1 AND motivo_recusa IS NOT NULL)
        OR
        (status <> 1 AND motivo_recusa IS NULL)
    )
);

-- TABELA: ocorrencia
-- Descrição: Registra problemas não registrados previamente, mas que já foram resolvidos por um técnico.
-- Dependências: usuario, local_unidade, categoria_equipamento

CREATE TABLE ocorrencia (
    id                       BIGSERIAL PRIMARY KEY,
    usuario_id               BIGINT NOT NULL REFERENCES usuario(id),
    local_unidade_id        BIGINT NOT NULL REFERENCES local_unidade(id),
    categoria_equipamento_id BIGINT NOT NULL REFERENCES categoria_equipamento(id),
    categoria_problema       INTEGER NOT NULL,
    titulo                   VARCHAR(100) NOT NULL,
    descricao_ocorrencia     VARCHAR(255) NOT NULL,
    descricao_local          VARCHAR(255) NOT NULL,
    prioridade               INTEGER NOT NULL,
    data_criacao             TIMESTAMP NOT NULL DEFAULT NOW(),
    data_atualizacao         TIMESTAMP DEFAULT NOW(),
    esta_ativo               BOOLEAN NOT NULL DEFAULT TRUE,
    CONSTRAINT ck_categoria_problema_ocorrencia_1_a_10 CHECK (categoria_problema BETWEEN 1 AND 10),
    CONSTRAINT ck_prioridade_ocorrencia_0_a_2 CHECK (prioridade BETWEEN 0 AND 2)
);

/**
 * Tabela: ordem_servico
 *
 * Descrição:
 * Registra as ordens de serviço e seu acompanhamento.
 *
 * Dependências:
 * - problema
 * - usuario
 */

CREATE TABLE ordem_servico (
    id                       BIGSERIAL PRIMARY KEY,
    problema_id              BIGINT NOT NULL UNIQUE REFERENCES problema(id),
    usuario_id               BIGINT NOT NULL REFERENCES usuario(id),
    status_ordem_servico     INTEGER NOT NULL DEFAULT 0,
    categoria_problema       INTEGER NOT NULL,
    data_prevista            TIMESTAMP NOT NULL,
    prioridade               INTEGER NOT NULL,
    data_criacao             TIMESTAMP NOT NULL DEFAULT NOW(),
    data_atualizacao         TIMESTAMP DEFAULT NOW(),
    esta_ativo               BOOLEAN NOT NULL DEFAULT TRUE,
    CONSTRAINT ck_status_ordem_servico CHECK (status_ordem_servico BETWEEN 0 AND 4),
    CONSTRAINT ck_categoria_problema_os_1_a_10 CHECK (categoria_problema BETWEEN 1 AND 10),
    CONSTRAINT ck_prioridade_os_0_a_2 CHECK (prioridade BETWEEN 0 AND 2)
);

/**
 * Tabela: ordem_servico_status_auditoria
 *
 * Descrição:
 * Registra as alterações de status das ordens de serviço, armazenando o valor anterior e o novo valor.
 *
 * Dependências:
 * - ordem_servico
 */

CREATE TABLE ordem_servico_status_auditoria (
    id                  BIGSERIAL PRIMARY KEY,
    ordem_servico_id    BIGINT NOT NULL REFERENCES ordem_servico(id),
    status_anterior     INTEGER NOT NULL,
    status_novo         INTEGER NOT NULL,
    data_alteracao      TIMESTAMP NOT NULL DEFAULT NOW(),
    CONSTRAINT ck_status_anterior_ordem_servico CHECK (status_anterior BETWEEN 0 AND 4),
    CONSTRAINT ck_status_novo_ordem_servico CHECK (status_novo BETWEEN 0 AND 4)
);

-- TABELA: ordem_servico_tecnico_auditoria
-- Descrição: Registra as alterações de técnico responsável por uma ordem de serviço.
-- Dependências: ordem_servico, usuario

CREATE TABLE ordem_servico_tecnico_auditoria (
    id                   BIGSERIAL PRIMARY KEY,
    ordem_servico_id     BIGINT NOT NULL REFERENCES ordem_servico(id),
    tecnico_anterior_id  BIGINT NOT NULL REFERENCES usuario(id),
    tecnico_novo_id      BIGINT NOT NULL REFERENCES usuario(id),
    data_alteracao       TIMESTAMP NOT NULL DEFAULT NOW()
);

/**
 * Tabela: tarefa
 *
 * Descrição:
 * Registra as tarefas vinculadas às ordens de serviço, permitindo seu acompanhamento em um kanban próprio.
 *
 * Dependências:
 * - ordem_servico
 */

CREATE TABLE tarefa (
    id                       BIGSERIAL PRIMARY KEY,
    ordem_servico_id         BIGINT NOT NULL REFERENCES ordem_servico(id) ON DELETE CASCADE,
    status_ordem_servico     INTEGER NOT NULL DEFAULT 0,
    titulo                   VARCHAR(100) NOT NULL,
    descricao                VARCHAR(255) NOT NULL,
    data_criacao             TIMESTAMP NOT NULL DEFAULT NOW(),
    data_atualizacao         TIMESTAMP DEFAULT NOW(),
    esta_ativo               BOOLEAN NOT NULL DEFAULT TRUE,
    CONSTRAINT ck_status_tarefa CHECK (status_ordem_servico BETWEEN 0 AND 4)
);

-- TABELA: observacao_conclusao
-- Descrição: Armazena observações relacionadas à conclusão das ordens de serviço.
-- Dependências: ordem_servico

CREATE TABLE observacao_conclusao (
    id                BIGSERIAL PRIMARY KEY,
    ordem_servico_id  BIGINT NOT NULL REFERENCES ordem_servico(id),
    dificuldade       INTEGER NOT NULL,
    observacao        VARCHAR(255) NOT NULL,
    data_criacao      TIMESTAMP NOT NULL DEFAULT NOW(),
    data_atualizacao  TIMESTAMP DEFAULT NOW(),
    esta_ativo        BOOLEAN NOT NULL DEFAULT TRUE,
    CONSTRAINT ck_dificuldade_observacao_1_a_3 CHECK (dificuldade BETWEEN 1 AND 3)
);

-- TABELA: foto
-- Descrição: Armazena fotos associadas às entidades do sistema.
-- Dependências: problema, ocorrencia, ordem_servico, observacao_conclusao, usuario

CREATE TABLE foto (
    id                       BIGSERIAL PRIMARY KEY,
    problema_id              BIGINT REFERENCES problema(id),
    ocorrencia_id            BIGINT REFERENCES ocorrencia(id),
    ordem_servico_id         BIGINT REFERENCES ordem_servico(id),
    observacao_conclusao_id  BIGINT REFERENCES observacao_conclusao(id),
    usuario_id               BIGINT REFERENCES usuario(id),
    url                      VARCHAR(255) NOT NULL,
    esta_ativo               BOOLEAN NOT NULL DEFAULT TRUE,
    data_criacao             TIMESTAMP NOT NULL DEFAULT NOW(),
    CONSTRAINT ck_foto_apenas_uma_fk CHECK (
        (CASE WHEN problema_id IS NOT NULL THEN 1 ELSE 0 END) +
        (CASE WHEN ocorrencia_id IS NOT NULL THEN 1 ELSE 0 END) +
        (CASE WHEN ordem_servico_id IS NOT NULL THEN 1 ELSE 0 END) +
        (CASE WHEN observacao_conclusao_id IS NOT NULL THEN 1 ELSE 0 END) +
        (CASE WHEN usuario_id IS NOT NULL THEN 1 ELSE 0 END) = 1
    )
);

/**
 * Tabela: turno
 *
 * Descrição:
 * Define os turnos de funcionamento das unidades.
 *
 * Dependências:
 * - unidade
 */

CREATE TABLE turno (
    id                    BIGSERIAL PRIMARY KEY,
    unidade_id           BIGINT NOT NULL REFERENCES unidade(id),
    nome                  VARCHAR(100) NOT NULL,
    hora_inicio           INTEGER NOT NULL,
    hora_fim              INTEGER NOT NULL,
    atravessa_meia_noite  BOOLEAN NOT NULL DEFAULT FALSE,
    data_criacao          TIMESTAMP NOT NULL DEFAULT NOW(),
    esta_ativo            BOOLEAN NOT NULL DEFAULT TRUE,
    CONSTRAINT ck_hora_inicio_range CHECK (hora_inicio BETWEEN 0 AND 86400),
    CONSTRAINT ck_hora_fim_range CHECK (hora_fim BETWEEN 0 AND 86400),
    CONSTRAINT ck_horas_consistentes CHECK (
        (atravessa_meia_noite = FALSE AND hora_inicio < hora_fim)
        OR
        (atravessa_meia_noite = TRUE AND hora_inicio > hora_fim)
    )
);

-- TABELA: turno_usuario
-- Descrição: Relaciona usuários aos seus respectivos turnos.
-- Dependências: turno, usuario

CREATE TABLE turno_usuario (
    id            BIGSERIAL PRIMARY KEY,
    turno_id      BIGINT NOT NULL REFERENCES turno(id),
    usuario_id    BIGINT NOT NULL REFERENCES usuario(id),
    data_criacao  TIMESTAMP NOT NULL DEFAULT NOW(),
    esta_ativo    BOOLEAN NOT NULL DEFAULT TRUE,
    CONSTRAINT uk_turno_usuario UNIQUE (turno_id, usuario_id)
);