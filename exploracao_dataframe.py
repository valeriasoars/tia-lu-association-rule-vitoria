import pandas as pd
from collections import Counter


df = pd.read_csv("vendas_dataset.csv")

print("\nHEAD")
print(df.head())

print("\nINFO DO DATAFRAME")
df.info()

#Verificação de Valores Ausentes (NaN)
print("\nVerificação de Valores Ausentes")
# Contagem de valores nulos por coluna
nulos_por_coluna = df.isnull().sum()
print("\nQtd de valores nulos")
print(nulos_por_coluna)

"""Apenas um um valor de descricao_produtos está ausente, melhor usar um drop."""

#Verificação de Registros Duplicados 
print("\nVerificação Duplicatas")

# Verificação de linhas completamente duplicadas
duplicadas_completas = df.duplicated().sum()
print(f"Número de linhas completamente duplicadas: {duplicadas_completas}")

# Verificação de IDs de Transação duplicados
duplicadas_id = df['id_transacao'].duplicated().sum()
print(f"Número de 'id_transacao' duplicados: {duplicadas_id}")

# Verificação de Descrição duplicadas
duplicadas_id = df['descricao_produtos'].duplicated().sum()
print(f"Número de 'descricao_produtos' duplicados: {duplicadas_id}")

"""Apesar de ter 1406 descricao produtos duplicados, os IDs de transação são deferentes. Acredito que sejam apenas compras frequentes."""

#Justificativa da Categorização - Frequência de Produtos Brutos 
print("\nJustificativa da Categorização")

dados_limpos = df.dropna(subset=['descricao_produtos']).copy()
#Contagem de Produtos Brutos
lista_produtos_brutos = []
for produtos in dados_limpos['descricao_produtos']:
    produtos_individuais = [produto.strip() for produto in produtos.split(';') if produto.strip()]
    lista_produtos_brutos.extend(produtos_individuais)

contador_produtos = Counter(lista_produtos_brutos)
total_produtos_distintos = len(contador_produtos)
total_produtos_em_transacoes = len(lista_produtos_brutos)

print(f"Total de produtos instanciados: {total_produtos_em_transacoes}")
print(f"Total de produtos distintos: {total_produtos_distintos}")

# Análise da Frequência 
# Produtos que aparecem uma vez 
produtos_uma_vez = sum(1 for contagem in contador_produtos.values() if contagem == 1)
print(f"\nProdutos que aparecem em APENAS 1 transação: {produtos_uma_vez} ({(produtos_uma_vez / total_produtos_distintos) * 100:.2f}%")

# Produtos que aparecem em 10 ou menos 
produtos_poucas_vezes = sum(1 for contagem in contador_produtos.values() if contagem <= 10)
print(f"Produtos que aparecem em 10 ou menos transações: {produtos_poucas_vezes} ({(produtos_poucas_vezes / total_produtos_distintos) * 100:.2f}%")

"""Criar Categorias? 
Muitos produtos aparecem em poucas transações indica, o que indica esparsidade(muitos itens únicos).Talvez a criação de categorias reduza essa esparsidade e aumente a frequência de ocorrência."""


# Top 10 Produtos 
print("\nTop 10 Produtos:")
df_top10 = pd.DataFrame(contador_produtos.most_common(10), columns=['Produto', 'Frequência'])
print(df_top10)