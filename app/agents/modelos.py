"""Compatibilidade: clientes de modelos pertencem à infraestrutura core/clients."""

from app.core.clients import llm_luna, llm_rapido, llm_especialista, obter_modelo_embedding

# Preserva os símbolos antigos e a identidade dos clientes já configurados.
__all__ = ["llm_luna", "llm_rapido", "llm_especialista", "obter_modelo_embedding"]
