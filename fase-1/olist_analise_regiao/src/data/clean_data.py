import pandas as pd
import janitor
from pathlib import Path

order_items = pd.read_csv("../../data/external/olist_order_items_dataset.csv")
customers = pd.read_csv("../../data/external/olist_customers_dataset.csv")
orders = pd.read_csv("../../data/external/olist_orders_dataset.csv")

# Calcular a receita por pedido
receita_por_pedido = (
    order_items
    .groupby("order_id")["price"]
    .sum()
    .reset_index()
)

# Mesclarar pedidos com clientes para obter informações adicionais
pedidos_clientes = orders.merge(customers, on="customer_id", how="left")

# Mesclarar  receitas com pedidos para obter a receita total por pedido
dados = pedidos_clientes.merge(receita_por_pedido, on="order_id", how="left")


# Limpar os dados usando janitor
def limpar_dados(df):
    df = df.clean_names()
    df = df.remove_empty()
    # df = df.remove_constant()
    df = df.drop_duplicates()
    return df  

pedidos_clientes = limpar_dados(pedidos_clientes)
dados = limpar_dados(dados)

# Converter colunas de data para o formato datetime, se necessário"
termos_desejados = ["_date", "_timestamp", "_at"]

# Definindo tipo da coluna price em real
dados["price"] = pd.to_numeric(dados["price"], errors="coerce")
dados["price"] = dados["price"].fillna(0)  # Substituir NaN por 0




for coluna in pedidos_clientes.columns:
    if any(termo in coluna for termo in termos_desejados):
       pedidos_clientes[coluna] = pd.to_datetime(pedidos_clientes[coluna], errors="coerce").dt.date

for coluna in dados.columns:
    if any(termo in coluna for termo in termos_desejados):
       dados[coluna] = pd.to_datetime(dados[coluna], errors="coerce").dt.date

# Substituir valores que contenham "_" por " "
for coluna in dados.columns:
    if dados[coluna].dtype == "str":
        dados[coluna] = dados[coluna].str.replace("_", " ", regex=True)

for coluna in pedidos_clientes.columns:
    if pedidos_clientes[coluna].dtype == "str":
        pedidos_clientes[coluna] = pedidos_clientes[coluna].str.replace("_", " ", regex=True)


# Salvar o DataFrame limpo em um novo arquivo CSV
saida_completos = Path("../../data/processed/dados.xlsx")
saida_clientes = Path("../../data/processed/pedidos_clientes.xlsx")
saida_completos.parent.mkdir(parents=True, exist_ok=True)
saida_clientes.parent.mkdir(parents=True, exist_ok=True)
dados.to_excel(saida_completos, index=False)
pedidos_clientes.to_excel(saida_clientes, index=False)

