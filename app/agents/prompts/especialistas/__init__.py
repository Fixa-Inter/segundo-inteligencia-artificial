# from .juiz import JUIZ_PROMPT
# from .feedback import FEEDBACK_PROMPT
# from .faq import FAQ_PROMPT

# __all__ = [
#     "JUIZ_PROMPT"
#     ,"FEEDBACK_PROMPT"
#     ,"FAQ_PROMPT"
# ]

from .analytics import ANALYTICS_PROMPT
from .faq import FAQ_PROMPT
from .feedback import FEEDBACK_PROMPT
from .juiz import JUIZ_PROMPT
from .solicitacoes import SOLICITACOES_PROMPT
from .visualizacoes import VISUALIZACOES_PROMPT


__all__ = [
    "ANALYTICS_PROMPT",
    "FAQ_PROMPT",
    "FEEDBACK_PROMPT",
    "JUIZ_PROMPT",
    "SOLICITACOES_PROMPT",
    "VISUALIZACOES_PROMPT",
]