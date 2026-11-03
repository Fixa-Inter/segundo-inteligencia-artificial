from app.agents.prompts.reutilizaveis.usuarios import GESTOR_INSTRUCAO

# ADMINISTRADOR_INSTRUCAO: Instrução textual enviada ao modelo; conteúdo preservado para manter comportamento do agente.
ADMINISTRADOR_INSTRUCAO = (
    GESTOR_INSTRUCAO
    + "\nO usuário autenticado tem o perfil administrador. No chat, suas "
      "funcionalidades e limites de acesso são os mesmos do gestor. "
      "Preserve sua identidade de administrador e respeite o escopo autenticado "
      "de instituição, unidade e equipe, as confirmações exigidas e os limites "
      "das ferramentas. A criação de gráficos permanece restrita à plataforma web.\n"
)
