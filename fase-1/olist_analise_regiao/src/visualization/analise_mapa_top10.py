import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.colors import Normalize
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.cm import ScalarMappable
from matplotlib.ticker import FuncFormatter
from matplotlib.patches import Polygon
from matplotlib.collections import PatchCollection
import matplotlib.patheffects as patheffects
from urllib.request import urlopen
import json
from salvar_graficos import salvar_grafico


def formatar_real(valor):
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def formatar_real_abreviado(valor):
    if valor >= 1_000_000:
        return f"R$ {valor / 1_000_000:.1f} mi".replace(".", ",")
    if valor >= 1_000:
        return f"R$ {valor / 1_000:.1f} mil".replace(".", ",")
    return formatar_real(valor)


def formatar_data_br(valor):
    return pd.to_datetime(valor).strftime("%d/%m/%Y")


def carregar_geojson_brasil():
    url = "https://raw.githubusercontent.com/codeforamerica/click_that_hood/master/public/data/brazil-states.geojson"
    with urlopen(url, timeout=30) as resposta:
        return json.load(resposta)


def extrair_poligonos(geometria):
    tipo = geometria["type"]
    coordenadas = geometria["coordinates"]

    if tipo == "Polygon":
        return [coordenadas[0]]

    if tipo == "MultiPolygon":
        poligonos = []
        for grupo in coordenadas:
            poligonos.append(grupo[0])
        return poligonos

    return []


def calcular_centro_rotulo(poligonos):
    maior_poligono = max(poligonos, key=len)
    pontos_x = [ponto[0] for ponto in maior_poligono]
    pontos_y = [ponto[1] for ponto in maior_poligono]
    return sum(pontos_x) / len(pontos_x), sum(pontos_y) / len(pontos_y)


ajustes_rotulos = {
    "PA": (0.0, -1.6),
    "SP": (0.7, -0.2),
}


# Base consolidada ja tratada na etapa anterior do projeto.
dados = pd.read_excel("../../data/processed/dados.xlsx")

# Receita agregada por UF, usada tanto no mapa quanto na tabela.
receita_por_uf = (
    dados.groupby("customer_state", as_index=False)["price"]
    .sum()
    .rename(columns={"customer_state": "UF", "price": "receita_uf"})
    .sort_values("receita_uf", ascending=False)
)

# Contagem de pedidos unicos para calcular ticket medio.
pedidos_por_uf = (
    dados.groupby("customer_state", as_index=False)["order_id"]
    .nunique()
    .rename(columns={"customer_state": "UF", "order_id": "pedidos"})
)

# Junta as metricas principais que vao aparecer na visualizacao.
receita_por_uf = receita_por_uf.merge(pedidos_por_uf, on="UF", how="left")
receita_por_uf["ticket_medio"] = receita_por_uf["receita_uf"] / receita_por_uf["pedidos"]
receita_total = receita_por_uf["receita_uf"].sum()
receita_por_uf["participacao_receita"] = receita_por_uf["receita_uf"] / receita_total
periodo_inicial = pd.to_datetime(dados["order_purchase_timestamp"]).min()
periodo_final = pd.to_datetime(dados["order_purchase_timestamp"]).max()

# GeoJSON dos estados para desenhar o mapa geografico no matplotlib.
geojson_brasil = carregar_geojson_brasil()
receita_dict = dict(zip(receita_por_uf["UF"], receita_por_uf["receita_uf"]))

# Ranking lateral com as 10 maiores receitas.
top_10 = receita_por_uf.nlargest(10, "receita_uf").copy()
top_10["Receita"] = top_10["receita_uf"].apply(formatar_real_abreviado)
top_10["Ticket Medio"] = top_10["ticket_medio"].apply(formatar_real)
top_10["Participacao"] = top_10["participacao_receita"].map(lambda valor: f"{valor:.1%}".replace(".", ","))

fig, (ax_mapa, ax_tabela) = plt.subplots(
    1,
    2,
    figsize=(20, 10),
    gridspec_kw={"width_ratios": [2.15, 1.25]},
)
fig.patch.set_facecolor("#f4f1ea")

norm = Normalize(vmin=receita_por_uf["receita_uf"].min(), vmax=receita_por_uf["receita_uf"].max())
cmap = LinearSegmentedColormap.from_list(
    "receita_brasil",
    ["#dbe7c9", "#8fc0a9", "#3d8d7a", "#1d4e5f", "#153243"],
)

# Cada poligono representa um estado e recebe cor conforme a receita.
patches = []
cores = []
rotulos_ufs = []

for feature in geojson_brasil["features"]:
    uf = feature["properties"]["sigla"]
    receita = receita_dict.get(uf)
    cor = cmap(norm(receita)) if receita is not None else "#e2e8f0"
    poligonos_estado = extrair_poligonos(feature["geometry"])

    if poligonos_estado:
        rotulos_ufs.append((uf, *calcular_centro_rotulo(poligonos_estado)))

    for poligono in poligonos_estado:
        patches.append(Polygon(poligono, closed=True))
        cores.append(cor)

colecao = PatchCollection(
    patches,
    facecolor=cores,
    edgecolor="#f8fafc",
    linewidth=1.3,
)
ax_mapa.add_collection(colecao)

for uf, pos_x, pos_y in rotulos_ufs:
    ajuste_x, ajuste_y = ajustes_rotulos.get(uf, (0.0, 0.0))
    ax_mapa.text(
        pos_x + ajuste_x,
        pos_y + ajuste_y,
        uf,
        ha="center",
        va="center",
        fontsize=8.5,
        fontweight="bold",
        color="#16313a",
        path_effects=[patheffects.withStroke(linewidth=2.5, foreground="#fffdf8")],
    )

ax_mapa.set_title("Receita por UF", fontsize=24, fontweight="bold", color="#16313a", loc="left", pad=15)
ax_mapa.text(
    0.0,
    0.988,
    "Mapa coroplético do Brasil com intensidade por receita total e ranking lateral das maiores UFs.",
    transform=ax_mapa.transAxes,
    fontsize=11,
    color="#4b5563",
)
ax_mapa.autoscale_view()
ax_mapa.set_aspect("equal")
ax_mapa.set_xticks([])
ax_mapa.set_yticks([])
ax_mapa.set_facecolor("#efe7db")
for spine in ax_mapa.spines.values():
    spine.set_visible(False)

barra_cores = fig.colorbar(ScalarMappable(norm=norm, cmap=cmap), ax=ax_mapa, fraction=0.035, pad=0.02)
barra_cores.outline.set_visible(False)
barra_cores.ax.yaxis.set_major_formatter(FuncFormatter(lambda x, _: formatar_real_abreviado(x)))
barra_cores.set_label("Receita Total", fontsize=11, fontweight="bold", color="#16313a")
barra_cores.ax.tick_params(colors="#374151", labelsize=10)

ax_tabela.axis("off")
ax_tabela.set_facecolor("#fbf9f4")
ax_tabela.text(
    0.0,
    0.98,
    "Top 10 UFs",
    transform=ax_tabela.transAxes,
    fontsize=20,
    fontweight="bold",
    color="#16313a",
    va="top",
)
ax_tabela.text(
    0.0,
    0.93,
    f"Receita total analisada: {formatar_real_abreviado(receita_total)}",
    transform=ax_tabela.transAxes,
    fontsize=10.5,
    color="#6b7280",
    va="top",
)
ax_tabela.text(
    0.0,
    0.89,
    f"Período analisado: {formatar_data_br(periodo_inicial)} a {formatar_data_br(periodo_final)}",
    transform=ax_tabela.transAxes,
    fontsize=10.5,
    color="#6b7280",
    va="top",
)

tabela = ax_tabela.table(
    cellText=top_10[["UF", "Receita", "Ticket Medio", "Participacao"]].values,
    colLabels=["UF", "Receita", "Ticket Médio", "% Receita"],
    bbox=[0.0, 0.08, 1.0, 0.74],
    cellLoc="center",
    colLoc="center",
)

tabela.auto_set_font_size(False)
tabela.set_fontsize(10.5)
tabela.scale(1.0, 1.55)

# Ajuste fino do alinhamento para deixar os numeros mais faceis de comparar.
for (linha, coluna), celula in tabela.get_celld().items():
    celula.set_edgecolor("#e5e7eb")
    celula.set_linewidth(0.6)
    if linha == 0:
        celula.set_facecolor("#e8ece7")
        celula.set_text_props(color="#16313a", weight="bold", ha="center")
    else:
        celula.set_facecolor("#ffffff" if linha % 2 else "#f6f3ee")
        if coluna == 0:
            celula.set_text_props(weight="bold", color="#16313a", ha="center")
            celula._loc = "center"
        else:
            celula.set_text_props(color="#374151", ha="right")
            celula._loc = "right"

plt.tight_layout()
salvar_grafico(fig, "mapa_receita_top10.png")
