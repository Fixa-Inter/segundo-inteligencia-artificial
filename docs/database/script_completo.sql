-- ===================================================
-- SCRIPT FÍSICO - FIXA
-- ===================================================


-- ===================================================
-- DROPS
-- ===================================================

DROP TABLE IF EXISTS turno_usuario CASCADE;
DROP TABLE IF EXISTS turno CASCADE;
DROP TABLE IF EXISTS foto CASCADE;
DROP TABLE IF EXISTS tarefa_status_historico CASCADE;
DROP TABLE IF EXISTS tarefa CASCADE;
DROP TABLE IF EXISTS ordem_servico_status_historico CASCADE;
DROP TABLE IF EXISTS ordem_servico CASCADE;
DROP TABLE IF EXISTS status_ordem_servico CASCADE;
DROP TABLE IF EXISTS ocorrencia CASCADE;
DROP TABLE IF EXISTS problema CASCADE;
DROP TABLE IF EXISTS equipamento CASCADE;
DROP TABLE IF EXISTS modelo_equipamento CASCADE;
DROP TABLE IF EXISTS marca_equipamento CASCADE;
DROP TABLE IF EXISTS categoria_equipamento CASCADE;
DROP TABLE IF EXISTS evento CASCADE;
DROP TABLE IF EXISTS local_endereco CASCADE;
DROP TABLE IF EXISTS aptidao CASCADE;
DROP TABLE IF EXISTS usuario CASCADE;
DROP TABLE IF EXISTS pagamento CASCADE;
DROP TABLE IF EXISTS contrato CASCADE;
DROP TABLE IF EXISTS plano CASCADE;
DROP TABLE IF EXISTS endereco CASCADE;
DROP TABLE IF EXISTS instituicao CASCADE;
DROP TABLE IF EXISTS super_admin CASCADE;
DROP TABLE IF EXISTS observacao_conclusao CASCADE;


-- ===================================================
-- TABELAS BASE (ADMIN / INSTITUIÇÃO)
-- ===================================================

-- TABELA: super_admin
-- Descrição: Armazena os administradores globais da plataforma.
-- Dependências: -

CREATE TABLE super_admin(
    id         SERIAL PRIMARY KEY,
    nome       VARCHAR(100) NOT NULL,
    email      VARCHAR(100) NOT NULL UNIQUE,
    senha_hash VARCHAR(255) NOT NULL,
    esta_ativo BOOLEAN NOT NULL DEFAULT TRUE
);


-- TABELA: instituicao
-- Descrição: Armazena as instituições cadastradas na plataforma.
-- Dependências: -

CREATE TABLE instituicao(
    id                SERIAL PRIMARY KEY,
    nome              VARCHAR(100) NOT NULL,
    tipo_instituicao  INTEGER NOT NULL,
    email_corporativo VARCHAR(100) UNIQUE,
    dominio_email     VARCHAR(100) NOT NULL UNIQUE,
    data_criacao      TIMESTAMP NOT NULL DEFAULT NOW(),
    esta_ativo        BOOLEAN NOT NULL DEFAULT TRUE
);


-- TABELA: endereco
-- Descrição: Armazena os endereços/franquias das instituições.
-- Dependências: instituicao

CREATE TABLE endereco(
    id             SERIAL PRIMARY KEY,
    instituicao_id INTEGER NOT NULL REFERENCES instituicao(id),
    cnpj           CHAR(14) NOT NULL UNIQUE,
    logradouro     VARCHAR(100) NOT NULL,
    numero         VARCHAR(10) NOT NULL,
    complemento    VARCHAR(100),
    bairro         VARCHAR(100) NOT NULL,
    cidade         VARCHAR(100) NOT NULL,
    estado         CHAR(2) NOT NULL,
    cep            CHAR(8) NOT NULL,
    data_criacao   TIMESTAMP NOT NULL DEFAULT NOW(),
    esta_ativo     BOOLEAN NOT NULL DEFAULT TRUE
);


-- ===================================================
-- FLUXO PLANO / PAGAMENTO
-- ===================================================

-- TABELA: plano
-- Descrição: Define os planos disponíveis para contratação.
-- Dependências: -

CREATE TABLE plano(
    id            SERIAL PRIMARY KEY,
    nome          VARCHAR(100) NOT NULL,
    valor         DECIMAL(10,2) NOT NULL,
    descricao     VARCHAR(255),
    duracao_meses INTEGER NOT NULL,
    data_criacao  TIMESTAMP NOT NULL DEFAULT NOW(),
    esta_ativo    BOOLEAN NOT NULL DEFAULT TRUE,

    CONSTRAINT ck_duracao_meses_positiva
        CHECK (duracao_meses > 0)
);


-- TABELA: contrato
-- Descrição: Registra os contratos vinculados às instituições.
-- Dependências: plano, endereco

CREATE TABLE contrato(
    id           SERIAL PRIMARY KEY,
    plano_id     INTEGER NOT NULL REFERENCES plano(id),
    endereco_id  INTEGER NOT NULL REFERENCES endereco(id),
    data_inicio  DATE NOT NULL DEFAULT CURRENT_DATE,
    data_fim     DATE NOT NULL,
    status       INTEGER NOT NULL DEFAULT 1, --   1 = Ativo, 2 = Inativo, 3 = Cancelado
    data_criacao TIMESTAMP NOT NULL DEFAULT NOW(),

    CONSTRAINT ck_data_fim_maior_ou_igual_data_inicio
        CHECK (data_fim > data_inicio)
);


-- TABELA: pagamento
-- Descrição: Registra os pagamentos relacionados aos contratos.
-- Dependências: contrato

CREATE TABLE pagamento(
    id               SERIAL PRIMARY KEY,
    contrato_id      INTEGER NOT NULL REFERENCES contrato(id),
    data_pagamento   TIMESTAMP NOT NULL,
    valor_pago       DECIMAL(10,2) NOT NULL,
    status           INTEGER DEFAULT 1, -- 1 = Pendente, 2 = Aprovado, 3 = Rejeitado
    metodo_pagamento INTEGER NOT NULL,
    data_criacao     TIMESTAMP NOT NULL DEFAULT NOW()
);


-- ===================================================
-- USUÁRIOS / APTIDÃO / FEEDBACK
-- ===================================================

-- TABELA: usuario
-- Descrição: Armazena os usuários e suas informações de acesso.
-- Dependências: usuario (auto-relacionamento)

CREATE TABLE usuario (
    id                 SERIAL PRIMARY KEY,
    endereco_id        INTEGER NOT NULL REFERENCES endereco(id),
    nome_completo      VARCHAR(100) NOT NULL,
    email              VARCHAR(100) NOT NULL UNIQUE,
    tipo_acesso        INTEGER NOT NULL,
    senha_hash         VARCHAR(255) NOT NULL,
    cargo              VARCHAR(100) NOT NULL,
    data_nascimento    DATE NOT NULL,
    data_criacao       TIMESTAMP NOT NULL DEFAULT NOW(),
    esta_ativo         BOOLEAN NOT NULL DEFAULT FALSE,
    primeiro_acesso    BOOLEAN NOT NULL DEFAULT TRUE,

    CONSTRAINT uk_usuario_id_endereco
        UNIQUE (id, endereco_id)
);


-- TABELA: aptidao
-- Descrição: Registra a aptidão dos técnicos para categorias de problemas.
-- Dependências: usuario

CREATE TABLE aptidao(
    id                 SERIAL PRIMARY KEY,
    usuario_id         INTEGER NOT NULL REFERENCES usuario(id),
    categoria_problema INTEGER NOT NULL,
    nota               DECIMAL(4,2) NOT NULL, -- As notas vão de 0.00 a 10.00
    data_criacao       TIMESTAMP NOT NULL DEFAULT NOW(),
    esta_ativo         BOOLEAN NOT NULL DEFAULT TRUE,

    CONSTRAINT uk_usuario_categoria_aptidao
        UNIQUE (usuario_id, categoria_problema)
);


-- TABELA: feedback
-- Descrição: Registra o feedback do usuário em relação ao aplicativo. 
CREATE TABLE feedback(
    id                 SERIAL PRIMARY KEY,
    usuario_id         INTEGER NOT NULL REFERENCES usuario(id),
    comentario         VARCHAR(255),
    ideia_central      VARCHAR(255),
    data_criacao       TIMESTAMP NOT NULL DEFAULT NOW(),
);


-- ===================================================
-- LOCAIS / EVENTOS
-- ===================================================

-- TABELA: local_endereco
-- Descrição: Representa locais específicos dentro dos endereços.
-- Dependências: endereco

CREATE TABLE local_endereco(
    id                  SERIAL PRIMARY KEY,
    endereco_id         INTEGER NOT NULL REFERENCES endereco(id),
    nome                VARCHAR(100) NOT NULL,
    tipo_local_endereco INTEGER NOT NULL,
    descricao           VARCHAR(255) NOT NULL,
    data_criacao        TIMESTAMP NOT NULL DEFAULT NOW(),
    esta_ativo          BOOLEAN NOT NULL DEFAULT TRUE
);


-- TABELA: evento
-- Descrição: Armazena eventos agendados em um endereço.
-- Dependências: usuario, local_endereco

CREATE TABLE evento(
    id                SERIAL PRIMARY KEY,
    usuario_id        INTEGER NOT NULL REFERENCES usuario(id),
    local_endereco_id INTEGER NOT NULL REFERENCES local_endereco(id),
    titulo            VARCHAR(100) NOT NULL,
    descricao         VARCHAR(255) NOT NULL,
    descricao_local   VARCHAR(255) NOT NULL,
    observacao        VARCHAR(255),
    data_hora_inicio  TIMESTAMP NOT NULL,
    data_hora_fim     TIMESTAMP NOT NULL,
    data_criacao      TIMESTAMP NOT NULL DEFAULT NOW()
);


-- ===================================================
-- EQUIPAMENTOS / PROBLEMAS / OCORRÊNCIAS
-- ===================================================

-- TABELA: categoria_equipamento
-- Descrição: Armazena as categorias utilizadas para classificar equipamentos.
-- Dependências: usuario

CREATE TABLE categoria_equipamento(
    id           SERIAL PRIMARY KEY,
    usuario_id   INTEGER NOT NULL REFERENCES usuario(id),
    nome         VARCHAR(100) NOT NULL,
    descricao    VARCHAR(255) NOT NULL,
    data_criacao TIMESTAMP NOT NULL DEFAULT NOW(),
    esta_ativo   BOOLEAN NOT NULL DEFAULT TRUE
);


-- TABELA: marca_equipamento
-- Descrição: Armazena as marcas dos equipamentos.
-- Dependências: -

CREATE TABLE marca_equipamento(
    id           SERIAL PRIMARY KEY,
    nome         VARCHAR(100) NOT NULL,
    descricao    VARCHAR(255) NOT NULL,
    data_criacao TIMESTAMP NOT NULL DEFAULT NOW(),
    esta_ativo   BOOLEAN NOT NULL DEFAULT TRUE
);


-- TABELA: modelo_equipamento
-- Descrição: Armazena os modelos vinculados às suas marcas e categorias.
-- Dependências: marca_equipamento, categoria_equipamento

CREATE TABLE modelo_equipamento(
    id                       SERIAL PRIMARY KEY,
    marca_equipamento_id     INTEGER NOT NULL REFERENCES marca_equipamento(id),
    categoria_equipamento_id INTEGER NOT NULL REFERENCES categoria_equipamento(id),
    nome                     VARCHAR(100) NOT NULL,
    descricao                VARCHAR(255) NOT NULL,
    data_criacao             TIMESTAMP NOT NULL DEFAULT NOW(),
    esta_ativo               BOOLEAN NOT NULL DEFAULT TRUE
);


-- TABELA: equipamento
-- Descrição: Armazena os equipamentos e suas localizações.
-- Dependências: usuario, modelo_equipamento, local_endereco

CREATE TABLE equipamento(
    id                    SERIAL PRIMARY KEY,
    usuario_id            INTEGER NOT NULL REFERENCES usuario(id),
    modelo_equipamento_id INTEGER NOT NULL REFERENCES modelo_equipamento(id),
    local_endereco_id     INTEGER NOT NULL REFERENCES local_endereco(id),
    codigo                VARCHAR(100) NOT NULL,
    data_criacao          TIMESTAMP NOT NULL DEFAULT NOW(),
    esta_ativo            BOOLEAN NOT NULL DEFAULT TRUE
);


-- TABELA: problema
-- Descrição: Registra problemas identificados nas instituições.
-- Dependências: usuario, categoria_equipamento, local_endereco

CREATE TABLE problema(
    id                       SERIAL PRIMARY KEY,
    usuario_id               INTEGER NOT NULL REFERENCES usuario(id),
    categoria_equipamento_id INTEGER NOT NULL REFERENCES categoria_equipamento(id),
    local_endereco_id        INTEGER NOT NULL REFERENCES local_endereco(id),
    titulo                   VARCHAR(100) NOT NULL,
    descricao_problema       VARCHAR(255) NOT NULL,
    descricao_local          VARCHAR(255) NOT NULL,
    motivo_recusa            VARCHAR(255),
    data_criacao             TIMESTAMP NOT NULL DEFAULT NOW(),
    status                   INTEGER NOT NULL DEFAULT 0, -- 0 = Pendente, 1 = Aprovado, 2 = Reprovado

    CONSTRAINT ck_motivo_recusa_status_recusado
        CHECK (
            (status = 2 AND motivo_recusa IS NOT NULL)
            OR
            (status <> 2 AND motivo_recusa IS NULL)
        )
);


-- TABELA: ocorrencia
-- Descrição: Registra ocorrências, ou seja, problemas não registrados, mas que já foram resolvidos
--            por um técnico.
-- Dependências: usuario, local_endereco, equipamento

CREATE TABLE ocorrencia(
    id                   SERIAL PRIMARY KEY,
    usuario_id           INTEGER NOT NULL REFERENCES usuario(id),
    local_endereco_id    INTEGER NOT NULL REFERENCES local_endereco(id),
    equipamento_id       INTEGER REFERENCES equipamento(id),
    categoria_problema   INTEGER NOT NULL,
    titulo               VARCHAR(100) NOT NULL,
    descricao_ocorrencia VARCHAR(255) NOT NULL,
    descricao_local      VARCHAR(255) NOT NULL,
    prioridade           INTEGER NOT NULL,
    data_criacao         TIMESTAMP NOT NULL DEFAULT NOW(),
    esta_ativo           BOOLEAN NOT NULL DEFAULT TRUE,

    CONSTRAINT ck_prioridade_ocorrencia_0_a_2
        CHECK (prioridade >= 0 AND prioridade <= 2)
);


-- ===================================================
-- ORDEM DE SERVIÇO / TAREFAS
-- ===================================================

-- TABELA: status_ordem_servico
-- Descrição: Define os status utilizados nas ordens de serviço e tarefas.
-- Dependências: -

CREATE TABLE status_ordem_servico(
    id        SERIAL PRIMARY KEY,
    nome      VARCHAR(100) NOT NULL,
    descricao VARCHAR(255)
);


-- TABELA: ordem_servico
-- Descrição: Registra as ordens de serviço e seu acompanhamento.
-- Dependências: problema, usuario, status_ordem_servico

CREATE TABLE ordem_servico(
    id                       SERIAL PRIMARY KEY,
    problema_id              INTEGER NOT NULL REFERENCES problema(id),
    usuario_id               INTEGER NOT NULL REFERENCES usuario(id),
    status_ordem_servico_id  INTEGER NOT NULL REFERENCES status_ordem_servico(id),
    categoria_problema       INTEGER NOT NULL,
    data_prevista            TIMESTAMP NOT NULL,
    prioridade               INTEGER NOT NULL,
    data_criacao             TIMESTAMP NOT NULL DEFAULT NOW(),

    CONSTRAINT ck_prioridade_os_0_a_2
        CHECK (prioridade >= 0 AND prioridade <= 2)
);


-- TABELA: ordem_servico_status_historico
-- Descrição: Mantém o histórico de status das ordens de serviço.
-- Dependências: ordem_servico, status_ordem_servico

CREATE TABLE ordem_servico_status_historico(
    id                       SERIAL PRIMARY KEY,
    ordem_servico_id         INTEGER NOT NULL REFERENCES ordem_servico(id) ON DELETE CASCADE,
    status_ordem_servico_id  INTEGER NOT NULL REFERENCES status_ordem_servico(id),
    data_atualizacao         TIMESTAMP NOT NULL DEFAULT NOW()
);


-- TABELA: tarefa
-- Descrição: Registra as tarefas vinculadas às ordens de serviço.
-- Dependências: ordem_servico, status_ordem_servico

CREATE TABLE tarefa(
    id                       SERIAL PRIMARY KEY,
    ordem_servico_id         INTEGER NOT NULL REFERENCES ordem_servico(id) ON DELETE CASCADE,
    status_ordem_servico_id  INTEGER NOT NULL REFERENCES status_ordem_servico(id),
    titulo                   VARCHAR(100) NOT NULL,
    descricao                VARCHAR(255) NOT NULL,
    data_criacao             TIMESTAMP NOT NULL DEFAULT NOW()
);


-- TABELA: tarefa_status_historico
-- Descrição: Mantém o histórico de status das tarefas.
-- Dependências: tarefa, status_ordem_servico

CREATE TABLE tarefa_status_historico(
    id                       SERIAL PRIMARY KEY,
    tarefa_id                INTEGER NOT NULL REFERENCES tarefa(id) ON DELETE CASCADE,
    status_ordem_servico_id  INTEGER NOT NULL REFERENCES status_ordem_servico(id),
    data_atualizacao         TIMESTAMP NOT NULL DEFAULT NOW()
);


-- ===================================================
-- FOTOS / TURNOS / OBSERVAÇÕES DE CONCLUSÃO
-- ===================================================

-- TABELA: observacao_conclusao
-- Descrição: Armazena observações relacionadas à conclusão das ordens.
-- Dependências: ordem_servico

CREATE TABLE observacao_conclusao(
    id               SERIAL PRIMARY KEY,
    ordem_servico_id INTEGER NOT NULL REFERENCES ordem_servico(id) ON DELETE CASCADE,
    dificuldade      INTEGER NOT NULL, -- 1 = Fácil, 2 = Médio, 3 = Difícil
    observacao       VARCHAR(255) NOT NULL,
    data_criacao     TIMESTAMP NOT NULL DEFAULT NOW()

    CONSTRAINT ck_dificuldade_observacao
        CHECK (dificuldade >= 1 AND dificuldade <= 3)
);


-- TABELA: foto
-- Descrição: Armazena fotos associadas às entidades do sistema.
-- Dependências: problema, ocorrencia, ordem_servico, observacao_conclusao, usuario

CREATE TABLE foto(
    id                       SERIAL PRIMARY KEY,
    problema_id              INTEGER REFERENCES problema(id),
    ocorrencia_id            INTEGER REFERENCES ocorrencia(id),
    ordem_servico_id         INTEGER REFERENCES ordem_servico(id) ON DELETE CASCADE,
    observacao_conclusao_id  INTEGER REFERENCES observacao_conclusao(id),
    usuario_id               INTEGER REFERENCES usuario(id),
    url                      VARCHAR(255) NOT NULL,
    esta_ativo               BOOLEAN NOT NULL DEFAULT TRUE,
    data_criacao             TIMESTAMP NOT NULL DEFAULT NOW(),

    CONSTRAINT ck_foto_apenas_uma_fk
        CHECK (
            (CASE WHEN problema_id              IS NOT NULL THEN 1 ELSE 0 END) +
            (CASE WHEN ocorrencia_id            IS NOT NULL THEN 1 ELSE 0 END) +
            (CASE WHEN ordem_servico_id         IS NOT NULL THEN 1 ELSE 0 END) +
            (CASE WHEN observacao_conclusao_id  IS NOT NULL THEN 1 ELSE 0 END) +
            (CASE WHEN usuario_id               IS NOT NULL THEN 1 ELSE 0 END)
            = 1
        )
);


-- TABELA: turno
-- Descrição: Define os turnos de funcionamento dos endereços.
-- Dependências: endereco

CREATE TABLE turno(
    id                   SERIAL PRIMARY KEY,
    endereco_id          INTEGER REFERENCES endereco(id) NOT NULL,
    nome                 VARCHAR(100) NOT NULL,
    hora_inicio          INTEGER NOT NULL,
    hora_fim             INTEGER NOT NULL,
    atravessa_meia_noite BOOLEAN NOT NULL DEFAULT FALSE,
    data_criacao         TIMESTAMP NOT NULL DEFAULT NOW(),
    esta_ativo           BOOLEAN NOT NULL DEFAULT TRUE,

    CONSTRAINT ck_hora_inicio_range
        CHECK (hora_inicio >= 0 AND hora_inicio <= 86400),

    CONSTRAINT ck_hora_fim_range
        CHECK (hora_fim >= 0 AND hora_fim <= 86400),

    CONSTRAINT ck_horas_consistentes
        CHECK (
            (atravessa_meia_noite = FALSE AND hora_inicio < hora_fim)
            OR
            (atravessa_meia_noite = TRUE AND hora_inicio > hora_fim)
        )
);


-- TABELA: turno_usuario
-- Descrição: Relaciona usuários aos seus respectivos turnos.
-- Dependências: turno, usuario

CREATE TABLE turno_usuario(
    id           SERIAL PRIMARY KEY,
    turno_id     INTEGER NOT NULL REFERENCES turno(id),
    usuario_id   INTEGER NOT NULL REFERENCES usuario(id),
    data_criacao TIMESTAMP NOT NULL DEFAULT NOW(),
    esta_ativo   BOOLEAN NOT NULL DEFAULT TRUE,

    CONSTRAINT uk_turno_usuario
        UNIQUE (turno_id, usuario_id)
);