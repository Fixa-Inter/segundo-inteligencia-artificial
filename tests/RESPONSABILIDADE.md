# Responsabilidade: tests

## Objetivo do módulo

Verificar compras, contrato MCP Pechincha, ingestão de FAQ e preservação de contratos da refatoração.

## O que deve ser armazenado aqui

Testes de regras de negócio, isolamento, falhas e contratos; integrações locais simuladas e contrato real opcional de compras.

## Comportamento e limites atuais

Complementa a suíte interna com compras/MCP e testes de refatoração. Inclui contratos anteriores, 132 cenários HTTP de cadastro, importações em processos limpos e recursos comuns. Apenas contrato Pechincha optativo usa serviço real, com RUN_PECHINCHA_LIVE_TESTS=1.

Módulo pai: [.](../RESPONSABILIDADE.md).

## Submódulos

| Pasta | Responsabilidade |
| --- | --- |
| [fixtures](fixtures/RESPONSABILIDADE.md) | Preservar referências capturadas antes da refatoração. |

## Funcionalidades disponíveis e arquivos

### [test_ingestao_faq.py](test_ingestao_faq.py)

Valida o inventário real de documentos, distribuição comum/específica por perfil, descoberta sem arquivos de responsabilidade, rejeição de corpus incompleto, chamada única por perfil, leitura UTF-8 e compatibilidade PDF. Exercita falhas de entrada, embeddings, publicação e limpeza sem rede. O teste com `AsyncQdrantClient(location=":memory:")` usa o mecanismo local de filtros para comprovar limpeza de obsoletos, ausência de duplicatas após atualização e preservação integral dos outros perfis. Embeddings são simulados; nenhum teste deste arquivo acessa OpenAI ou Qdrant remoto.

O catálogo registra os recursos existentes. Funções assíncronas usam `await`; ferramentas LangChain devem receber o contexto injetado. Símbolos com `_` são detalhes internos, cuja assinatura e regras devem ser conferidas antes de reutilizar.

### [test_compras_unit.py](test_compras_unit.py)

Verifica compras unit; os cenários e auxiliares estão listados abaixo.

- `test_purchase_routing_and_only_item_required()`.
- `test_store_category_and_price_are_sent_as_filters(monkeypatch)`.
- `test_product_link_survives_output_redaction()`.
- `test_purchase_judge_receives_compact_evidence(monkeypatch)`.
- `test_purchase_draft_survives_optional_question_before_search(monkeypatch)`.

### [test_pechincha_mcp.py](test_pechincha_mcp.py)

Verifica pechincha mcp; os cenários e auxiliares estão listados abaixo.

- `test_mcp_session_and_structured_search(monkeypatch)`.
- `test_sse_and_tool_error_are_handled(monkeypatch)`.
- `test_empty_deals_are_success_but_bad_shape_is_error()`.
- `test_only_query_is_required_and_price_range_must_be_valid()`.

### [test_pechincha_mcp_contract.py](test_pechincha_mcp_contract.py)

Verifica pechincha mcp contract; os cenários e auxiliares estão listados abaixo.

- `test_public_tools_contract()`.
- Constantes, aliases e estado de módulo: `pytestmark`.

### [test_refatoracao_cadastros.py](test_refatoracao_cadastros.py)

Verifica refatoracao cadastros; os cenários e auxiliares estão listados abaixo.

- `test_cadastro_preserva_resultado_payload_bearer_e_envio_unico(monkeypatch, cenario)`: Verifica respostas completas, transporte e ausência de repetição do POST.
- `test_erro_de_transporte_nao_declara_sucesso_nem_reenvia(monkeypatch, dominio, falha)`: Uma gravação potencialmente enviada permanece indeterminada, sem retry.
- Constantes, aliases e estado de módulo: `CENARIOS`, `DOMINIOS`.

### [test_refatoracao_contratos.py](test_refatoracao_contratos.py)

Verifica refatoracao contratos; os cenários e auxiliares estão listados abaixo.

- `test_openapi_preserva_rotas_campos_descricoes_e_status()`: Detecta alterações no contrato HTTP, inclusive documentação/validação.
- `test_argumentos_das_ferramentas_preservam_contrato_do_modelo(chave)`: Mantém nomes, tipos, limites e obrigatoriedade dos argumentos originais.
- `test_instrucoes_dos_agentes_preservam_texto_original_inclusive_espacos(chave)`: Evita mudar a entrada do LLM ao reorganizar imports e comentar o código.
- `test_caminho_antigo_de_cadastro_reexporta_a_mesma_classe(classe)`: Chamadores legados e serviços novos usam a mesma classe e validação.
- `test_caminho_antigo_de_resultado_reexporta_a_mesma_classe(classe)`: Mantém identidade dos contratos usados por agentes e pelo grafo.
- Constantes, aliases e estado de módulo: `REFERENCIA`.

### [test_refatoracao_importacoes.py](test_refatoracao_importacoes.py)

Verifica refatoracao importacoes; os cenários e auxiliares estão listados abaixo.

- `test_importar_interfaces_nao_inicializa_grafo_modelos_ou_bancos(ordem)`: Importações dos namespaces devem ser leves e não iniciar recursos externos.
- `test_todas_exportacoes_resolvem_em_processo_limpo_sem_ciclos()`: Resolve funções/classes/constantes de todas as fachadas sem abrir conexões.
- `test_anotacoes_contexto_cadastro_resolvem_sem_nomes_ausentes()`: Avalia os tipos da função compartilhada de contexto com `typing.get_type_hints`, detectando imports de tipos ausentes mesmo no Python 3.14, que adia a avaliação. Reproduz a causa do `NameError` observado na inicialização com Python 3.12.
- `test_core_nao_importa_grafo_agentes_servicos_ou_ferramentas()`: Regras comuns não podem voltar a depender da orquestração de aplicação.
- `test_fachada_observa_substituicao_no_modulo_proprietario(monkeypatch)`: Evita congelar referências de modelo/cliente ao centralizar importações.
- Constantes, aliases e estado de módulo: `RAIZ`, `PACOTES`.

### [test_refatoracao_recursos.py](test_refatoracao_recursos.py)

Verifica refatoracao recursos; os cenários e auxiliares estão listados abaixo.

- `test_tres_meses_respeitam_calendario_e_ano_bissexto(hoje, esperado)`.
- `test_data_obrigatoria_nao_aceita_nulo_ou_coercao(valor)`.
- `test_data_opcional_e_datetime_preservam_politica_da_listagem()`.
- `test_celulas_nao_criam_links_colunas_ou_html(texto, esperado)`.
- `test_textos_de_ausencia_dos_dois_dominios_sao_preservados()`.
- `test_falhas_dos_tres_indicadores_preservam_resultado(monkeypatch, dominio, falha, status)`.
- `test_periodo_invalido_nao_chega_ao_warehouse(monkeypatch, dominio, inicio, fim)`.

## Bateria de regressão

`python -m pytest -q -p no:cacheprovider` executa app/tests e /tests. Os novos arquivos com prefixo test_refatoracao verificam contratos, 132 cenários de cadastro, falhas de transporte, identidade dos modelos reexportados, importações sem ciclos e recursos comuns.

As fixtures são capturas anteriores com dados simulados. A suíte não autoriza abrir conexões externas durante importações. O contrato Pechincha real continua optativo por RUN_PECHINCHA_LIVE_TESTS=1.

## Dependências internas observadas

Importações existentes nos arquivos desta pasta; não representam uma arquitetura desejada nem autorização para ampliar escopos.

- [app/agents](../app/agents/RESPONSABILIDADE.md).
- [app/agents/compras](../app/agents/compras/RESPONSABILIDADE.md).
- [app/core](../app/core/RESPONSABILIDADE.md).
- [app/graph](../app/graph/RESPONSABILIDADE.md).
- [app/mcp/pechincha](../app/mcp/pechincha/RESPONSABILIDADE.md).
- [app/schemas/cadastros](../app/schemas/cadastros/RESPONSABILIDADE.md).
- [app/services/indicadores/gerais](../app/services/indicadores/gerais/RESPONSABILIDADE.md).
- [app/tools/ocorrencias](../app/tools/ocorrencias/RESPONSABILIDADE.md).
- [app/tools/ordensServico](../app/tools/ordensServico/RESPONSABILIDADE.md).
