from pathlib import Path


# Salvar os gráficos em um diretório específico.
def salvar_grafico(figura, nome_arquivo):
    diretorio = Path(__file__).resolve().parent / "images"
    diretorio.mkdir(parents=True, exist_ok=True)
    caminho_completo = diretorio / nome_arquivo
    figura.savefig(caminho_completo, bbox_inches="tight", dpi=300)
    return caminho_completo