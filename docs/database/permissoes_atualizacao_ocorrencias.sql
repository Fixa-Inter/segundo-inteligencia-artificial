-- Execute como administrador no banco da aplicação.
-- Complementa as permissões básicas de leitura já usadas pela Manu.
-- As roles devem existir. Administradores usam a conexão de manu_gestor.
-- Não executa atualizações de dados, não cria roles e não configura RLS.
-- Os filtros de autor, unidade e registro ativo são aplicados pela aplicação.

BEGIN;

GRANT SELECT (
    id, usuario_id, local_unidade_id, categoria_equipamento_id,
    categoria_problema, titulo, descricao_ocorrencia, descricao_local,
    prioridade, esta_ativo
)
ON TABLE public.ocorrencia
TO manu_tecnico, manu_gestor;

-- Inclui a permissão necessária ao SELECT ... FOR UPDATE OF o.
GRANT UPDATE (
    titulo, descricao_ocorrencia, descricao_local, local_unidade_id,
    categoria_equipamento_id, categoria_problema, prioridade, data_atualizacao
)
ON TABLE public.ocorrencia
TO manu_tecnico, manu_gestor;

GRANT SELECT (id, ocorrencia_id, url, esta_ativo)
ON TABLE public.foto
TO manu_tecnico, manu_gestor;

GRANT INSERT (ocorrencia_id, url)
ON TABLE public.foto
TO manu_tecnico, manu_gestor;

-- DELETE não admite restrição por coluna. A aplicação limita os registros
-- pelo ocorrencia_id após travar e conferir a ocorrência própria e ativa.
-- A substituição remove vínculos no PostgreSQL; não apaga arquivos do Cloudinary.
GRANT DELETE ON TABLE public.foto TO manu_tecnico, manu_gestor;

DO $$
DECLARE
    sequencia TEXT;
BEGIN
    sequencia := pg_get_serial_sequence('public.foto', 'id');
    IF sequencia IS NOT NULL THEN
        EXECUTE format('GRANT USAGE ON SEQUENCE %s TO manu_tecnico, manu_gestor', sequencia);
    END IF;
END;
$$;

COMMIT;
