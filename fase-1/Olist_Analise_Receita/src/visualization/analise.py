import seaborn as sns
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
from matplotlib.colors import LinearSegmentedColormap
from salvar_graficos import salvar_grafico

# Configurações de estilo para os gráficos
sns.set_theme(style="whitegrid")

# Configurando dataframes
dados = pd.read_excel("../../data/processed/dados.xlsx")
pedidos_clientes = pd.read_excel("../../data/processed/pedidos_clientes.xlsx")

# Função para formatar valores em reais
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

# Calculando receita por UF
receita_por_uf = (
    dados
    .groupby("customer_state")["price"]
    .sum()
    .reset_index()
    .rename(columns={"price": "receita_uf"})
    .sort_values(by="receita_uf", ascending=False)
)

# receita total por UF
receita_uf = dados.groupby("customer_state")["price"].sum()

# número de pedidos por UF
pedidos_uf = dados.groupby("customer_state")["order_id"].nunique()

# ticket médio por UF
ticket_medio_uf = (receita_uf / pedidos_uf).reset_index()
ticket_medio_uf.columns = ["UF", "ticket_medio"]

receita_total = receita_por_uf["receita_uf"].sum()
media_receita = receita_por_uf["receita_uf"].mean()
periodo_inicial = pd.to_datetime(dados["order_purchase_timestamp"]).min()
periodo_final = pd.to_datetime(dados["order_purchase_timestamp"]).max()

cmap = LinearSegmentedColormap.from_list(
    "receita_barras",
    ["#dbe7c9", "#8fc0a9", "#3d8d7a", "#1d4e5f", "#153243"],
)
cores_barras = [cmap(valor) for valor in pd.Series(range(len(receita_por_uf))) / max(len(receita_por_uf) - 1, 1)]

# print(receita_por_uf.head(10))

fig, ax = plt.subplots(figsize=(17, 9))
fig.patch.set_facecolor("#f4f1ea")
ax.set_facecolor("#fbf9f4")

sns.barplot(
    x="customer_state",
    y="receita_uf",
    hue="customer_state",
    data=receita_por_uf,
    palette=cores_barras,
    dodge=False,
    legend=False,
    ax=ax,
)

ax.set_title("Receita por UF", fontsize=24, fontweight="bold", color="#16313a", loc="left", pad=35)
ax.text(
    0.0,
    1.03,
    "Comparativo da receita total por estado, com destaque para distribuição, média e período analisado.",
    transform=ax.transAxes,
    fontsize=11,
    color="#4b5563",
)
ax.text(
    1.0,
    1.04,
    f"Período: {formatar_data_br(periodo_inicial)} a {formatar_data_br(periodo_final)}\nReceita total: {formatar_real_abreviado(receita_total)}",
    transform=ax.transAxes,
    ha="right",
    va="top",
    fontsize=10.5,
    color="#6b7280",
)

ax.axhline(
    media_receita,
    color="#b45309",
    linewidth=1.5,
    linestyle="--",
    alpha=0.9,
)
ax.text(
    len(receita_por_uf) - 0.4,
    media_receita * 1.01,
    f"Média: {formatar_real_abreviado(media_receita)}",
    ha="right",
    va="bottom",
    fontsize=10,
    color="#92400e",
    fontweight="bold",
)

ax.set_xlabel("UF", fontsize=12, fontweight="bold", color="#374151", labelpad=12)
ax.set_ylabel("Receita Total", fontsize=12, fontweight="bold", color="#374151", labelpad=12)
ax.yaxis.set_major_formatter(FuncFormatter(lambda x, _: formatar_real_abreviado(x)))
ax.tick_params(axis="x", rotation=0, labelsize=10, colors="#374151")
ax.tick_params(axis="y", labelsize=10, colors="#374151")
ax.grid(axis="y", color="#d6d3d1", linestyle="--", linewidth=0.8, alpha=0.7)
ax.grid(axis="x", visible=False)

for lado in ["top", "right"]:
    ax.spines[lado].set_visible(False)
ax.spines["left"].set_color("#d6d3d1")
ax.spines["bottom"].set_color("#d6d3d1")

for barra in ax.patches:
    altura = barra.get_height()
    ax.annotate(
        formatar_real_abreviado(altura),
        (barra.get_x() + barra.get_width() / 2, altura),
        ha="center",
        va="bottom",
        fontsize=9,
        fontweight="bold",
        color="#16313a",
        rotation=45,
        xytext=(0, 6),
        textcoords="offset points"
    )

ax.set_ylim(0, receita_por_uf["receita_uf"].max() * 1.18)
plt.tight_layout()
salvar_grafico(fig, "receita_por_uf.png")






