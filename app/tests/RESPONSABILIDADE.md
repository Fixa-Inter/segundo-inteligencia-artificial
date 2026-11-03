# Responsabilidade: app/tests

## Objetivo do módulo

Verificar contratos e comportamento interno.

## O que deve ser armazenado aqui

Testes pytest, dublês de bancos/modelos/HTTP e regressões.

## Comportamento e limites atuais

Suíte anterior preservada sem alterar testes para acomodar regressões. conftest desativa tracing; cenários simulam integrações. A migração de timestamps e o catálogo SDD antes ausentes agora estão presentes. Novas caracterizações ficam em /tests.

Módulo pai: [app](../RESPONSABILIDADE.md).

## Funcionalidades disponíveis e arquivos

O catálogo registra os recursos existentes. Funções assíncronas usam `await`; ferramentas LangChain devem receber o contexto injetado. Símbolos com `_` são detalhes internos, cuja assinatura e regras devem ser conferidas antes de reutilizar.

### [conftest.py](conftest.py)

Desativa flags de tracing; não define fixtures compartilhadas.

### [test_administrador_chat.py](test_administrador_chat.py)

Verifica administrador chat; os cenários e auxiliares estão listados abaixo.

- `usuario_administrador() -> UsuarioContexto`.
- `test_perfil_autenticado_percorre_grafo_e_resposta(monkeypatch)`.
- `test_agentes_e_conexao_do_administrador_seguem_gestor()`.
- `test_ferramentas_registradas_do_administrador_sao_identicas_as_do_gestor()`.
- `test_prompt_administrador_herda_gestor_preservando_identidade()`.
- `test_administrador_nao_recebe_criacao_exclusiva_de_tecnico_e_solicitante()`.
- `test_consultas_do_administrador_preservam_unidade_e_edicao_de_ocorrencia_exige_autoria(monkeypatch)`.
- `test_faq_do_administrador_consulta_documentos_do_gestor(monkeypatch)`.

### [test_atualizacao_ocorrencia.py](test_atualizacao_ocorrencia.py)

Verifica atualizacao ocorrencia; os cenários e auxiliares estão listados abaixo.

- `registro()`.
- `fluxo(monkeypatch)`.
- `turno(fluxo, mensagem, imagens=None)`.
- `async selecionar(fluxo, **alteracoes)`.
- `apresentar(fluxo, resposta)`.
- `test_ferramentas_expostas_apenas_aos_tres_perfis_autorizados(monkeypatch, perfil)`.
- `test_solicitante_nao_consegue_chamar_tools_diretamente(fluxo)`.
- `test_selecao_mostra_apenas_titulo_descricao_e_metadados_de_ocorrencia(fluxo)`.
- `test_selecao_exige_apresentacao_persistida_em_outro_turno(fluxo, apresentada, novo_turno)`.
- `test_primeiro_aceite_preserva_campos_e_mostra_enums_legiveis(fluxo)`.
- `test_so_executor_aprovado_grava_uma_vez(fluxo, documentos, incerto)`.
- `test_mudanca_depois_da_apresentacao_exige_nova_conferencia(fluxo, campo)`.
- `test_fotos_iniciais_sao_preservadas_e_exigem_escolha_explicita(fluxo, acao)`.
- `test_categorias_seguem_ids_do_contrato(nome, identificador)`.
- `test_prioridade_invalida_nao_e_aceita(valor)`.
- `test_nao_seleciona_id_fora_dos_candidatos(fluxo)`.
- `test_busca_qdrant_restringe_autor_unidade_e_atividade(monkeypatch, perfil)`.
- `test_leitura_com_trava_exige_autoria_e_atividade_para_todos(monkeypatch, perfil)`.
- `test_transacao_altera_campos_enums_e_fotos_da_ocorrencia(monkeypatch, acao)`.
- `test_registro_indisponivel_ou_modificado_nao_sofre_escritas(monkeypatch, motivo)`.
- `test_falha_ao_inserir_foto_aborta_a_transacao(monkeypatch)`.
- `test_foto_recebida_invalida_proposta_sem_modificar_solicitacao(monkeypatch, fluxo)`.
- `test_roteador_e_supervisor_encaminham_atualizacao_de_ocorrencia(monkeypatch, fluxo)`.
- `test_no_guarda_coleta_como_atualizacao_e_injeta_a_ferramenta_correta(monkeypatch, fluxo, cadastro)`.
- `test_continuacao_preserva_modo_ocorrencia_sem_usar_rascunho_de_solicitacao(fluxo)`.
- `test_criacao_nao_processa_rascunho_de_atualizacao(monkeypatch, fluxo)`.
- `test_confirmacao_so_e_marcada_depois_de_persistir_a_resposta(monkeypatch, fluxo, etapa, falhar)`.

### [test_atualizacao_solicitacao.py](test_atualizacao_solicitacao.py)

Verifica atualizacao solicitacao; os cenários e auxiliares estão listados abaixo.

- `registro()`.
- `test_todos_perfis_recebem_atualizacao_e_listagem_feedbacks(monkeypatch, perfil)`.
- `fluxo(monkeypatch)`.
- `turno(fluxo, mensagem, imagens=None)`.
- `async selecionar(fluxo, **alteracoes)`.
- `apresentar(fluxo, resposta)`.
- `test_selecao_tem_titulo_e_descricao_consecutivos_e_passa_pelo_montador(fluxo)`.
- `test_aceite_da_selecao_nunca_prepara_operacao_e_mostra_resultado_final(fluxo, aceite)`.
- `test_aceite_de_identificacao_com_escolha_de_fotos_so_mostra_proposta_final(fluxo, mensagem, acao)`.
- `test_selecao_exige_apresentacao_persistida_em_turno_anterior(fluxo, apresentada, novo_turno)`.
- `test_fotos_da_mensagem_inicial_sao_preservadas_e_escolha_nao_pode_ser_inventada(fluxo)`.
- `test_pergunta_ou_negacao_nao_autoriza_substituir_fotos(fluxo, mensagem)`.
- `test_so_executor_aprovado_grava_e_segundo_aceite_nao_repete(fluxo, documentos, incerto)`.
- `test_alteracao_depois_do_aceite_invalida_a_operacao(fluxo, campo)`.
- `test_nao_seleciona_id_que_nao_veio_da_busca_propria(fluxo)`.
- `test_continuacao_preserva_operacao_de_atualizacao(fluxo)`.
- `test_nova_busca_descarta_selecao_e_conferencia_anteriores(fluxo)`.
- `test_nova_foto_recebida_no_no_invalida_apresentacao_anterior(monkeypatch, fluxo)`.
- `test_ferramenta_de_criacao_recusa_rascunho_de_atualizacao(fluxo)`.
- `test_busca_vetorial_filtra_unidade_e_ids_proprios_pendentes(monkeypatch)`.
- `test_campos_e_fotos_usam_mesma_transacao_sem_cloudinary(monkeypatch, acao)`.
- `test_status_ou_conteudo_alterado_bloqueia_todas_as_gravacoes(monkeypatch, motivo)`.
- `test_falha_ao_inserir_foto_aborta_a_transacao(monkeypatch)`.
- `test_confirmacao_so_fica_disponivel_depois_de_persistir_resposta(monkeypatch, fluxo, etapa, falhar)`.

### [test_auditoria_fluxo.py](test_auditoria_fluxo.py)

Verifica auditoria fluxo; os cenários e auxiliares estão listados abaixo.

- `test_novo_turno_fora_escopo_nao_herda_bloqueio_juiz(monkeypatch)`.
- `test_confirmacao_solicitacao_disponibiliza_contexto_roteador(monkeypatch)`.
- `test_cnpj_sem_pontuacao_anonimizado_inteiro()`.
- `test_pergunta_nao_autoriza_edicao()`.
- `test_cadastro_exige_confirmacao_posterior_proposta(monkeypatch)`.
- `test_saida_remove_dados_pessoais_sem_reescrever_texto()`.
- `test_instrucao_utiliza_data_atual_construcao(monkeypatch)`.
- `test_indicadores_recebe_ferramenta_dados_operacionais(monkeypatch)`.

### [test_auth.py](test_auth.py)

Verifica auth; os cenários e auxiliares estão listados abaixo.

- `test_obter_usuario_atual(monkeypatch) -> None`.
- `test_obter_usuario_sem_token() -> None`.
- `test_consulta_perfil_segue_contrato_api(monkeypatch) -> None`.

### [test_cadastro_solicitacao_contrato.py](test_cadastro_solicitacao_contrato.py)

Verifica cadastro solicitacao contrato; os cenários e auxiliares estão listados abaixo.

- `dados()`.
- `cliente_simulado(monkeypatch, status, corpo)`.
- `test_payload_segue_swagger_e_interpreta_sucesso(monkeypatch)`.
- `test_descricao_local_obrigatoria(descricao)`.
- `test_recusa_preserva_detalhe_sem_repetir_post(monkeypatch)`.
- `test_juiz_recebe_relato_anterior_e_confirmacao(monkeypatch)`.
- `test_revisao_somente_texto_limitada_a_uma_tentativa(monkeypatch)`.

### [test_chat.py](test_chat.py)

Verifica chat; os cenários e auxiliares estão listados abaixo.

- `usuario_teste(perfil: str='solicitante') -> UsuarioContexto`.
- `test_chat(monkeypatch, perfil, plataforma) -> None`.
- `test_chat_rejeita_resposta_vazia_sem_reenvio(monkeypatch, resposta_final) -> None`.
- Constantes, aliases e estado de módulo: `cliente`.

### [test_clientes_compartilhados.py](test_clientes_compartilhados.py)

Verifica clientes compartilhados; os cenários e auxiliares estão listados abaixo.

- `test_mongo_reutiliza_cliente_e_fecha_no_encerramento(monkeypatch)`.
- `test_lifespan_fecha_clientes_se_indice_falhar(monkeypatch)`.
- `test_qdrant_reutiliza_cliente_e_fecha_no_encerramento(monkeypatch)`.

### [test_coleta_parcial.py](test_coleta_parcial.py)

Verifica coleta parcial; os cenários e auxiliares estão listados abaixo.

- `test_foto_antiga_e_relato_continuam_ate_proposta_completa(monkeypatch, tipo)`.
- `test_especialista_recebe_coleta_e_foto_sem_novo_pedido(monkeypatch)`.
- `test_consulta_de_ocorrencias_nao_inicia_rascunho(monkeypatch)`.
- `test_primeira_mensagem_com_foto_anexa_ao_rascunho_parcial(monkeypatch)`.
- `test_coleta_parcial_nao_envia_cadastro(monkeypatch)`.

### [test_confirmacoes_continuacoes.py](test_confirmacoes_continuacoes.py)

Verifica confirmacoes continuacoes; os cenários e auxiliares estão listados abaixo.

- `test_aceites_compartilhados(mensagem)`.
- `test_perguntas_condicoes_correcoes_nao_autorizam(mensagem)`.
- `test_manifestacoes(mensagem, esperado)`.
- `proposta(pausado=False)`.
- `contexto()`.
- `test_sim_continua_proposta_ativa_sem_chamar_modelo(monkeypatch)`.
- `test_novo_assunto_pausa_rascunho_e_nao_prende_roteamento(monkeypatch)`.
- `test_detalhe_continua_coleta_sem_rascunho(monkeypatch)`.
- `test_sim_nao_retoma_rascunho_pausado()`.
- `test_operacoes_pendentes_persistidas(monkeypatch, mensagem, campo, valor)`.
- `test_duas_propostas_exigem_esclarecimento_sem_mutacao(monkeypatch)`.
- `test_pergunta_edicao_nao_executa_mutacao(monkeypatch)`.
- `test_imagem_sem_texto_continua_apos_validacao(monkeypatch)`.

### [test_consultas_ajuda_geral.py](test_consultas_ajuda_geral.py)

Verifica consultas ajuda geral; os cenários e auxiliares estão listados abaixo.

- `test_consultas_ficam_no_ajuda_geral_e_respeitam_perfil(monkeypatch, perfil, consultas_esperadas)`.
- `test_agente_de_cadastro_preserva_criacao_sem_consultas(monkeypatch, perfil, cadastros_esperados)`.
- `test_roteador_separa_consulta_de_cadastro_e_continuacao(monkeypatch, cadastro, continua, intencao_esperada)`.
- `test_consulta_pausa_rascunho_e_segue_para_ajuda_geral(monkeypatch)`.
- Constantes, aliases e estado de módulo: `CONSULTAS`, `CADASTROS`.

### [test_databricks_client.py](test_databricks_client.py)

Verifica databricks client; os cenários e auxiliares estão listados abaixo.

- `test_cliente_http_reutiliza_o_pool(monkeypatch)`.

### [test_databricks_service.py](test_databricks_service.py)

Verifica databricks service; os cenários e auxiliares estão listados abaixo.

- `resposta_sucesso(*, linhas=None, colunas=None, proximo_chunk=None)`.
- `configurar_cliente(monkeypatch)`.
- `test_consulta_enviada_com_parametro_nomeado_e_retorna_linhas(configurar_cliente)`.
- `test_consulta_pendente_faz_polling_e_busca_chunks(configurar_cliente)`.
- `test_erro_sql_retorna_excecao_sem_expor_como_sucesso(configurar_cliente)`.
- `test_erro_http_e_convertido_em_erro_do_cliente(configurar_cliente)`.
- `test_timeout_cancela_consulta_pendente(configurar_cliente)`.
- `test_sql_nao_select_ou_parametros_incompletos_sao_rejeitados(configurar_cliente)`.
- `test_falha_de_configuracao_indica_nomes_sem_exibir_segredos(monkeypatch, configurar_cliente)`.

### [test_encerramento_resumo.py](test_encerramento_resumo.py)

Verifica encerramento resumo; os cenários e auxiliares estão listados abaixo.

- `test_gerar_resumo_estruturado_valida_titulo_e_resumo(monkeypatch)`.
- `test_gerar_resumo_rejeita_saida_invalida(monkeypatch, titulo, resumo)`.
- `test_falha_ao_gerar_resumo_nao_altera_sessao(monkeypatch)`.
- `test_encerramento_inexistente_nao_acessa_documento(monkeypatch)`.
- `test_encerramento_de_outra_conta_nao_modifica_documento(monkeypatch)`.
- `test_titulo_e_resumo_persistem_nas_duas_consultas_de_historico(monkeypatch)`.
- `test_historico_legado_nao_interpreta_primeira_linha_como_titulo()`.

### [test_eventos.py](test_eventos.py)

Verifica eventos; os cenários e auxiliares estão listados abaixo.

- `dados_evento(**campos)`.
- `contexto_evento()`.
- `proposta_evento()`.
- `test_horarios_sem_fuso_sao_normalizados_e_passado_e_permitido()`.
- `test_horarios_com_fuso_preservam_instante_e_comparam_em_utc()`.
- `test_dados_invalidos_sao_recusados(campos)`.
- `test_campos_obrigatorios(campo)`.
- `simular_http(monkeypatch, status=200, corpo=None)`.
- `test_payload_bearer_identidade_e_datas_seguem_contrato(monkeypatch)`.
- `test_interpretacao_http_sem_repeticao(monkeypatch, status, corpo, esperado)`.
- `test_timeout_ou_resposta_invalida_nao_repetem_post(monkeypatch, falha)`.
- `local_evento(monkeypatch)`.
- `test_busca_filtra_unidade_autenticada(monkeypatch, contexto_evento, local_evento, perfil)`.
- `test_rascunho_contem_utc_e_rotulos_locais_sem_identidade(monkeypatch, contexto_evento, local_evento)`.
- `test_tools_negam_perfis_nao_autorizados(monkeypatch, contexto_evento, perfil)`.
- `test_proposta_nao_apresentada_ou_modificada_nao_prepara_envio(monkeypatch, contexto_evento, proposta_evento, alteracao)`.
- `test_aceites_parciais_identificam_campos(proposta_evento, contexto_evento, mensagem, campos)`.
- `test_vocabulario_de_eventos(mensagem, manifestacao)`.
- `test_aceite_de_outro_cadastro_nao_confirma_evento(proposta_evento, contexto_evento)`.
- `test_sim_continua_evento_e_resposta_publica_aceita_intencao(proposta_evento, contexto_evento)`.
- `test_envio_incerto_bloqueia_nova_preparacao(monkeypatch, contexto_evento, proposta_evento, status)`.
- `operacoes_evento(monkeypatch)`: Exercita o protocolo durável real com uma coleção local simulada.
- `motor_evento(monkeypatch, proposta_evento, local_evento, operacoes_evento)`.
- `estado_aprovado(contexto)`.
- `test_grafo_so_envia_evento_apos_juiz(monkeypatch, contexto_evento, proposta_evento, motor_evento, decisao, perfil, plataforma)`.
- `test_executor_nao_repete_post(monkeypatch, contexto_evento, proposta_evento, motor_evento, resultado_api)`.
- `test_alteracao_apos_aprovacao_impede_envio(contexto_evento, proposta_evento, motor_evento, alteracao)`.
- `test_confirmacao_parcial_persiste_somente_campos_aceitos(contexto_evento, proposta_evento, motor_evento)`.
- `test_coleta_correcao_e_arquivo_de_evento_preservam_outros_rascunhos(monkeypatch)`.
- `test_ferramentas_de_evento_sao_conectadas_apenas_aos_perfis_autorizados(monkeypatch, perfil)`.
- `test_coleta_e_retomo_do_rascunho_sao_injetados_sem_exigir_foto(monkeypatch, contexto_evento)`.
- `test_continuacao_atualiza_somente_proposta_de_evento(monkeypatch, contexto_evento, proposta_evento, mensagem)`.
- `test_confirmacao_publica_depende_de_proposta_apresentada_e_persistida(monkeypatch, contexto_evento, proposta_evento, falhar_persistencia)`.
- Constantes, aliases e estado de módulo: `ferramentas`, `busca`, `servico`.

### [test_evidencias.py](test_evidencias.py)

Verifica evidencias; os cenários e auxiliares estão listados abaixo.

- `chamada(nome, identificador)`.
- `retorno(identificador, conteudo, status='success')`.
- `test_multiplas_tools_preservam_resultados_e_excluem_historico_e_formato()`.
- `test_falhas_e_texto_faq_nao_sao_convertidos_em_sucesso_de_negocio()`.
- `test_coletor_acumula_evidencias_sem_mutar_estado()`.
- `test_no_solicitacoes_entrega_multiplas_evidencias_ao_grafo(monkeypatch)`.
- `test_nova_mensagem_limpa_evidencias_do_checkpoint()`.
- `test_no_solicitacoes_registra_estado_persistido_para_o_juiz(monkeypatch)`.

### [test_fluxo_integrado.py](test_fluxo_integrado.py)

Verifica fluxo integrado; os cenários e auxiliares estão listados abaixo.

- `executar_turno()`.
- `preparar_fluxo(monkeypatch, avaliacoes)`.
- `test_resposta_aprovada_passou_juiz_e_protecao_saida(monkeypatch)`.
- `test_revisao_texto_nao_repete_especialista(monkeypatch, segundo_veredito)`.
- `test_bloqueio_entrada_impede_especialista_e_juiz(monkeypatch)`.

### [test_graph_especialistas.py](test_graph_especialistas.py)

Verifica graph especialistas; os cenários e auxiliares estão listados abaixo.

- `criar_runtime()`.
- `criar_estado(perfil: str='gestor') -> dict`.
- `test_executar_analytics_gestor(monkeypatch) -> None`.
- `test_analytics_bloqueia_perfil_sem_permissao(monkeypatch) -> None`.
- `test_administrador_acessa_indicadores_gerenciais(monkeypatch) -> None`.
- `test_visualizacao_rejeita_sucesso_sem_consulta_executada(monkeypatch) -> None`.
- `test_visualizacao_bloqueia_perfil_sem_permissao(monkeypatch, perfil) -> None`.
- `test_executar_feedback(monkeypatch) -> None`.
- `test_especialista_rejeita_resposta_incompativel(monkeypatch) -> None`.
- `test_workflow_possui_todos_os_especialistas() -> None`.

### [test_graph_runner.py](test_graph_runner.py)

Verifica graph runner; os cenários e auxiliares estão listados abaixo.

- `dependencias_persistencia(monkeypatch)`.
- `criar_usuario() -> UsuarioContexto`.
- `test_executar_grafo_inicializa_estado_e_contexto(monkeypatch, plataforma) -> None`.
- `test_resposta_vazia_nao_e_persistida(monkeypatch, resposta_final) -> None`.

### [test_guardrail.py](test_guardrail.py)

Verifica guardrail; os cenários e auxiliares estão listados abaixo.

- `test_anonimizar_email() -> None`.
- `test_anonimizar_cpf(cpf) -> None`.
- `test_anonimizar_cnpj(cnpj) -> None`.
- `test_saida_omite_cnpj_inteiro(cnpj)`.
- `test_cpf_cnpj_mesma_mensagem_preservam_classificacao()`.
- `test_anonimizar_varios_dados() -> None`.
- `test_desanonimizar_omite_pii_por_padrao() -> None`.
- `test_desanonimizar_pode_restaurar_pii() -> None`.
- `test_bloquear_prompt_injection(monkeypatch) -> None`.
- `test_bloquear_tentativa_de_obter_credencial(monkeypatch) -> None`.
- `test_aprovar_mensagem_legitima(monkeypatch) -> None`.
- `test_bloquear_pedido_perigoso(monkeypatch) -> None`.
- `test_bloquear_pedido_ilicito(monkeypatch) -> None`.
- `test_falha_do_classificador_nao_derruba_chat(monkeypatch) -> None`.
- `test_guardrail_saida_remove_email() -> None`.
- `test_guardrail_saida_remove_cpf_resposta() -> None`.
- `test_guardrail_saida_preserva_texto_aprovado_juiz() -> None`.
- `test_guardrail_saida_omite_token_entrada(restaurar) -> None`.

### [test_health.py](test_health.py)

Verifica health; os cenários e auxiliares estão listados abaixo.

- `test_health_check() -> None`.
- Constantes, aliases e estado de módulo: `cliente`.

### [test_indicadores_agent.py](test_indicadores_agent.py)

Verifica indicadores agent; os cenários e auxiliares estão listados abaixo.

- `test_agente_indicadores_recebe_36_tools_sem_unidade_editavel(monkeypatch)`.
- `test_agente_permanece_com_resposta_estruturada(monkeypatch)`.
- `test_prompt_indica_tools_fronteiras_e_metricas_nao_disponiveis()`.
- `test_roteador_distingue_contagem_analytics_de_lista_de_registros(monkeypatch)`.

### [test_indicadores_ocorrencias.py](test_indicadores_ocorrencias.py)

Verifica indicadores ocorrencias; os cenários e auxiliares estão listados abaixo.

- `runtime(perfil='gestor')`.
- `unidade_autenticada(monkeypatch)`.
- `verificar_escopo(consulta, resultado, ferramenta)`.
- `periodo()`.
- `consulta_com_linhas(monkeypatch, linhas)`.
- `test_tool_total_ocorrencias_soma_gold_por_data_de_criacao(monkeypatch, unidade_autenticada)`.
- `test_tool_ocorrencias_por_tecnico_soma_por_tecnico_id(monkeypatch)`.
- `test_tool_ocorrencias_por_unidade_soma_por_unidade_id(monkeypatch)`.
- `test_tool_ocorrencias_por_local_soma_por_local_id(monkeypatch)`.
- `test_tool_ocorrencias_por_categoria_problema(monkeypatch)`.
- `test_tool_ocorrencias_bloqueia_nao_gestor_e_periodo_invalido(monkeypatch, unidade_autenticada)`.
- `test_tool_ocorrencias_por_categoria_equipamento(monkeypatch)`.
- `test_tool_ocorrencias_por_prioridade_preserva_codigos(monkeypatch)`.
- `test_tool_ocorrencias_ativas_representa_revisao_do_gestor(monkeypatch)`.
- `test_tool_taxa_alta_prioridade_calcula_codigo_zero_na_coorte(monkeypatch)`.
- `test_tool_ocorrencias_por_periodo_parametriza_granularidade(monkeypatch)`.
- `test_service_rejeita_granularidade_ocorrencia_invalida(monkeypatch)`.

### [test_indicadores_ordens_servico.py](test_indicadores_ordens_servico.py)

Verifica indicadores ordens servico; os cenários e auxiliares estão listados abaixo.

- `runtime(perfil='gestor')`.
- `unidade_autenticada(monkeypatch)`.
- `verificar_escopo(consulta, resultado, tabela)`.
- `executar_com_resultado(monkeypatch, resultado)`.
- `test_tool_total_os_consulta_gold_com_periodo_exclusivo(monkeypatch, unidade_autenticada)`.
- `test_tool_os_abertas_usa_status_atual_sem_periodo(monkeypatch, perfil)`.
- `test_tool_os_atrasadas_separa_status_de_prazo_vencido(monkeypatch)`.
- `test_tool_taxa_atraso_informa_numerador_e_denominador(monkeypatch)`.
- `test_tool_os_finalizadas_filtra_data_de_conclusao(monkeypatch)`.
- `test_tool_taxa_conclusao_prazo_preserva_cobertura_e_denominador(monkeypatch)`.
- `test_tool_tempo_espera_usa_os_tempos_e_timestamps(monkeypatch)`.
- `test_tools_bloqueiam_contexto_ou_unidade_nao_autorizados(monkeypatch, unidade_autenticada)`.
- `test_servicos_indicadores_exigem_unidade_valida_antes_de_consultar(monkeypatch)`.
- `test_tool_periodo_invertido_retorna_validacao_sem_consultar(monkeypatch)`.
- `test_tool_tempo_medio_resolucao_filtra_conclusao_valida(monkeypatch)`.
- `test_tool_tempo_medio_pausado_inclui_zero(monkeypatch)`.
- `test_tool_taxa_reabertura_consulta_coorte_criacao(monkeypatch)`.
- `test_tool_taxa_reatribuicao_consulta_coorte_criacao(monkeypatch)`.
- `test_tool_carga_ativa_tecnicos_e_snapshot_sem_periodo(monkeypatch)`.
- `test_tool_produtividade_tecnicos_filtra_data_de_conclusao(monkeypatch)`.
- `test_tool_media_tarefas_os_indisponivel_sem_contagens_do_bi(monkeypatch)`.

### [test_indicadores_problemas.py](test_indicadores_problemas.py)

Verifica indicadores problemas; os cenários e auxiliares estão listados abaixo.

- `runtime(perfil='gestor')`.
- `unidade_autenticada(monkeypatch)`.
- `verificar_escopo(consulta, resultado, ferramenta, tabela='gold_kpi_solicitacoes_diario')`.
- `executar_com_resultado(monkeypatch, resultado)`.
- `periodo()`.
- `test_tool_total_solicitacoes_soma_coorte_de_criacao(monkeypatch, unidade_autenticada)`.
- `test_tool_solicitacoes_pendentes_retraz_status_atual_da_coorte(monkeypatch)`.
- `test_tool_solicitacoes_aprovadas_retraz_status_atual_da_coorte(monkeypatch)`.
- `test_tool_solicitacoes_reprovadas_retraz_status_atual_da_coorte(monkeypatch)`.
- `test_tool_taxa_aprovacao_usa_todas_as_solicitacoes_como_base(monkeypatch)`.
- `test_tool_taxa_reprovacao_usa_todas_as_solicitacoes_como_base(monkeypatch)`.
- `test_tool_taxa_conversao_conta_solicitacao_uma_vez(monkeypatch)`.
- `test_tool_problema_exige_periodo_e_perfil_gestor(monkeypatch, unidade_autenticada)`.
- `test_tool_solicitacoes_por_unidade_retorna_ids_sem_nome(monkeypatch)`.
- `test_tool_solicitacoes_por_local_retorna_ids_sem_nome_tipo(monkeypatch)`.
- `test_tool_solicitacoes_por_categoria_equipamento(monkeypatch)`.
- `test_tool_solicitacoes_por_periodo_parametriza_granularidade(monkeypatch)`.
- `test_service_rejeita_granularidade_inesperada_sem_consultar(monkeypatch)`.
- `test_tool_taxa_recorrencia_agrupa_par_local_categoria_e_usa_timestamps(monkeypatch)`.

### [test_indice_faq.py](test_indice_faq.py)

Verifica indice faq; os cenários e auxiliares estão listados abaixo.

- `test_garantir_indice_faq_cria_somente_se_ausente(monkeypatch, indices)`.
- `test_lifespan_garante_indice_faq_antes_de_atender(monkeypatch)`.

### [test_jev_fluxos.py](test_jev_fluxos.py)

Verifica jev fluxos; os cenários e auxiliares estão listados abaixo.

- `respostas_roteador(intencao='solicitacao', confianca=0.9, continua=0.1)`.
- `respostas_juiz(veredito='aprovado', motivo='nenhum', sem_suporte=0.05, corrigivel=0.05, risco=0.05, confianca=0.9)`.
- `estado_juiz(evidencias=None)`.
- `test_roteamento_usa_historico_e_proposta_serializavel(monkeypatch)`.
- `test_roteamento_incerto_pede_esclarecimento_sem_pausar_proposta(monkeypatch)`.
- `test_juiz_distingue_falta_de_evidencia_de_falha_corrigivel(monkeypatch, evidencias, corrigivel, esperado)`.
- `test_juiz_bloqueia_risco_grave_mesmo_se_choice_aprova(monkeypatch)`.
- `test_motivo_inconsistente_com_baixa_confianca_nao_bloqueia(monkeypatch)`.
- `test_motivo_de_permissao_nao_e_ignorado_por_baixa_confianca(monkeypatch)`.
- `test_juiz_reavalia_uma_vez_bloqueio_sem_motivo(monkeypatch)`.
- `test_juiz_mantem_bloqueio_se_reavaliacao_continua_sem_motivo(monkeypatch)`.
- `test_juiz_nao_reavalia_risco_grave_sem_motivo(monkeypatch)`.
- `test_juiz_bloqueia_falha_de_transporte(monkeypatch)`.
- `test_respostas_invalidas_sao_rejeitadas()`.
- `test_endpoint_classificacao_preserva_contrato(monkeypatch)`.
- Constantes, aliases e estado de módulo: `juiz`.

### [test_limite_listagens.py](test_limite_listagens.py)

Verifica limite listagens; os cenários e auxiliares estão listados abaixo.

- `test_listagens_restringem_periodo_e_tres_mais_recentes(monkeypatch, modulo, consulta, coluna)`.
- `test_busca_filtrada_de_ordens_limita_resultados_sem_alterar_periodo_expresso(monkeypatch)`.
- `test_pendencias_do_gestor_mostram_cinco_mais_recentes(monkeypatch)`.
- `test_orientacao_da_consulta_atual_eh_exibida_uma_vez_no_final(monkeypatch)`.
- `test_orientacao_nao_aparece_quando_a_consulta_falha()`.
- `test_juiz_recebe_tabela_inteira_sem_repetir_linhas_estruturadas()`.
- `test_juiz_preserva_evidencia_grande_como_dado_estruturado()`.
- Constantes, aliases e estado de módulo: `HOJE`, `juiz`.

### [test_listar_feedbacks.py](test_listar_feedbacks.py)

Verifica listar feedbacks; os cenários e auxiliares estão listados abaixo.

- `test_listagem_usa_somente_id_autenticado_e_preserva_conteudo(monkeypatch, perfil)`.
- `test_lista_vazia_e_falha_de_consulta_sao_distintas(monkeypatch, falhar)`.
- `test_sem_autenticacao_nao_consulta_banco(monkeypatch)`.

### [test_memoria_negocio.py](test_memoria_negocio.py)

Verifica memoria negocio; os cenários e auxiliares estão listados abaixo.

- `preparar_cliente(monkeypatch, modulo, colecao)`.
- `test_salvar_mensagem_preserva_dono_e_anexos(monkeypatch)`.
- `test_confirmacao_da_resposta_persiste_e_aparece_no_historico(monkeypatch)`.
- `test_sessao_existente_nao_cria_segundo_documento(monkeypatch)`.
- `test_sessao_nova_fica_ativa_no_historico(monkeypatch)`.
- `test_sessao_acessivel_respeita_dono_e_estado_ativo(monkeypatch, documento, esperado)`.
- `test_acao_somente_inicia_se_ainda_aguarda_confirmacao(monkeypatch)`.

### [test_mensagens_timestamp.py](test_mensagens_timestamp.py)

Verifica mensagens timestamp; os cenários e auxiliares estão listados abaixo.

- `test_timestamp_e_instante_da_gravacao_e_atualizacao_da_sessao(monkeypatch, papel)`.
- `test_datas_bson_e_com_fuso_sao_expostas_em_utc(instante)`.
- `test_mensagem_antiga_expoe_null_sem_inventar_data()`.
- `test_endpoints_retornam_timestamps_reais_e_null_para_legados(monkeypatch, rota)`.
- `test_migracao_so_preenche_mensagens_sem_timestamp(monkeypatch)`.
- Constantes, aliases e estado de módulo: `salvar`, `historico`.

### [test_observabilidade_politica.py](test_observabilidade_politica.py)

Verifica observabilidade politica; os cenários e auxiliares estão listados abaixo.

- `test_politica_sobrescreve_flags_ativadas_e_cache(monkeypatch)`.
- `test_entrada_direta_nao_envia_traces_nem_herda_pai(falha)`.
- `test_middleware_desabilita_tracing_na_requisicao()`.
- `test_configuracao_prometheus_compose_e_dashboard_consistentes()`.
- Constantes, aliases e estado de módulo: `RAIZ`.

### [test_ocorrencias_enums_status.py](test_ocorrencias_enums_status.py)

Verifica ocorrencias enums status; os cenários e auxiliares estão listados abaixo.

- `dados()`.
- `test_contrato_http_sem_repetir_post(monkeypatch, codigo, esperado)`.
- `test_limites_e_numeros_rejeitados()`.
- `test_prioridade_e_status_fixos(monkeypatch, prioridade, identificador)`.
- `test_enums_documentados()`.
- `test_tecnicos_contam_status_por_id(monkeypatch)`.
- `test_confirmacao_foto_e_protecao_duplicidade(monkeypatch, foto_inicial)`.
- Constantes, aliases e estado de módulo: `ROOT`.

### [test_operacoes_aprovadas.py](test_operacoes_aprovadas.py)

Verifica operacoes aprovadas; os cenários e auxiliares estão listados abaixo.

- `contexto()`.
- `documentos(monkeypatch)`.
- `estado_aprovado(contexto)`.
- `test_preparacao_repetida_nao_grava_feedback_e_rejeita_dados_divergentes(monkeypatch, contexto, documentos)`.
- `test_cadastro_prepara_sem_post_e_so_executor_envia(monkeypatch, tipo, contexto, documentos, falhar_atualizacao)`.
- `test_sem_aprovacao_nao_executa(monkeypatch, contexto, documentos, veredito)`.
- `test_aprovacao_nao_serve_para_outros_dados_ou_contextos(monkeypatch, contexto, documentos, alteracao)`.
- `test_duas_execucoes_concorrentes_nao_repetem_gravacao(monkeypatch, contexto, documentos)`.
- `test_timeout_nao_libera_reenvio(monkeypatch, contexto, documentos)`.
- `test_falha_no_mongo_depois_do_sucesso_preserva_confirmacao(monkeypatch, contexto, documentos)`.
- `test_edicoes_e_anexos_aguardam_aprovacao(monkeypatch, contexto, documentos, tipo)`.
- `test_falha_do_agente_apos_preparar_nao_grava_e_juiz_bloqueia(monkeypatch, contexto, documentos)`.
- `test_grafo_completo_executa_feedback_somente_apos_juiz(monkeypatch, contexto, documentos, decisao)`.
- `test_resultado_real_sobrevive_a_falha_posterior(monkeypatch, contexto, falha)`.
- `test_resultados_parciais_sao_informados_separadamente(monkeypatch, contexto, documentos)`.
- `test_retorno_invalido_do_servico_nao_autoriza_repeticao(monkeypatch, contexto, documentos)`.
- `test_falha_ao_preparar_nao_registra_operacao_para_execucao(monkeypatch, contexto)`.
- `test_update_confirmado_nao_vira_recusa_se_releitura_nao_traz_detalhes(monkeypatch, contexto)`.

### [test_orquestrador.py](test_orquestrador.py)

Verifica orquestrador; os cenários e auxiliares estão listados abaixo.

- `decisao(intencao, *, continua, esclarecer=False, cadastro=None)`.
- `proposta(*, pausado=False)`.
- `runtime()`.
- `test_orquestrador_recebe_historico_e_rascunhos_ativos_e_pausados(monkeypatch)`.
- `test_detalhe_da_ocorrencia_mantem_rascunho_ativo(monkeypatch)`.
- `test_referencia_a_ocorrencia_pausada_retorna_ao_fluxo(monkeypatch)`.
- `test_retorno_a_ocorrencia_pausa_solicitacao_ativa(monkeypatch)`.
- `test_novo_registro_do_mesmo_tipo_pausa_o_rascunho_antigo(monkeypatch)`.
- `test_decisao_ambigua_nao_altera_propostas(monkeypatch)`.

### [test_permissoes_consultas.py](test_permissoes_consultas.py)

Verifica permissoes consultas; os cenários e auxiliares estão listados abaixo.

- `criar_usuario(perfil='solicitante')`.
- `test_solicitante_nao_consulta_colecao_restrita(monkeypatch, colecao)`.
- `test_limite_invalido_impede_consulta(monkeypatch, limite)`.
- `test_cursor_nao_transita_entre_unidades_colecoes(colecao, unidade)`.
- `test_registro_outra_unidade_rejeitado()`.
- `test_solicitante_sem_problemas_nao_consulta_vetor(monkeypatch)`.
- `test_problemas_solicitante_filtrados_usuario_unidade(monkeypatch)`.

### [test_propostas_cadastro.py](test_propostas_cadastro.py)

Verifica propostas cadastro; os cenários e auxiliares estão listados abaixo.

- `dados(tipo)`.
- `proposta(tipo='solicitacao')`.
- `contexto(mensagem='Sim')`.
- `test_proposta_invalida_nao_recebe_aceite(mudanca)`.
- `test_foto_posterior_preserva_aceite_sem_nova_confirmacao()`.
- `test_resumo_alteracao_mostra_somente_campo_pendente()`.
- `test_cadastro_respeita_aceite_e_versao(monkeypatch, tipo, mensagem)`.
- `test_versao_criada_mesmo_turno_nao_chama_backend(monkeypatch, tipo)`.
- `test_atualizar_rascunho_preserva_aceite_campos_inalterados(monkeypatch)`.
- `test_resumo_conferido_juiz_antes_de_ser_marcado_apresentado(monkeypatch)`.
- `test_revisao_altera_apenas_texto_e_mantem_resumo_uma_vez(monkeypatch)`.
- `test_contexto_temporal_converte_dia_timezone()`.
- `test_aceite_local_confirma_somente_local_e_preserva_restante()`.
- `test_aceite_foto_nao_confirma_dados_e_categoria_ambigua_esclarecida()`.
- `test_apresentacao_registrada_somente_depois_resposta_persistida(monkeypatch, falhar_resposta, marcada)`.
- `test_reapresentacao_da_proposta_controla_botao_de_confirmacao(monkeypatch, pausado, mostrar_resumo, esperado)`.
- `test_referencia_temporal_renovada_entre_invocacoes(monkeypatch)`.
- `test_conflito_versao_impede_envio(monkeypatch, tipo, falha_confirmacao)`.

### [test_respostas_padrao.py](test_respostas_padrao.py)

Verifica respostas padrao; os cenários e auxiliares estão listados abaixo.

- `evidencia(ferramenta='buscar_faq', resultado=TRECHO_FAQ_AUSENTE, status_execucao='success', status_operacao=None)`.
- `test_grafo_entrega_texto_padrao_sem_cadastro_ou_feedback_automatico(monkeypatch, intencao, status, retorno, texto)`.
- `test_falhas_permissoes_e_escritas_nao_sao_substituidas(evidencias, contexto, status, intencao)`.
- `test_nao_padroniza_sem_causa_identificada(status, intencao, evidencias)`.
- `test_marcador_nao_aprova_texto_livre_nem_erro()`.
- `test_fallback_tecnico_continua_diferente_de_funcionalidade_ausente()`.

### [test_sessao.py](test_sessao.py)

Verifica sessao; os cenários e auxiliares estão listados abaixo.

- `criar_usuario_teste() -> UsuarioContexto`.
- `test_encerrar_sessao_com_sucesso(monkeypatch)`.
- `test_encerrar_sessao_sem_autenticacao()`.
- `test_encerrar_com_bearer_valido_rejeita_id_invalido_ou_inexistente(monkeypatch, thread_id, status_esperado)`.
- `test_id_sessao_muito_longo_e_rejeitado(rota)`.
- `test_id_sessao_em_branco_e_rejeitado_antes_do_servico(monkeypatch, rota, servico, id_codificado)`.
- `test_id_sessao_valido_e_normalizado_antes_do_servico(monkeypatch, rota, servico, resultado)`.
- `test_value_error_do_encerramento_vira_422(monkeypatch)`.
- `test_consulta_sessao_em_branco_e_rejeitada_antes_do_servico(monkeypatch)`.
- `test_encerrar_sessao_sem_acesso_retorna_404_uniforme(monkeypatch, thread_id)`.
- `test_encerrar_sessao_propria_persiste_resumo(monkeypatch)`.
- `test_conversa_encerrada_pode_continuar_ate_ser_excluida_do_historico(monkeypatch)`.
- Constantes, aliases e estado de módulo: `cliente`.

### [test_visualizacoes_agent.py](test_visualizacoes_agent.py)

Verifica visualizacoes agent; os cenários e auxiliares estão listados abaixo.

- `dependencias(monkeypatch)`.
- `contexto()`.
- `chamada(analise_id='VIS-01', **alteracoes)`.
- Classe `ModeloRoteiro` (`BaseChatModel`): Produz lotes e uma resposta estruturada a partir dos ToolMessages reais.
  Campos/atributos declarados: `lotes: list[list[dict]]`.
  Métodos/validadores: `_llm_type(self)`; `bind_tools(self, tools, **kwargs)`; `_generate(self, messages, stop=None, run_manager=None, **kwargs)`.
- `executar(agente)`.
- `test_no_captura_sdk_real_com_escopo_isolado(monkeypatch, dependencias, concorrente)`.
- `test_fabrica_injeta_as_seis_tools_historico_schema_e_limite(monkeypatch)`.
- `test_extensoes_nao_substituem_tools_canonicas_com_mesmo_nome(monkeypatch)`.
- `test_registro_real_contem_tools_nos_especialistas_autorizados()`.
- `test_prompt_usa_catalogo_canonico_e_consulta_direta_sem_exemplos_numericos_inventados()`.
- `test_contrato_aceita_status_analiticos_e_so_sucesso_seleciona(status)`.
- `test_esclarecimento_ou_falha_de_geracao_nao_inventa_referencia(status)`.
- `test_uma_selecao_nao_aceita_lista_dados_inventados_ou_identificador_alterado(mudanca)`.
- `test_agente_real_seleciona_referencia_retornada_pela_tool(dependencias)`.
- `test_limite_tres_e_compartilhado_e_aplicado_antes_de_executar_lote(dependencias, paralelo)`.
- `test_tentativas_com_argumentos_invalidos_tambem_consumem_orcamento(dependencias)`.
- `test_historico_e_resposta_estruturada_nao_consumem_orcamento_analitico(monkeypatch, dependencias)`.
- `test_orcamento_e_isolado_por_execucao_do_mesmo_agente(dependencias, concorrente)`.
- Constantes, aliases e estado de módulo: `NOMES`.

### [test_visualizacoes_aprovacao.py](test_visualizacoes_aprovacao.py)

Verifica visualizacoes aprovacao; os cenários e auxiliares estão listados abaixo.

- `avaliacao(veredito='aprovado', incompatibilidade=0.05, sem_suporte=0.05)`.
- `cenario(monkeypatch)`.
- `julgar(c)`.
- `test_juiz_avalia_dados_e_libera_somente_apos_protecao(cenario)`.
- `test_candidata_invalida_nao_chega_ao_jev(cenario, campo)`.
- `test_incompatibilidade_exige_nova_consulta_e_nao_revisao_textual(cenario)`.
- `test_erro_ou_resposta_jev_incompleta_nao_libera_dados(cenario, caplog, erro)`.
- `test_alteracao_apos_aprovacao_impede_envio(cenario, campo)`.
- `test_guardrail_recusa_sem_dados_aprovados(monkeypatch, cenario, bloqueio)`.
- `test_redacao_de_pii_no_texto_preserva_dados(cenario)`.
- `test_revisao_recebe_dados_preserva_captura_e_exige_novo_julgamento(monkeypatch, cenario)`.
- `test_falha_revisao_nao_preserva_aprovacao(monkeypatch, cenario, falha)`.
- `test_resposta_sem_candidata_nao_inventa_grafico(cenario, status)`.
- `test_grafo_compilado_julga_revisa_e_libera_sem_repetir_consulta(monkeypatch, cenario, vereditos)`.
- `test_sucesso_parcial_preserva_avisos_no_julgamento_e_na_saida(cenario)`.
- `test_alteracao_durante_etapa_e_detectada(monkeypatch, cenario, etapa)`.
- `test_dados_sem_contexto_autenticado_nao_sao_avaliados(cenario)`.
- `test_registro_model_construct_tambem_e_revalidado(cenario)`.
- Constantes, aliases e estado de módulo: `juiz`.

### [test_visualizacoes_consultas_boxplots.py](test_visualizacoes_consultas_boxplots.py)

Verifica visualizacoes consultas boxplots; os cenários e auxiliares estão listados abaixo.

- `cliente(monkeypatch)`.
- `pedido(analise_id, filtros=None)`.
- `consultar(servico, analise_id, *, unidade_id=7, filtros=None)`.
- `amostra(campo, valores, *, inicio_id=1, **grupo)`.
- Classe `PercentilContinuo`.
  Métodos/validadores: `__init__(self)`; `step(self, valor, percentil)`; `finalize(self)`.
- `executar_amostra(cliente, fonte, linhas, transformar=None)`: Executa CTEs, joins e ranks reais; emula o percentil do dialeto Databricks.
- `test_tres_boxplots_usam_toda_populacao_e_quartis_interpolados(cliente, servico, analise_id, fonte, campo)`.
- `test_grupos_pequenos_usam_resumo_integrado(cliente, servico, analise_id, fonte, campo, n)`.
- `test_iqr_zero_preserva_caixa_sem_dispersao_inventada(cliente, valores, extremos)`.
- `test_observacoes_exatamente_nos_limites_pertencem_aos_bigodes(cliente)`.
- `test_grupos_mistos_resumos_nulos_e_sem_base_nao_desaparecem(cliente)`.
- `test_negativos_e_nulos_excluidos_zero_preservado(cliente, servico, analise_id, fonte, campo)`.
- `test_fonte_vazia_e_fonte_sem_elegiveis_diferem(cliente, servico, analise_id, fonte, campo)`.
- `test_limite_por_grupo_prioriza_afastamento_sem_recalcular_quartis(cliente)`.
- `test_limite_global_mantem_grupos_com_todos_os_extremos_omitidos(cliente)`.
- `test_extremos_inferiores_e_superiores_compartilham_prioridade_por_afastamento(cliente)`.
- `test_empates_sao_estaveis_e_extremos_iguais_de_os_distintas_nao_sao_deduplicados(cliente)`.
- `test_limite_de_grupos_nao_corta_grupos_silenciosamente(cliente, quantidade, status)`.
- `test_periodo_unidade_e_filtros_precedem_todas_as_estatisticas(cliente)`.
- `test_nao_finitos_nao_sao_descartados_como_negativos(cliente, valor)`.
- `test_chaves_nulas_ou_duplicadas_nao_alteram_grain_silenciosamente(cliente, chave)`.
- `test_estatisticas_incompativeis_nao_liberam_grafico(cliente, campo, valor)`.
- `test_selecao_incompleta_ou_incoerente_de_extremos_e_erro(cliente, mudanca)`.
- `test_unidade_retornada_diferente_do_escopo_e_erro(cliente)`.
- `test_unidade_invalida_nao_consulta(cliente, servico, analise_id, fonte, campo)`.
- `test_comparacao_entre_unidades_nao_e_liberada_por_filtro(cliente, filtros)`.
- `test_falhas_nao_liberam_estatisticas_parciais(cliente, erro, status)`.
- Constantes, aliases e estado de módulo: `CASOS`.

### [test_visualizacoes_consultas_histogramas.py](test_visualizacoes_consultas_histogramas.py)

Verifica visualizacoes consultas histogramas; os cenários e auxiliares estão listados abaixo.

- `cliente(monkeypatch)`.
- `pedido(analise_id, *, filtros=None)`.
- `consultar(servico, analise_id, *, filtros=None, unidade_id=7)`.
- `executar_amostra(cliente, fonte, linhas)`: Executa o SQL de agregação, adaptando tabela/DATE e fornecendo isnan.
- `amostra(campo, valores)`.
- `test_tres_histogramas_dez_intervalos_fronteiras_sem_dupla_contagem(cliente, servico, analise_id, fonte, campo)`.
- `test_valores_iguais_incluindo_zero_tem_intervalo_unico(cliente, servico, analise_id, fonte, campo, valor)`.
- `test_intervalos_vazios_recebem_frequencia_zero(cliente, servico, analise_id, fonte, campo)`.
- `test_fonte_sem_linhas_no_recorte_e_diferente_de_observacoes_nulas(cliente, servico, analise_id, fonte, campo)`.
- `test_tempos_negativos_excluidos_sao_contados_e_nulos_nao_viram_zero(cliente, servico, analise_id, fonte, campo)`.
- `test_so_tempos_negativos_nao_fabricam_intervalo_zero(cliente, servico, analise_id, fonte, campo)`.
- `test_populacao_maior_que_transporte_e_contada_por_inteiro(cliente, servico, analise_id, fonte, campo)`.
- `test_filtros_unidade_e_periodo_sao_aplicados_antes_da_faixa(cliente)`.
- `test_limites_decimais_contam_vizinhos_e_fronteiras_com_os_mesmos_numeros(cliente)`.
- `test_valores_nao_finitos_nao_sao_excluidos_silenciosamente_como_negativos(cliente, invalido)`.
- `test_quantidade_invalida_ou_nao_representavel_nao_recebe_intervalo_impreciso(cliente, invalido)`.
- `test_faixa_com_precisao_insuficiente_para_dez_intervalos_nao_e_deformada(cliente)`.
- `resposta()`.
- `test_resposta_incompativel_nao_libera_histograma(cliente, alteracao)`.
- `test_colunas_ausentes_nao_sao_preenchidas_com_zero(cliente, campo)`.
- `test_agregado_deve_ter_uma_linha(cliente, linhas)`.
- `test_unidade_invalida_impede_acesso_ao_histograma(cliente, servico, analise_id, fonte, campo)`.
- `test_histograma_nao_aceita_escopo_fonte_ou_numero_de_intervalos_livres(cliente, filtros)`.
- `test_falhas_nao_liberam_distribuicao_parcial_ou_detalhes_internos(cliente, erro, status)`.
- Constantes, aliases e estado de módulo: `CASOS`.

### [test_visualizacoes_consultas_medias.py](test_visualizacoes_consultas_medias.py)

Verifica visualizacoes consultas medias; os cenários e auxiliares estão listados abaixo.

- `cliente(monkeypatch)`.
- `pedido(analise_id, *, filtros=None)`.
- `consultar(servico, analise_id, *, filtros=None, unidade_id=7)`.
- `linha(grupo, *, valor='25.125', elegiveis='3', total='3', negativos='0')`.
- `test_sete_medias_usam_fonte_medida_e_base_sem_reescalar(cliente, servico, analise_id, campo, grupo)`.
- `test_tabela_vazia_difere_de_registros_sem_base(cliente, servico, analise_id, campo, grupo)`.
- `test_unidade_invalida_impede_consulta_de_medias(cliente, servico, analise_id, campo, grupo)`.
- `executar_amostra(cliente, fonte, linhas)`: Executa os agregados reais em SQLite, adaptando apenas tabela e DATE.
- `test_prazo_mantem_denominador_total_e_calcula_so_datas_validas_nao_nulas(cliente)`.
- `test_media_pausa_exclui_negativos_conta_exclusoes_e_mantem_zero(cliente)`.
- `test_pausa_sem_elegiveis_nao_apresenta_media_zero(cliente, valores, excluidos)`.
- `test_percentuais_usam_linhas_elegiveis_e_grupos_preservam_ids(cliente, analise_id, campo)`.
- `test_recorrencia_nao_pondera_media_pelo_numero_de_solicitacoes(cliente)`.
- `test_taxas_solicitacao_mantem_zero_real_e_excluem_nulos(cliente, analise_id, campo, grupo)`.
- `test_cobertura_global_soma_bases_sem_media_de_medias_e_mantem_grupo_sem_base(cliente)`.
- `test_medidas_ou_bases_incompativeis_nao_sao_coagidas_zeradas_ou_liberadas(cliente, alteracao)`.
- `test_campo_de_cobertura_ausente_nao_e_inventado(cliente, campo)`.
- `test_media_pausa_negativa_apos_exclusao_e_erro_de_resposta(cliente)`.
- `test_contagem_de_negativos_deve_ser_inteira_e_compativel_com_a_base(cliente, negativos)`.
- `test_negativos_sao_excluidos_apenas_das_analises_aprovadas_da_criacao()`.
- `test_percentuais_mensais_agrupam_diretamente_na_fonte(cliente, analise_id, servico)`.
- `test_categorias_excedentes_nao_entregam_cobertura_parcial_como_total(cliente)`.
- `test_flag_de_validade_nao_pode_ser_substituida_por_filtro_do_modelo(cliente)`.
- Constantes, aliases e estado de módulo: `CASOS`.

### [test_visualizacoes_consultas_os.py](test_visualizacoes_consultas_os.py)

Verifica visualizacoes consultas os; os cenários e auxiliares estão listados abaixo.

- `cliente(monkeypatch)`.
- `historica(analise_id='VIS-01', filtros=None, granularidade='dia')`.
- `snapshot(analise_id='VIS-03', filtros=None)`: Extrai dados originais para detectar mudança antes da escrita.
- `consultar(servico, pedido, unidade_id=7)`.
- `linha_diaria(dia='2026-10-02', valor='3', quantidade='3')`.
- `linha_status()`.
- `linha_tecnico(indice=1)`.
- `test_seis_analises_usam_fonte_medida_e_unidade_obrigatorias(cliente, servico, pedido, fonte, expressao)`.
- `test_nenhuma_analise_consulta_sem_unidade_valida(cliente, servico, pedido, fonte, expressao)`.
- `test_unidade_nao_e_coagida_para_inteiro(cliente, unidade)`.
- `test_series_sao_ordenadas_preenchem_lacunas_e_preservam_populacao(cliente)`.
- `test_periodo_e_inclusivo_no_inicio_e_exclusivo_no_fim(cliente, servico, analise_id)`.
- `test_tabela_de_conclusoes_vazia_nao_produz_serie_inventada_de_zeros(cliente)`.
- `test_status_snapshot_preserva_categoria_nula_e_timestamp_da_fonte(cliente)`.
- `test_carga_ativa_aplica_flag_obrigatoria_e_normaliza_id_sem_perda_de_precisao(cliente)`.
- `test_produtividade_usa_periodo_de_conclusao_e_nao_fonte_de_carga_ativa(cliente)`.
- `test_prazo_vencido_por_local_preserva_zero_real_e_nao_substitui_por_atraso(cliente)`.
- `test_multiplos_valores_usam_in_e_campos_diferentes_usam_and(cliente)`.
- `test_texto_com_sql_continua_sendo_apenas_valor_parametrizado(cliente)`.
- `test_servico_direto_rejeita_filtros_invalidos_antes_de_consultar(cliente, filtros)`.
- `test_consulta_incompativel_nao_e_executada(cliente, servico, pedido)`.
- `test_periodo_maior_que_366_dias_e_rejeitado_no_servico(cliente)`.
- `test_cinquenta_categorias_sao_aceitas_e_51_nao_sao_cortadas(cliente)`.
- `test_falhas_nao_liberam_dados_nem_detalhes_de_excecao(cliente, caplog, erro, status)`.
- `test_resposta_inconsistente_nao_vira_grafico(cliente, linhas)`.
- `test_rotulo_ausente_na_resposta_nao_e_inventado(cliente)`.
- `test_categoria_repetida_no_resultado_nao_e_contada_novamente(cliente)`.
- `test_alteracao_do_pedido_durante_await_nao_muda_metadados_da_consulta(cliente)`.
- Constantes, aliases e estado de módulo: `CASOS`.

### [test_visualizacoes_consultas_volumes.py](test_visualizacoes_consultas_volumes.py)

Verifica visualizacoes consultas volumes; os cenários e auxiliares estão listados abaixo.

- `cliente(monkeypatch)`.
- `pedido(analise_id, *, filtros=None, dias=3, inicio=date(2026, 10, 1))`.
- `consultar(servico, consulta, unidade_id=7)`.
- `prioridade(codigo, nome, dia='2026-10-02', valor='1', quantidade='1')`.
- `test_oito_consultas_usam_fonte_medida_agrupamento_e_escopo_corretos(cliente, servico, analise_id, fonte, medida, dimensoes, linha)`.
- `test_nenhuma_consulta_executa_sem_unidade(cliente, servico, analise_id, fonte, medida, dimensoes, linha)`.
- `test_fonte_vazia_nao_cria_categorias_nem_calendario_de_zeros(cliente, servico, analise_id, fonte, medida, dimensoes, linha)`.
- `test_solicitacoes_por_dia_preenchem_lacunas_sem_aumentar_populacao(cliente)`.
- `test_status_de_solicitacao_e_aplicado_somente_na_fonte_correta(cliente)`.
- `test_recorrencia_preserva_ids_textuais_zeros_a_esquerda_e_locais_homonimos(cliente)`.
- `test_prioridades_preenchem_cada_grupo_e_mantem_ordem_com_dimensoes_nulas(cliente)`.
- `test_nao_inventa_grupo_para_prioridade_sem_registros_no_periodo(cliente)`.
- `test_prioridade_com_nome_nulo_nao_ganha_rotulo_inferido(cliente)`.
- `test_limite_de_500_pontos_e_global_e_inclui_lacunas_de_todos_os_grupos(cliente)`.
- `test_serie_aceita_50_grupos_e_rejeita_51_sem_cortar(cliente)`.
- `test_mesmo_dia_em_prioridades_distintas_e_valido_mas_ponto_duplicado_e_rejeitado(cliente)`.
- `test_coluna_de_prioridade_ausente_nao_e_convertida_em_grupo_nulo(cliente)`.
- `test_alta_prioridade_usa_flag_publicada_e_preserva_zero_real(cliente)`.
- `test_filtros_de_ocorrencia_preservam_booleanos_e_valores_parametrizados(cliente)`.
- `test_analises_de_outra_fonte_nao_sao_substituidas_por_contagens(cliente, servico, analise_id)`.
- `test_mes_e_semana_agrupam_na_fonte_sem_reinterpretar_como_dias(cliente, servico, analise_id)`.
- `test_fontes_historicas_nao_recebem_consulta_de_snapshot(cliente, servico, analise_id)`.
- `test_timeout_nos_novos_dominios_nao_libera_dados(cliente, servico, analise_id)`.
- Constantes, aliases e estado de módulo: `CASOS`.

### [test_visualizacoes_contratos.py](test_visualizacoes_contratos.py)

Verifica visualizacoes contratos; os cenários e auxiliares estão listados abaixo.

- `consulta(analise_id='VIS-01', *, filtros=None, granularidade='dia')`.
- `metadados(analise_id='VIS-01')`.
- `grupo_boxplot(**alteracoes)`.
- `test_periodo_usa_datas_explicitas_e_fim_exclusivo()`.
- `test_periodo_nao_aceita_intervalo_invalido_ou_timestamp_implicito(alteracao)`.
- `test_contexto_autenticado_e_fonte_nao_sao_argumentos_do_modelo(campo)`.
- `test_contrato_snapshot_nao_oferece_parametros_temporais(campo, valor)`.
- `test_validacao_impede_escolha_de_analise_de_outra_tool()`.
- `test_validacao_recusa_periodo_no_snapshot_e_exige_periodo_nas_demais_fontes()`.
- `test_series_exigem_granularidade_e_outros_formatos_nao_a_aceitam()`.
- `test_filtros_multiplos_preservam_valores_sem_escolher_outro_escopo()`.
- `test_contrato_filtro_recusa_selecao_vazia_e_operadores_arbitrarios(valor)`.
- `test_valores_de_filtro_respeitam_tipo_sem_conversao_silenciosa(filtros)`.
- `test_ids_textuais_de_recorrencia_nao_sao_convertidos_em_inteiros()`.
- `test_filtros_nao_contradizem_populacao_obrigatoria_de_os_abertas()`.
- `test_flag_booleana_de_ocorrencia_nao_aceita_inteiro_no_lugar_de_booleano()`.
- `test_contrato_preserva_grupos_nulos_valor_zero_e_ausencia_de_base()`.
- `test_medidas_nao_aceitam_booleanos_texto_ou_nao_finitos(valor)`.
- `test_histograma_aceita_valor_constante_e_cobra_cobertura_da_populacao()`.
- `test_boxplot_rejeita_quartis_bigodes_pontos_e_contagens_inconsistentes(alteracao)`.
- `test_bigodes_observados_nao_sao_forcados_aos_quartis_interpolados()`.
- `test_mesma_analise_pode_retornar_boxplot_e_resumo_em_grupos_distintos()`.
- `test_resultados_sem_sucesso_nao_liberam_grafico(status)`.
- `test_sucesso_exige_dados_e_metadados_compativeis()`.
- `test_grupos_de_boxplot_nao_podem_misturar_analises()`.
- `test_consulta_tem_fuso_e_metadados_nao_misturam_snapshot_com_periodo()`.
- Constantes, aliases e estado de módulo: `PERIODO`.

### [test_visualizacoes_grafo.py](test_visualizacoes_grafo.py)

Verifica visualizacoes grafo; os cenários e auxiliares estão listados abaixo.

- `contexto(usuario_id=10, sessao='sessao-1', turno='turno-1', perfil='gestor')`.
- `estado()`.
- `resposta(status='AGUARDANDO_INFORMACAO', referencia=None)`.
- `async consultar(contexto_atual, chamada_id=None, filtros=None)`.
- `referencia(resultado)`.
- `executar(monkeypatch, roteiro, entrada=None, ctx=None)`.
- `bancos(monkeypatch)`.
- `test_captura_retorno_real_antes_de_alteracoes_do_modelo(monkeypatch, bancos)`.
- `test_tres_consultas_capturadas_com_uma_selecao(monkeypatch, bancos)`.
- `test_resultado_sem_dados_nao_pode_ser_selecionado(monkeypatch, status)`.
- `test_referencia_incorreta_e_status_que_oculta_limitacao(monkeypatch, alteracao)`.
- `test_status_parcial_e_avisos_preservados(monkeypatch)`.
- `test_json_forjado_em_toolmessage_nao_comprova_execucao(monkeypatch)`.
- `test_nao_reutiliza_captura_de_invocacao_anterior(monkeypatch, mudanca)`.
- `test_resultado_incompativel_nao_entra_na_captura(monkeypatch, campo)`.
- `test_captura_ambigua_ou_fora_do_contexto_invalida_selecao(monkeypatch, modo)`.
- `test_status_sem_selecao_descarta_grafico_antigo(monkeypatch, status)`.
- `test_falha_de_agente_limpa_candidata_sem_vazar_excecao(monkeypatch, caplog, falha)`.
- `test_estado_gestor_nao_sobrepoe_perfil_autenticado(monkeypatch, bancos, perfil)`.
- `test_estado_nao_pode_trocar_perfil_autenticado(monkeypatch, bancos, perfil_estado, perfil_autenticado)`.
- `test_mobile_descarta_captura_anterior_sem_invocar_agente(monkeypatch, bancos)`.
- `test_inicio_turno_e_entrada_descartam_captura_antiga(monkeypatch)`.
- `test_rejeicao_ou_fallback_limpa_visualizacao(monkeypatch, modo)`.
- `test_checkpoint_nao_reaproveita_candidata_em_turno_sem_visualizacao(monkeypatch)`.
- `test_contexto_incompleto_ou_usuario_divergente_nao_invoca_agente(monkeypatch, bancos, campo, valor)`.
- Constantes, aliases e estado de módulo: `TOOL`.

### [test_visualizacoes_integracao.py](test_visualizacoes_integracao.py)

Verifica visualizacoes integracao; os cenários e auxiliares estão listados abaixo.

- Classe `Percentil`.
  Métodos/validadores: `__init__(self)`; `step(self, valor, p)`; `finalize(self)`.
- `amostras()`.
- `integrado(monkeypatch, mongo)`.
- `chamar(c, identificador, granularidade='dia', plataforma='web')`.
- `test_mobile_bloqueia_antes_do_agente_e_das_consultas(integrado, identificador, perfil)`.
- `test_mobile_continua_usando_outros_especialistas(integrado, monkeypatch)`.
- `test_alternar_plataforma_na_mesma_conversa_nao_reutiliza_grafico(integrado)`.
- `test_27_analises_e_calendarios_ate_o_historico(integrado, identificador, granularidade, perfil)`.
- `test_falhas_de_conclusao_nao_publicam_grafico(integrado, identificador, falha)`.
- `test_perfil_sem_acesso_nao_executa_consulta(integrado, perfil)`.
- `test_histograma_zero_negativos_e_nulos_ate_a_api(integrado, identificador)`.
- `test_boxplot_pequeno_publica_resumo_com_cobertura(integrado, identificador)`.
- `test_extremos_limitados_preservam_estatisticas_e_omissoes(integrado)`.
- `test_sla_agrega_populacao_e_filtra_datas_invalidas(integrado)`.
- `test_ausencia_de_base_nao_e_convertida_em_zero(integrado, identificador)`.
- `test_vinculo_ausente_impede_warehouse(integrado)`.
- `test_metricas_medem_sem_identificadores_ou_conteudo(integrado)`.
- `test_analise_desconhecida_nao_cria_rotulo_com_entrada_recebida(integrado)`.
- Constantes, aliases e estado de módulo: `juiz`, `salvar`, `CASOS`.

### [test_visualizacoes_limites.py](test_visualizacoes_limites.py)

Verifica visualizacoes limites; os cenários e auxiliares estão listados abaixo.

- `consulta(dias=366, filtros=None)`.
- `resumo(indice=1, quantidade=1)`.
- `boxplot(extremos=0, indice=1, quantidade=100)`.
- `test_periodo_aceita_366_dias_e_rejeita_367_sem_mudar_as_datas()`.
- `test_snapshot_continua_sem_receber_periodo()`.
- `test_filtro_aceita_50_valores_e_rejeita_51_sem_remover_selecoes()`.
- `test_limite_de_filtros_e_por_campo()`.
- `test_categorias_aceitam_50_e_rejeitam_51_sem_recortar()`.
- `test_limite_de_series_conta_pontos_de_lacunas_sem_registros()`.
- `test_limite_de_grupos_na_serie_e_independente_do_limite_de_pontos()`.
- `test_mesmo_grupo_em_datas_distintas_nao_e_contado_como_grupos_diferentes()`.
- `test_grupos_de_resumo_tambem_entram_no_limite_do_grafico()`.
- `test_pontos_extremos_respeitam_limites_por_grupo_e_no_total()`.
- `test_contagem_total_de_extremos_nao_e_limitada_aos_pontos_enviados()`.
- `test_validador_de_resultado_preserva_a_regra_de_tamanho_minimo_do_boxplot()`.
- `test_histograma_nao_excede_dez_intervalos()`.

### [test_visualizacoes_persistencia.py](test_visualizacoes_persistencia.py)

Verifica visualizacoes persistencia; os cenários e auxiliares estão listados abaixo.

- `origem(monkeypatch, request)`.
- `avaliar(expressao, doc)`: Compara requisitos às ofertas e valida trechos citados contra anúncios recebidos.
- Classe `Colecao`.
  Métodos/validadores: `__init__(self)`; `corresponde(self, filtro)`; `update_one(self, filtro, alteracao)`; `find_one(self, filtro, projecao=None, **kwargs)`.
- `mongo(monkeypatch)`.
- `gravar(origem, turno='turno')`.
- `test_mesmo_payload_publico_persistido_e_recuperado(origem, mongo, capsys)`.
- `test_publicacao_rejeita_alteracao_ou_falta_de_aprovacao(origem, campo)`.
- `test_limite_utf8_exato_sem_truncar(origem)`.
- `test_nao_grava_grafico_em_papel_ou_turno_invalidos(origem, mongo, papel, turno)`.
- `test_repeticao_identica_nao_duplica_e_conflito_nao_substitui(origem, mongo, monkeypatch)`.
- `test_gravacao_filtra_dono_sessao_e_conversa_ativa(origem, mongo, campo, valor)`.
- `test_quota_atomica_em_gravacoes_concorrentes(monkeypatch, origem, mongo)`.
- `test_dolar_em_rotulo_permanece_literal(origem, mongo)`.
- `test_falha_mongo_nao_confirma_gravacao(origem, mongo, monkeypatch)`.
- `test_historico_antigo_e_perfil_sem_exposicao(origem, mongo)`.
- `test_api_preserva_nulos_e_mesmo_payload(monkeypatch, origem, mongo, rota)`.
- `test_api_historico_so_expoe_grafico_ao_gestor_dono(monkeypatch, origem, mongo, perfil)`.
- `test_executor_persiste_antes_de_disponibilizar_ao_chat(monkeypatch, origem, falha)`.
- `test_contrato_textual_continua_sem_campo_visualizacao()`.
- `test_api_com_executor_e_persistencia_reais_no_mongo_simulado(monkeypatch, origem, mongo, recusa)`.
- `test_contrato_publico_recusa_conteudo_invalido(origem, alteracao)`.
- `test_historico_incompativel_nao_recalcula_nem_vaza_dados(origem, mongo)`.
- `test_nome_e_id_do_tecnico_preservados(origem, mongo)`.
- Constantes, aliases e estado de módulo: `salvar`, `historico`, `juiz`.

### [test_visualizacoes_regras.py](test_visualizacoes_regras.py)

Verifica visualizacoes regras; os cenários e auxiliares estão listados abaixo.

- `test_catalogo_cobre_exatamente_os_ids_do_sdd()`.
- `test_selecao_rejeita_analises_fora_do_catalogo(identificador)`.
- `test_tool_de_uma_fonte_nao_pode_selecionar_analise_de_outra()`.
- `test_filtros_nao_ampliam_escopo_nem_escolhem_sql(analise_id, campo)`.
- `test_status_de_solicitacao_nao_se_aplica_a_recorrencia(campo)`.
- `test_snapshot_nao_oferece_data_de_criacao_como_filtro_de_periodo(analise_id)`.
- `test_entrada_e_saida_tem_fontes_distintas_e_contagens_corretas()`.
- `test_percentuais_sao_medias_em_escala_100_sem_zerar_ausencia()`.
- `test_tempos_excluem_nulos_e_estatistica_pendente_nao_recebe_agregacao()`.
- `test_regras_obrigatorias_preservam_populacao_e_semantica()`.
- `test_boxplot_por_unidade_nao_concede_filtro_de_unidade()`.
- `test_ids_de_recorrencia_preservam_tipo_textual_fornecido_pelo_bi()`.
- `test_selecao_nao_permite_alterar_o_catalogo_compartilhado()`.

### [test_visualizacoes_resumos.py](test_visualizacoes_resumos.py)

Verifica visualizacoes resumos; os cenários e auxiliares estão listados abaixo.

- `resumir(valores, *, grupo=None)`.
- `test_calcula_resumo_da_populacao_com_um_a_quatro_registros(valores, media, mediana)`.
- `test_exclui_nulos_preservando_zeros_e_conta_somente_observacoes_validas()`.
- `test_grupo_vazio_nao_ganha_resumo_com_valores_zero(valores)`.
- `test_nao_trunca_grupo_elegivel_para_boxplot_para_caber_no_resumo(valores)`.
- `test_limite_considera_nao_nulos_e_nao_o_tamanho_da_lista()`.
- `test_valores_iguais_preservam_ausencia_de_dispersao()`.
- `test_nao_arredonda_observacoes_antes_das_estatisticas()`.
- `test_entrada_invalida_nao_e_descartada_silenciosamente(valor)`.
- `test_preserva_identidade_e_campos_do_grupo_em_cada_analise(analise_id)`.
- `test_nao_inventa_rotulo_para_dimensao_nula()`.
- `test_rejeita_dimensoes_que_nao_correspondem_a_analise(grupo)`.
- `test_resumo_nao_substitui_outros_tipos_de_analise()`.
- `test_serializacao_preserva_identificacao_estatisticas_e_motivo()`.
- `test_contrato_rejeita_resumo_inconsistente(alteracao)`.

### [test_visualizacoes_series_temporais.py](test_visualizacoes_series_temporais.py)

Verifica visualizacoes series temporais; os cenários e auxiliares estão listados abaixo.

- `cliente(monkeypatch)`.
- `pedido(analise_id, granularidade, inicio='2026-10-05', fim='2026-10-08', filtros=None)`.
- `consultar(servico, consulta, unidade_id=7)`.
- `linha(campo, valor, dia='2026-10-05', **extras)`.
- `executar_amostra(cliente, fonte, linhas)`: Executa agregados reais em SQLite, adaptando tabela, DATE e TRUNC.
- `test_seis_series_em_tres_granularidades_calculam_na_fonte(cliente, servico, analise_id, campo, percentual, granularidade)`.
- `test_semanas_parciais_nao_ampliam_unidade_ou_datas_solicitadas(cliente)`.
- `test_meses_parciais_com_mes_vazio_preservam_recorte_e_distincao_de_parcial(cliente)`.
- `test_fim_exclusivo_alinhado_nao_cria_proximo_periodo(cliente, granularidade, inicio, fim, ultimo)`.
- `test_semana_de_janeiro_pode_ter_referencia_no_ano_anterior(cliente)`.
- `test_percentuais_agregam_linhas_sem_media_de_medias_e_lacunas_sao_nulas(cliente, granularidade, inicio, fim, primeiro, ultimo)`.
- `test_cobertura_de_prazo_mantem_datas_invalidas_no_total(cliente, granularidade, inicio, fim)`.
- `test_grupos_de_prioridade_observados_incluem_nulos_sem_inventar_outros(cliente, granularidade, inicio, fim)`.
- `test_limite_500_e_global_e_inclui_lacunas_por_grupo(cliente, granularidade, fim, status)`.
- `test_limite_de_grupos_nao_e_relaxado_com_agregacao(cliente, granularidade)`.
- `test_fonte_vazia_nao_inventa_calendario(cliente, granularidade)`.
- `test_referencias_desalinhadas_ou_fora_do_calendario_nao_sao_arredondadas(cliente, granularidade, referencia)`.
- `test_pontos_duplicados_no_mesmo_periodo_sao_erro(cliente, granularidade)`.
- `test_calendario_nao_afrouxa_periodo_maximo_ou_unidade(cliente, granularidade)`.
- `test_granularidade_adulterada_e_revalidada_antes_do_sql(cliente)`.
- `test_calendario_irrepresentavel_e_recusado_antes_de_acessar_fonte(cliente, granularidade)`.
- `test_contrato_recusa_indicacao_parcial_falsa_e_recorte_fora_do_calendario()`.
- `test_contrato_confronta_trecho_consultado_com_recorte_dos_metadados(cliente)`.
- `test_calendario_respeita_segunda_feira_meses_e_anos_bissextos(referencia, granularidade, inicio, seguinte)`.
- `test_granularidade_sql_vem_de_lista_fechada(granularidade, expressao)`.
- `test_calendario_recusa_granularidades_nao_aprovadas(granularidade)`.
- `test_calendario_nao_inventa_datas_apos_ano_maximo(granularidade)`.
- Constantes, aliases e estado de módulo: `CASOS`.

### [test_visualizacoes_tools.py](test_visualizacoes_tools.py)

Verifica visualizacoes tools; os cenários e auxiliares estão listados abaixo.

- `usuario(perfil='gestor', usuario_id=10)`.
- `runtime(perfil='gestor', usuario_id=10, contexto=None)`.
- `argumentos(analise_id='VIS-01')`.
- `resultado_vazio(consulta, unidade_id)`.
- `dependencias(monkeypatch)`.
- `invocar(fonte='os_criacao', dados=None, contexto_runtime=None)`.
- `test_mobile_nao_executa_tool_mesmo_com_gestor_valido(dependencias, fonte)`.
- `test_schema_mostra_so_argumentos_e_analises_da_fonte(fonte)`.
- `test_27_analises_resolvem_unidade_no_servidor_e_despacham_no_dominio(dependencias, fonte, analise_id, perfil)`.
- `test_analise_de_outra_fonte_e_rejeitada_antes_da_unidade(dependencias, fonte)`.
- `test_outros_perfis_nao_sao_autorizados_pelo_estado_que_diz_gestor(dependencias, perfil)`.
- `test_contexto_nao_autenticado_nao_pode_ser_substituido_por_id_solto(dependencias, contexto)`.
- `test_runtime_ausente_e_negado_sem_excecao_de_assinatura(dependencias)`.
- `test_usuario_invalido_ou_adulterado_e_negado(dependencias, identificador)`.
- `test_unidade_resolvida_invalida_nao_vira_consulta_sem_escopo(dependencias, unidade)`.
- `test_vinculo_nao_confirmado_nao_tem_fallback_ou_detalhes_sensiveis(dependencias, caplog, erro, status)`.
- `test_argumentos_protegidos_nao_sao_aceitos_pelo_sdk(dependencias, campo)`.
- `test_runtime_em_json_nao_e_tratado_como_objeto_injetado(dependencias)`.
- `test_snapshot_recusa_campos_temporais_mesmo_nulos(dependencias, campo, valor)`.
- `test_filtros_invalidos_sao_rejeitados_antes_de_resolver_unidade(dependencias, filtros)`.
- `test_periodo_e_granularidade_incompativeis_sao_rejeitados_sem_banco(dependencias)`.
- `test_filtros_textuais_de_recorrencia_mantem_zeros_e_multiplos_valores(dependencias)`.
- `test_status_dos_servicos_nao_sao_convertidos_em_graficos(dependencias, status)`.
- `test_resultado_de_consulta_diferente_nao_e_liberado(dependencias, alteracao)`.
- `test_excecao_inesperada_do_servico_nao_vaza_detalhes(dependencias, caplog)`.
- `test_chamadas_concorrentes_nao_compartilham_unidade_resolvida(dependencias)`.
- `test_argumentos_sao_copiados_antes_do_await_de_unidade(dependencias)`.
- `test_resposta_fora_dos_limites_nao_e_liberada_mesmo_se_servico_nao_validar(dependencias)`.
- Classe `EstadoTeste` (`TypedDict`).
  Campos/atributos declarados: `messages: Annotated[list[BaseMessage], add_messages]`.
- `executar_no_toolnode(args, contexto)`.
- `test_toolnode_injeta_runtime_e_preserva_resultado_json_real(dependencias, monkeypatch)`.
- `test_toolnode_nao_aceita_usuario_falso_no_runtime_do_modelo(dependencias)`.
- `test_erro_de_schema_no_toolnode_tem_json_seguro(dependencias)`.
- Constantes, aliases e estado de módulo: `FERRAMENTAS`, `MATRIZ`.

## Preservação da suíte

Os testes anteriores permanecem intactos. O pytest.ini descobre esta pasta e /tests, sem percorrer caches/ambiente virtual. O script de migração e o SDD ausentes na referência inicial agora estão presentes. Novos testes de caracterização e de importações ficam em /tests.

## Dependências internas observadas

Importações existentes nos arquivos desta pasta; não representam uma arquitetura desejada nem autorização para ampliar escopos.

- [app/agents](../agents/RESPONSABILIDADE.md).
- [app/agents/agentsResult](../agents/agentsResult/RESPONSABILIDADE.md).
- [app/agents/prompts](../agents/prompts/RESPONSABILIDADE.md).
- [app/agents/prompts/reutilizaveis](../agents/prompts/reutilizaveis/RESPONSABILIDADE.md).
- [app/api/dependencies](../api/dependencies/RESPONSABILIDADE.md).
- [app/api/routes](../api/routes/RESPONSABILIDADE.md).
- [app/core](../core/RESPONSABILIDADE.md).
- [app/core/clients](../core/clients/RESPONSABILIDADE.md).
- [app/graph](../graph/RESPONSABILIDADE.md).
- [app/guardrails](../guardrails/RESPONSABILIDADE.md).
- [app/memory/persistencia](../memory/persistencia/RESPONSABILIDADE.md).
- [app/memory/vectorSearch](../memory/vectorSearch/RESPONSABILIDADE.md).
- [app/observability](../observability/RESPONSABILIDADE.md).
- [app/schemas](../schemas/RESPONSABILIDADE.md).
- [app/services](../services/RESPONSABILIDADE.md).
- [app/services/ajuda_geral](../services/ajuda_geral/RESPONSABILIDADE.md).
- [app/services/feedback](../services/feedback/RESPONSABILIDADE.md).
- [app/services/gerais](../services/gerais/RESPONSABILIDADE.md).
- [app/services/indicadores](../services/indicadores/RESPONSABILIDADE.md).
- [app/services/indicadores/gerais](../services/indicadores/gerais/RESPONSABILIDADE.md).
- [app/services/ocorrencias](../services/ocorrencias/RESPONSABILIDADE.md).
- [app/services/ordensServico](../services/ordensServico/RESPONSABILIDADE.md).
- [app/services/solicitacoes](../services/solicitacoes/RESPONSABILIDADE.md).
- [app/services/tecnicos](../services/tecnicos/RESPONSABILIDADE.md).
- [app/services/visualizacoes](../services/visualizacoes/RESPONSABILIDADE.md).
- [app/tools/ajuda_geral](../tools/ajuda_geral/RESPONSABILIDADE.md).
- [app/tools/faq](../tools/faq/RESPONSABILIDADE.md).
- [app/tools/feedback](../tools/feedback/RESPONSABILIDADE.md).
- [app/tools/metricas_kpis](../tools/metricas_kpis/RESPONSABILIDADE.md).
- [app/tools/ocorrencias](../tools/ocorrencias/RESPONSABILIDADE.md).
- [app/tools/solicitacoes](../tools/solicitacoes/RESPONSABILIDADE.md).
- [app/tools/toolsRequest](../tools/toolsRequest/RESPONSABILIDADE.md).
- [app/tools/visualizacoes](../tools/visualizacoes/RESPONSABILIDADE.md).
