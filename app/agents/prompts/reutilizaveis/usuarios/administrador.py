from app.agents.prompts.reutilizaveis.usuarios.gestor import GESTOR_INSTRUCAO


ADMINISTRADOR_INSTRUCAO = (
    GESTOR_INSTRUCAO
    + "\nO usuário autenticado tem o perfil administrador. No chat, suas "
      "funcionalidades e limites de acesso são os mesmos do gestor. "
      "Preserve sua identidade de administrador e respeite o escopo autenticado "
      "de instituição, unidade e equipe, as confirmações exigidas e os limites "
      "das ferramentas. A criação de gráficos permanece restrita à plataforma web.\n"
)
