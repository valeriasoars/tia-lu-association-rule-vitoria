def analisar_resultados(modelo_eclat):
    print("="*80)
    print("ANÁLISE DE RESULTADOS")
    print("="*80)

    grupos = {}
    # Agora cada itemset tem suporte como float (ex: 0.15), não contagem
    for itemset, suporte in modelo_eclat.itemsets_frequentes.items():
        k = len(itemset)
        grupos.setdefault(k, []).append((itemset, suporte))

    print("\nTOP ITEMSETS POR TAMANHO:\n")
    for k in sorted(grupos.keys()):
        print(f"--- Itemsets de tamanho {k} ---")
        # Ordena pelos mais frequentes
        top = sorted(grupos[k], key=lambda x: x[1], reverse=True)[:15]
        for iset, sup in top:
            # agora já é proporção, então não divide por total_transacoes
            cont = sup * modelo_eclat.total_transacoes  # só pra mostrar também o número estimado de transações
            print(f"  • {' + '.join(sorted(iset)):35s} | {sup:6.2%} ({cont:6.1f})")
        print()

    if modelo_eclat.regras:
        print("\nTOP 20 REGRAS DE ASSOCIAÇÃO:\n")
        for i, r in enumerate(modelo_eclat.regras[:20], 1):
            ant = " + ".join(r["antecedente"])
            cons = " + ".join(r["consequente"])
            print(f"{i:2d}. [{ant}] → [{cons}] | sup={r['suporte']:.2%} conf={r['confianca']:.1%} lift={r['lift']:.2f}")
    else:
        print("\nNenhuma regra gerada com os parâmetros atuais")

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
