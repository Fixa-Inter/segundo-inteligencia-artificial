"""Compatibilidade de importação; contratos canônicos estão em app/schemas/cadastros."""

from app.schemas.cadastros import CriarEventoEntrada

# Mantém os nomes históricos sem duplicar classes ou validadores.
__all__ = ['CriarEventoEntrada']
