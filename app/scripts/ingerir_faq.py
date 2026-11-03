"""Ingere referências comuns e manuais por perfil: python -m app.scripts.ingerir_faq."""

import asyncio
from pathlib import Path

from app.core import DIRETORIO_BASE
from app.memory.embedding import ingerir_faq

# Diretório das fontes de produto; independe da pasta de execução do comando.
DIRETORIO_DOCUMENTOS_FAQ = DIRETORIO_BASE / "dados"
# Administrador consulta o conteúdo de gestor em buscar_faq; não possui índice separado.
PERFIS_FAQ = ("solicitante", "tecnico", "gestor")


def descobrir_documentos_faq(
    diretorio_dados: str | Path = DIRETORIO_DOCUMENTOS_FAQ,
) -> dict[str, tuple[Path, ...]]:
    """Monta o corpus completo de cada perfil para main, excluindo documentação de arquitetura."""
    raiz = Path(diretorio_dados)

    def listar_fontes(pasta: Path) -> tuple[Path, ...]:
        """Seleciona somente Markdown de produto dentro da pasta informada."""
        return tuple(sorted(
            caminho for caminho in pasta.rglob("*")
            if caminho.is_file()
            and caminho.suffix.lower() == ".md"
            and caminho.name.casefold() != "responsabilidade.md"
        ))

    # Validação: confere todas as pastas antes de atualizar o primeiro perfil.
    comuns = listar_fontes(raiz / "fixa")
    if not comuns:
        raise ValueError(f"Nenhum documento comum de FAQ encontrado em {raiz / 'fixa'}.")

    documentos = {}
    for perfil in PERFIS_FAQ:
        especificos = listar_fontes(raiz / "mobile" / perfil)
        if not especificos:
            raise ValueError(f"Nenhum manual de FAQ encontrado para o perfil {perfil}.")
        documentos[perfil] = comuns + especificos
    return documentos


async def main():
    """Substitui cada perfil uma vez com dados/fixa e seu próprio manual de dados/mobile."""
    documentos_por_perfil = descobrir_documentos_faq()
    for perfil, caminhos in documentos_por_perfil.items():
        await ingerir_faq(caminhos, perfil)

if __name__ == "__main__":
    asyncio.run(main())
