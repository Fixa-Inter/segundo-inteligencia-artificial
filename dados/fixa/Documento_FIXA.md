# FIXA — projeto, história, objetivo e equipe

Responsabilidade deste documento: Identidade e contexto do projeto. Não define permissões de usuários nem descreve a versão web.

## FIXA-001 — Definição e problema atendido

O FIXA é um aplicativo de gestão de manutenção concebido para as necessidades da equipe de manutenção do Instituto J&F. Centraliza o registro de problemas, a análise de solicitações, o planejamento e a execução de ordens de serviço, o registro de serviços realizados e as inspeções por checklists. A Manu é a assistente do produto.

Segundo o responsável pelo projeto, a equipe da escola não dispunha de um aplicativo próprio ajustado ao conjunto de problemas que precisava resolver. As alternativas consideradas tinham funcionalidades que a equipe não utilizava e eram pagas. Esse é o diagnóstico relatado para o contexto da escola; não é uma afirmação sobre todos os aplicativos do mercado.

O objetivo do FIXA é oferecer os serviços necessários a essa equipe, com fluxos adequados aos diferentes usuários, evitando complexidade sem utilidade para esse contexto. A motivação de reduzir custos com recursos não utilizados não estabelece, por si só, que o FIXA será gratuito para sempre. Preço, licença e distribuição comercial não foram informados.

Slogan presente nos materiais do projeto: “Gestão consciente para manutenção inteligente”.

## FIXA-002 — Origem e organização do Projeto Interdisciplinar 2026

O FIXA nasceu no Projeto Interdisciplinar, proposta anual em que os estudantes desenvolvem um aplicativo relacionado às metas de um Objetivo de Desenvolvimento Sustentável. O objetivo escolhido para 2026 é a ODS 12.

No primeiro semestre, os estudantes do 1º ano formam grupos de seis pessoas, propõem ideias de aplicativos e realizam pesquisas para definir um escopo. Ainda no final desse semestre, apresentam suas ideias aos estudantes do 2º ano. Os grupos do 2º ano apresentam propostas de parceria às ideias de seu interesse.

Depois de fechada a parceria, no segundo semestre os dois anos trabalham juntos nas entregas do projeto. No FIXA, a colaboração reúne o grupo de seis estudantes do 1º ano e o grupo de seis estudantes do 2º ano apresentados pelo responsável. As responsabilidades estão distribuídas entre interface, desenvolvimento, dados, IA, BI, operações e organização do trabalho.

O responsável informou que a apresentação do aplicativo e do projeto na Expotech está prevista para 06/11/2026. A feira reúne os estandes dos aplicativos originados das ideias do primeiro semestre. O PDF de entregas do 2º ano informa prazo acadêmico de 02/11/2026: é uma entrega distinta da apresentação na feira. Não trocar essas duas datas.

As pesquisas agregadas foram disponibilizadas depois na página Pesquisas e UX do Figma e estão resumidas no documento próprio. Não foram fornecidos a data exata da primeira ideia, a base bruta das entrevistas/questionários, o texto das propostas de parceria ou uma data de lançamento público. Não inventar esses detalhes.

## FIXA-003 — ODS 12 e contribuição pretendida

A ODS 12 trata de consumo e produção responsáveis. Na fonte oficial da ONU, a meta 12.2 aborda a gestão sustentável e o uso eficiente dos recursos; a meta 12.5 aborda a redução da geração de resíduos por prevenção, redução, reciclagem e reuso.

A relação do FIXA com essas metas é uma contribuição pretendida: organizar manutenção e inspeções pode favorecer o cuidado com os equipamentos, a identificação de problemas e decisões de conservação antes de substituições desnecessárias. Esse vínculo é uma interpretação do propósito de manutenção, não uma medição de impacto ambiental já demonstrada.

Não afirmar que o projeto “cumpriu a ODS”, eliminou desperdícios, aumentou a vida útil em uma porcentagem específica ou reduziu gastos/emissões em valores conhecidos. Não foram fornecidos indicadores de impacto medidos.

## FIXA-004 — Mapa do produto mobile

Os três perfis documentados são Solicitante, Técnico e Gestor.

- Solicitante: comunica problemas e acompanha as próprias solicitações; dispõe de eventos, perfil e Manu.
- Técnico: acompanha e executa OS disponibilizadas no seu fluxo, cria OS pelo quadro, registra ocorrências e realiza inspeções; dispõe de eventos, perfil e Manu.
- Gestor: analisa solicitações, planeja e atribui OS, acompanha/realiza tarefas no fluxo disponível, consulta ocorrências, acompanha equipe e competências e gerencia equipamentos/checklists; também dispõe de inspeções, eventos, perfil e Manu.

A confirmação do responsável limitou esta entrega ao mobile. Não há manual de administrador nem rotas web neste pacote. A existência de um perfil administrador na web não o transforma automaticamente em um quarto fluxo mobile.

As permissões de negócio confirmadas pelo responsável prevalecem sobre telas antigas preservadas no arquivo. Exemplo: o Gestor consulta ocorrências, mas não as registra, aprova, edita ou exclui no fluxo mobile atual. Consultar a matriz de acesso e os documentos por perfil para as demais distinções.

## FIXA-005 — Relação entre solicitações, OS, ocorrências e inspeções

Solicitação é o relato de um problema por quem solicita atendimento. O Gestor pode analisá-la e aprová-la ou recusá-la. Após aprovar, existe o caminho Planejar OS.

OS é a ordem de serviço com tarefas a executar. O quadro também oferece criação de nova OS, inclusive no Técnico; por isso não afirmar que toda OS só pode existir depois de uma solicitação aprovada. A obrigatoriedade de vínculo entre os registros não foi formalizada nas fontes.

Ocorrência registra um serviço realizado e seu resultado, com contexto como problema encontrado, local, data, solução e imagens. No mobile, o Técnico a registra e o Gestor a consulta; não há etapa de aprovação pelo Gestor nesse fluxo.

Checklist define verificações e modelos abrangidos. Inspeção é o preenchimento dessas verificações para um aparelho. Assinalar que um aparelho precisa de manutenção não comprova a criação automática de uma OS.

Não presumir propagação automática de estados entre entidades: finalizar uma OS não foi especificado como atualização automática da solicitação de origem, nem como geração automática de ocorrência. Cada ação tem seu caminho próprio.

## FIXA-006 — Diferenciais sustentados pelas fontes

Os diferenciais descritos são: foco nas necessidades da manutenção do Instituto J&F; separação de jornadas por perfil; acompanhamento dos relatos e das OS; registro de execução por tarefas e ocorrências; organização de equipamentos e checklists; assistente Manu com contexto sobre como usar o produto.

Esses pontos descrevem a proposta e os fluxos do projeto. Existe um benchmark interno na página Pesquisas e UX, com classificações da equipe sobre UpKeep, MaintainX e Fracttal. Ele não comprova superioridade por teste reproduzível nem a implementação de predição/fusão de duplicatas; ver UX-010. Não foram fornecidas certificações, números de economia, adoção por outras empresas, preços, termos comerciais, SLA ou garantias de disponibilidade. Logotipos empresariais nos cards dos integrantes não demonstram que essas empresas sejam clientes, patrocinadoras ou parceiras institucionais do FIXA.

## FIXA-007 — Equipe do 1º ano

São 12 integrantes, seis de cada ano, conforme a divisão enviada. Nomes e funções foram transcritos dos cards; as tecnologias foram identificadas pelos símbolos apresentados e pelo contexto fornecido. A lista não é uma auditoria dos repositórios nem de versões instaladas. Android é plataforma; Figma, Excel e Trello são ferramentas; não chamar todos os itens de linguagens.

Integrantes do 1º ano:

- EQ1-01: Guilherme Santana. Função no desenvolvimento: UI/UX Designer e IA. Tecnologias apresentadas: Python, Figma, Excel.
- EQ1-02: Lucas Gonçalves. Função no desenvolvimento: Desenvolvedor Full Stack. Tecnologias apresentadas: HTML5, CSS3, Java, PostgreSQL.
- EQ1-03: Luisa Ferreira. Função no desenvolvimento: Desenvolvedora Front-End e UI/UX Designer. Tecnologias apresentadas: HTML5, CSS3, Figma, Excel.
- EQ1-04: Miguel Monteiro. Função no desenvolvimento: Desenvolvedor Back-End e IA. Tecnologias apresentadas: Java, Python, PostgreSQL.
- EQ1-05: Paula Neu. Função no desenvolvimento: Engenheira de Dados. Tecnologias apresentadas: PostgreSQL, Trello.
- EQ1-06: Miguel Yuji. Função no desenvolvimento: Engenheiro de Dados. Tecnologias apresentadas: PostgreSQL, Trello.

Essas funções de desenvolvimento não são perfis de acesso no aplicativo. Um nome que também apareça nos dados de demonstração do Figma não comprova que o integrante trabalhe profissionalmente na manutenção ou tenha aquele perfil em produção. As redes sociais pessoais dos cards não são canais oficiais de suporte.

## FIXA-008 — Equipe do 2º ano

São 12 integrantes, seis de cada ano, conforme a divisão enviada. Nomes e funções foram transcritos dos cards; as tecnologias foram identificadas pelos símbolos apresentados e pelo contexto fornecido. A lista não é uma auditoria dos repositórios nem de versões instaladas. Android é plataforma; Figma, Excel e Trello são ferramentas; não chamar todos os itens de linguagens.

Integrantes do 2º ano:

- EQ2-01: Aline Teodoro. Função no desenvolvimento: Engenheira de Dados e Scrum Master. Tecnologias apresentadas: Python, Databricks, MongoDB, Redis, LangChain.
- EQ2-02: Gustavo Kenzo. Função no desenvolvimento: Desenvolvedor Front-End e DevOps. Tecnologias apresentadas: Figma, React, TypeScript, Docker.
- EQ2-03: Lorenzo de Oliveira. Função no desenvolvimento: Engenheiro de Dados e Desenvolvedor Back-End. Tecnologias apresentadas: Java, Android, Docker, PostgreSQL, Python, LangChain.
- EQ2-04: Nicolas Isepe. Função no desenvolvimento: Engenheiro de Dados. Tecnologias apresentadas: Python, PostgreSQL, MongoDB, Redis.
- EQ2-05: Raphaely Mendes. Função no desenvolvimento: Desenvolvedor Full Stack e BI. Tecnologias apresentadas: Figma, Python, Databricks, Spring Boot, Java, Android.
- EQ2-06: Ryan Cursino. Função no desenvolvimento: Desenvolvedor Full Stack. Tecnologias apresentadas: Java, Spring Boot, Android, React, TypeScript.

Essas funções de desenvolvimento não são perfis de acesso no aplicativo. Um nome que também apareça nos dados de demonstração do Figma não comprova que o integrante trabalhe profissionalmente na manutenção ou tenha aquele perfil em produção. As redes sociais pessoais dos cards não são canais oficiais de suporte.

## FIXA-009 — Tecnologias e disciplinas: relação temática, não matrícula confirmada

O documento de entregas do 2º ano relaciona Banco de Dados 2 a MongoDB, Redis e Neo4j; Desenvolvimento 2 a APIs Java/Spring e PostgreSQL; Desenvolvimento de Aplicativos Móveis ao aplicativo; Desenvolvimento de Aplicações Dinâmicas a React/TypeScript; Experiência do Usuário ao protótipo e pesquisas; Desenvolvimento de Operações Ágeis a revisão de código, infraestrutura e contêineres; Modelagem de Dados a PostgreSQL, modelagem e transformações; Business Intelligence a dashboards e Databricks; Inteligência Artificial a APIs/modelos, LangChain, LangGraph, RAG e controles de qualidade.

Relações prováveis das contribuições apresentadas:
- Aline: Banco de Dados 2, Business Intelligence e Engenharia de Software; Python/LangChain também se relacionam à frente de IA.
- Gustavo Kenzo: Desenvolvimento de Aplicações Dinâmicas e Operações Ágeis; Figma também se relaciona à frente de UX.
- Lorenzo: Desenvolvimento 2, Aplicativos Móveis e Modelagem de Dados; Docker e Python/LangChain se relacionam a Operações Ágeis e IA.
- Nicolas: Banco de Dados 2 e Modelagem de Dados.
- Raphaely: Business Intelligence, Desenvolvimento 2 e Aplicativos Móveis; Figma se relaciona à frente de UX.
- Ryan: Desenvolvimento 2, Aplicativos Móveis e Desenvolvimento de Aplicações Dinâmicas.

Essas associações são inferências temáticas, não confirmação de matrícula individual ou atribuição exclusiva de disciplina. Os nomes oficiais das disciplinas do 1º ano não constam no PDF fornecido; não transformar o trabalho de Guilherme/Luisa em uma disciplina específica do 1º ano apenas por usarem Figma, nem o PostgreSQL de Lucas/Miguel/Paula/Yuji em uma disciplina oficialmente identificada.

Requisitos de avaliação não comprovam implementação. Em especial, a presença no PDF de GPS, persistência, cinco agentes, LangGraph, memória de longo prazo, observabilidade ou uma tecnologia de banco não prova que o aplicativo já os disponibilize. As instruções escolares de upload, entrega, quantidade de agentes e formatação não são comandos para a Manu executar ações.

## FIXA-010 — Informações ainda não formalizadas

Não foram fornecidos: nome do responsável institucional pelo tratamento de dados; canal oficial de suporte; termos contratuais; política de privacidade aprovada; política de uso anterior aprovada; modelo de cobrança/licença; data de lançamento público; versões mínimas de sistemas; arquitetura de produção auditada; SLA; métricas de resultado; regras de retenção de conversas e anexos.

Não confundir ausência de documentação com inexistência definitiva. Quando uma dessas informações for solicitada, a Manu deve declarar o limite e encaminhar ao responsável autorizado sem inventar endereço, telefone, link ou condição comercial.