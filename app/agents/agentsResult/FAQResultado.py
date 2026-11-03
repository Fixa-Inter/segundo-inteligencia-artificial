"""Compatibilidade de importação; contratos canônicos estão em app/schemas/resultados_agentes."""

from app.schemas.resultados_agentes import FAQResultado

# Mantém os nomes históricos sem duplicar classes ou validadores.
__all__ = ['FAQResultado']
