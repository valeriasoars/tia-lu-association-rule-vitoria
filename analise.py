# analise.py
def analisar_resultados(modelo_eclat):
    print("="*80)
    print("ANÁLISE DE RESULTADOS")
    print("="*80)

    grupos = {}
    for itemset, cont in modelo_eclat.itemsets_frequentes.items():
        k = len(itemset)
        grupos.setdefault(k, []).append((itemset, cont))

    print("\n TOP ITEMSETS POR TAMANHO:\n")
    for k in sorted(grupos.keys()):
        print(f"--- Itemsets de tamanho {k} ---")
        top = sorted(grupos[k], key=lambda x: x[1], reverse=True)[:15]
        for iset, cnt in top:
            sup = cnt / modelo_eclat.total_transacoes
            print(f"  • {' + '.join(sorted(iset)):35s} | {sup:6.2%} ({cnt:4d})")
        print()

    if modelo_eclat.regras:
        print("\n TOP 20 REGRAS DE ASSOCIAÇÃO:\n")
        for i, r in enumerate(modelo_eclat.regras[:20], 1):
            ant = " + ".join(r["antecedente"])
            cons = " + ".join(r["consequente"])
            print(f"{i:2d}. [{ant}] → [{cons}] | sup={r['suporte']:.2%} conf={r['confianca']:.1%} lift={r['lift']:.2f}")
    else:
        print("\n Nenhuma regra gerada com os parâmetros atuais")

def exemplos_recomendacao(modelo_eclat):
    print("\n" + "="*80)
    print("EXEMPLOS DE RECOMENDAÇÃO")
    print("="*80 + "\n")

    exemplos = [
        ["camisa"],
        ["calcinha"],
        ["short", "camisa"],
        ["pijama"],
    ]
    for carrinho in exemplos:
        print(f"Carrinho: {carrinho}")
        recs = modelo_eclat.recomendar(carrinho, top_n=5)
        if recs:
            for i, (item, score) in enumerate(recs, 1):
                print(f"  {i}. {item} (score: {score:.2f})")
        else:
            print("  Sem recomendações")
        print("-"*60)
