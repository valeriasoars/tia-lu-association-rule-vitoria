import pandas as pd
from preprocessamento import PreprocessadorVestuario
from eclat import MineradorECLAT
from analise import analisar_resultados, exemplos_recomendacao

if __name__ == "__main__":
    caminho_csv = "vendas_dataset.csv"

    # 1) Pré-processamento (usar categorias para reduzir esparsidade)
    prep = PreprocessadorVestuario()
    df_proc = prep.processar(caminho_csv)
    transacoes = df_proc["lista_produtos"].tolist()
    print(f"\nTransações após processamento: {len(transacoes)}")

    # 2) ECLAT
    miner = MineradorECLAT(min_suporte=0.01, min_confianca=0.40, min_lift=1.10)
    miner.ajustar(transacoes, max_tamanho=3).gerar_regras()

    # 3) Análise e exemplos
    analisar_resultados(miner)
    exemplos_recomendacao(miner)

    # 4) Salvar saídas
    fi_df = pd.DataFrame(
        [{"itemset": tuple(sorted(k)), "count": v, "support": v/ miner.total_transacoes}
         for k, v in miner.itemsets_frequentes.items()]
    ).sort_values(["support","count"], ascending=[False, False]).reset_index(drop=True)
    regras_df = miner.regras_df()

    fi_df.to_csv("itemsets_frequentes_eclat.csv", index=False, encoding="utf-8")
    regras_df.to_csv("regras_associacao_eclat.csv", index=False, encoding="utf-8")
    print("\n Arquivos salvos: itemsets_frequentes_eclat.csv, regras_associacao_eclat.csv")
