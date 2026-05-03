from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt

from salvar_graficos import salvar_grafico


def calcular_variacao_percentual(valor_2017, valor_2018):
    if valor_2017 == 0:
        return None
    return ((valor_2018 - valor_2017) / valor_2017) * 100


def formatar_real_abreviado(valor):
    if valor >= 1_000_000:
        return f"R$ {valor / 1_000_000:.1f} mi".replace(".", ",")
    if valor >= 1_000:
        return f"R$ {valor / 1_000:.1f} mil".replace(".", ",")
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def formatar_variacao(valor):
    if pd.isna(valor):
        return "Sem base"
    icone = "▲" if valor > 0 else "▼" if valor < 0 else "■"
    return f"{icone} {valor:+.1f}%".replace(".", ",")


base_dir = Path(__file__).resolve().parents[2]
arquivo_dados = base_dir / "data" / "processed" / "dados.xlsx"

# Leitura da base consolidada usada nas outras analises.
dados = pd.read_excel(arquivo_dados)
dados["order_purchase_timestamp"] = pd.to_datetime(dados["order_purchase_timestamp"], errors="coerce")

# Filtra apenas os anos que entram na comparacao.
dados_comparacao = dados[dados["order_purchase_timestamp"].dt.year.isin([2017, 2018])].copy()
dados_comparacao["ano"] = dados_comparacao["order_purchase_timestamp"].dt.year

# Soma a receita por UF em cada ano.
tabela_comparativa = (
    dados_comparacao
    .groupby(["customer_state", "ano"], as_index=False)["price"]
    .sum()
    .pivot(index="customer_state", columns="ano", values="price")
    .reset_index()
    .rename(columns={
        "customer_state": "UF",
        2017: "receita_2017",
        2018: "receita_2018",
    })
)

tabela_comparativa["receita_2017"] = tabela_comparativa["receita_2017"].fillna(0)
tabela_comparativa["receita_2018"] = tabela_comparativa["receita_2018"].fillna(0)
tabela_comparativa["variacao_percentual"] = tabela_comparativa.apply(
    lambda linha: calcular_variacao_percentual(linha["receita_2017"], linha["receita_2018"]),
    axis=1,
)

tabela_comparativa["situacao"] = tabela_comparativa["variacao_percentual"].apply(
    lambda valor: "Sem base em 2017"
    if pd.isna(valor)
    else "Aumento" if valor > 0 else "Queda" if valor < 0 else "Estavel"
)

top_5_aumentos = tabela_comparativa[tabela_comparativa["variacao_percentual"] > 0].nlargest(5, "variacao_percentual")
top_5_quedas = tabela_comparativa[tabela_comparativa["variacao_percentual"] < 0].nsmallest(5, "variacao_percentual")

tabela_comparativa = pd.concat([top_5_aumentos, top_5_quedas], ignore_index=True)
tabela_comparativa = tabela_comparativa.sort_values("variacao_percentual", ascending=False, na_position="last")

tabela_visual = tabela_comparativa.copy()
tabela_visual["Receita 2017"] = tabela_visual["receita_2017"].apply(formatar_real_abreviado)
tabela_visual["Receita 2018"] = tabela_visual["receita_2018"].apply(formatar_real_abreviado)
tabela_visual["Variação"] = tabela_visual["variacao_percentual"].apply(formatar_variacao)
tabela_visual = tabela_visual[["UF", "Receita 2017", "Receita 2018", "Variação"]]

fig, ax = plt.subplots(figsize=(13, 8.5))
fig.patch.set_facecolor("#f4f1ea")
ax.set_facecolor("#fbf9f4")
ax.axis("off")

ax.text(
    0.0,
    1.03,
    "Comparativo de Receita por UF: 2017 x 2018",
    transform=ax.transAxes,
    fontsize=22,
    fontweight="bold",
    color="#16313a",
    va="top",
)
ax.text(
    0.0,
    0.985,
    "Top 5 aumentos e top 5 quedas por UF, ordenados da maior para a menor variação percentual.",
    transform=ax.transAxes,
    fontsize=10.5,
    color="#4b5563",
    va="top",
)

tabela = ax.table(
    cellText=tabela_visual.values,
    colLabels=tabela_visual.columns,
    bbox=[0.0, 0.02, 1.0, 0.9],
    cellLoc="center",
    colLoc="center",
)

tabela.auto_set_font_size(False)
tabela.set_fontsize(10)
tabela.scale(1.0, 1.4)

for (linha, coluna), celula in tabela.get_celld().items():
    celula.set_edgecolor("#e5e7eb")
    celula.set_linewidth(0.6)

    if linha == 0:
        celula.set_facecolor("#e8ece7")
        celula.set_text_props(color="#16313a", weight="bold", ha="center")
        continue

    variacao_valor = tabela_comparativa.iloc[linha - 1]["variacao_percentual"]
    if pd.isna(variacao_valor):
        cor_linha = "#f3f4f6"
    elif variacao_valor > 0:
        cor_linha = "#ecfdf5"
    elif variacao_valor < 0:
        cor_linha = "#fef2f2"
    else:
        cor_linha = "#fffbeb"

    celula.set_facecolor(cor_linha)

    if coluna == 0:
        celula.set_text_props(color="#16313a", weight="bold", ha="center")
        celula._loc = "center"
    elif coluna in [1, 2, 3]:
        cor_texto = "#166534" if coluna == 3 and not pd.isna(variacao_valor) and variacao_valor > 0 else "#991b1b" if coluna == 3 and not pd.isna(variacao_valor) and variacao_valor < 0 else "#374151"
        celula.set_text_props(color=cor_texto, ha="right")
        celula._loc = "right"

salvar_grafico(fig, "comparativo_receita_2017_2018.png")
plt.tight_layout()
plt.show()