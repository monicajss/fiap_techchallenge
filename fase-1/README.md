# Tech Challenge - Fase 1

## Case E-commerce Olist  
Este desafio propõe a construção de um relatório executivo voltado a 
investidores e acionistas do setor de e-commerce, baseado no Brazilian E-Commerce  Public Dataset by Olist. O objetivo é transformar dados transacionais em uma narrativa  clara sobre desempenho comercial, eficiência logística e/ou satisfação do cliente, culminando em recomendações acionáveis e, quando possível, previsões 
fundamentadas. 

## Sobre o Dataset 
O dataset reúne aproximadamente 100 mil pedidos entre 2016 e 2018, cobrindo 
múltiplos marketplaces no Brasil. Inclui tabelas interconectadas de clientes, pedidos,  itens, produtos, vendedores, pagamentos, avaliações e geolocalização por CEP. Os  dados são reais e foram anonimizados. Há possibilidade de análises 
multidimensionais, como status do pedido, preço, meios de pagamento, desempenho 
de frete, localização, atributos de produto e reviews.  
O dataset pode ser acessado aqui. 

## Estrutura dos Dados e Dicionário (visão executiva) 
- customers: customer_id, customer_unique_id, zip_code_prefix, cidade, 
estado. 
- orders: order_id, customer_id, compra/aprovação/entrega, status, timestamps de compra/aprovação/entrega. 
- order_items: order_id, item_id, product_id, seller_id, shipping_limit_date, 
price, freight_value. 
- payments: order_id, payment_type, installments, payment_value. 
- order_reviews: order_id, review_score, timestamps, review_comment_title/text. 
- products: product_id, category_name, pesos/medidas, descrição. 
- sellers: seller_id, zip_code_prefix, cidade, estado. 
- geolocation: zip_code_prefix, latitude, longitude, cidade, estado. 
- category_translation: tradução de nomes de categorias para inglês.