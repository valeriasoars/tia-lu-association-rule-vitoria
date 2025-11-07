import pandas as pd
from collections import Counter
from preprocessamento import PreprocessadorVestuario

prep = PreprocessadorVestuario()
df_proc = prep.processar("vendas_dataset.csv")  
N = len(df_proc)

# Contagem de categorias por transação
contagem = Counter()
for cats in df_proc["lista_produtos"]:
    contagem.update(set(cats))  

# DataFrame de cobertura por categoria
cats_df = (
    pd.DataFrame(contagem.items(), columns=["categoria","freq_transacoes"])
    .sort_values("freq_transacoes", ascending=False)
    .reset_index(drop=True)
)

cats_df["cobertura_%"] = (cats_df["freq_transacoes"] / N) * 100

dados_brutos = len(pd.read_csv("vendas_dataset.csv"))
total_transacoes = len(df_proc)
transacoes_com_categoria = (df_proc["lista_produtos"].apply(len) > 0).sum()  

cobertura_global = transacoes_com_categoria / dados_brutos

print(f"Cobertura categoria: {cobertura_global:.1%}  [{transacoes_com_categoria}/{dados_brutos}] ")
print(f"Transações válidas: {N}")
print("\nCobertura por categoria:")
print(cats_df.to_string(index=False))

