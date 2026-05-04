# olist_analise_top_produtos_sellers

bases: sellers, products, orders, orders_items, customers, geolocation, payments, reviews
bases principais: sellers, products, orders, orders_items
período: 2016, 2017, 2018
bibliotecas: pandas, matplotlib, seaborn


Tanto para analisar 'Top Produtos' quanto para 'Top Sellers', seguiu-se o seguinte' passos:

1: Importação das bases
2: Mescla das bases pelas suas colunas referências em comum, como 'order_id' e 'costumer_id', formando uma variável mesclada que considere diversas partes das bases que foram mescladas.
3: Conversão da coluna 'order_purchase_timestamp' para o tipo datetime.
4: Usar um laço para agrupar os dados por ano e product_category_name para contar as vendas.
5: Selecionar os 5 produtos mais vendidos (ou os 10 melhores vendedores, no caso de Sellers) para cada ano através dos códigos descritos no notebook.
