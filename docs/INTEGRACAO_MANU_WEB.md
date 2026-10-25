# Integração da Manu com a web

Atividade [#46](https://github.com/Fixa-Inter/segundo-inteligencia-artificial/issues/46), em apoio à [web #11](https://github.com/Fixa-Inter/segundo-aplicacao-website/issues/11). Branch `feature/integracao-web-manu`, criada de `origin/dev`. Não houve promoção das branches permanentes.

## Contrato autenticado

| Método | Rota | Uso |
| --- | --- | --- |
| POST | `/api/v1/chat` | Envia `{mensagem, thread_id, imagens}`; `thread_id: null` inicia uma conversa |
| GET | `/api/v1/chat/sessions?limite=50` | Até 50 conversas recentes do usuário autenticado |
| GET | `/api/v1/chat/sessions/{thread_id}` | Mensagens, título, data, encerramento e confirmação pendente |
| DELETE | `/api/v1/chat/sessions/{thread_id}` | Encerra e gera resumo; o histórico permanece consultável |

Bearer é validado na API FIXA. A identidade e o CNPJ nunca vêm do corpo da mensagem ou de parâmetros do navegador. O perfil atual da API Web traz `tipoAcesso` como objeto e não traz `cnpjUnidade`: a adaptação normaliza o enum e consulta a unidade ativa do ID validado no PostgreSQL. O contrato anterior com enum string e CNPJ continua aceito.

Os perfis permitidos continuam sendo solicitante, técnico e gestor. Administrador não é convertido em gestor. A leitura do MongoDB filtra `user_id`; não expõe tokens, rascunhos ou documentos internos. Conversas encerradas rejeitam novas mensagens com 409 quando o chat está configurado. Encerramentos repetidos não geram outro resumo.

A confirmação da última resposta é persistida para restaurar os botões após recarregar a web. `confirmacao: "sim"` apenas apresenta a proposta; a execução depende de uma nova manifestação explícita do usuário, processada pelo fluxo já existente.

## Configuração local

A web oferece `npm run ia:prepare`, `npm run ia:up`, `npm run ia:logs` e `npm run ia:down`, com Docker Compose. O serviço usa porta 8000 no loopback; MongoDB e Qdrant ficam na rede interna, com volumes persistentes. Não é preciso modificar o código da API Java.

Variáveis do serviço:

- `FIXA_API_BASE_URL`: API Java, sem `/api/v1` no final.
- `FIXA_WEB_ORIGINS`: origens permitidas por CORS, separadas por vírgula. Padrão local: `http://localhost:5173,http://127.0.0.1:5173`.
- `MONGO_URI`, `QDRANT_URL`, `QDRANT_API_KEY` e `DATABASE_URL_GESTOR`, `DATABASE_URL_TECNICO`, `DATABASE_URL_SOLICITANTE`.
- `QDRANT_TIMEOUT_SECONDS`: prazo das operações do cliente; 30 segundos por padrão, 60 no Compose local para a criação dos índices.
- `OPENAI_API_KEY`, `TYPESAFE_API_KEY` e `GEMINI_API_KEY`: somente no servidor. O Compose da web lê `dev.local/ia.env`, ignorado pelo Git.

O modelo `gpt-6-luna` e a Responses API foram preservados conforme o repositório. A configuração corresponde à [documentação oficial da OpenAI](https://developers.openai.com/api/docs/models/gpt-6-luna). Acesso efetivo e respostas ainda precisam ser confirmados com credenciais válidas.

Saúde e histórico não inicializam os modelos. Sem as três chaves, POST de chat retorna 503 antes de criar uma sessão; não há chave fictícia nem resposta guiada em produção. A proteção de entrada continua no fluxo: apenas sua inicialização passou a ocorrer quando usada.

Na primeira execução, collections ausentes do Qdrant são criadas vazias, com os índices usados pelo projeto. Isso não carrega FAQ, não gera embeddings nem sincroniza cadastros operacionais. A ingestão precisa de fontes reais e credenciais; nenhum PDF de FAQ veio no clone consultado. Os processos de ingestão/sincronização existentes continuam separados.

## Verificações de 25/10/2026

- Dockerfile compilado com dependências originais e inicialização local com MongoDB/Qdrant reais.
- 219 testes aprovados e 1 `xfail` já declarado no repositório. Execução em contêiner `--network none`, com valor de teste somente para construir o cliente em testes antigos; nenhum provedor externo foi chamado.
- Seis falhas iniciais da suíte eram mocks ausentes da consulta de anexos nos testes do executor/propostas. Os testes passaram a isolar essa dependência do MongoDB, sem alterar suas asserções de negócio.
- API Java real autentica gestor; consulta do histórico na IA retorna 200, sem Bearer retorna 401 e conversa de outro usuário retorna 404. Histórico sintético de QA foi inserido no MongoDB e removido ao final.
- POST sem chaves retorna 503. A inferência OpenAI/JEV/Gemini não foi executada: credenciais ainda não foram fornecidas.

O teste da suíte não equivale a homologação ou validação de todas as ferramentas com modelos reais. O caso `xfail` e as divergências históricas em `docs/validacao_fluxo.md` continuam registrados.
