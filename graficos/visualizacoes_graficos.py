import matplotlib.pyplot as plt
import numpy as np


def visualizar_top_items(modelo_eclat, top_n=15):
    """
    Gráfico de barras horizontais com os itens mais frequentes
    """
    items_individuais = {
        list(itemset)[0]: suporte 
        for itemset, suporte in modelo_eclat.itemsets_frequentes.items() 
        if len(itemset) == 1
    }
    
    items_sorted = sorted(items_individuais.items(), key=lambda x: x[1], reverse=True)[:top_n]
    items, suportes = zip(*items_sorted)
    
    fig, ax = plt.subplots(figsize=(10, 8))
    y_pos = np.arange(len(items))
    
    colors = plt.cm.viridis(np.linspace(0.3, 0.9, len(items)))
    
    bars = ax.barh(y_pos, [s * 100 for s in suportes], color=colors)
    ax.set_yticks(y_pos)
    ax.set_yticklabels(items)
    ax.invert_yaxis()
    ax.set_xlabel('Suporte (%)', fontsize=12, fontweight='bold')
    ax.set_title(f'Top {top_n} Produtos Mais Comprados', fontsize=14, fontweight='bold', pad=20)
    ax.grid(axis='x', alpha=0.3, linestyle='--')
    
    for i, (bar, sup) in enumerate(zip(bars, suportes)):
        width = bar.get_width()
        ax.text(width + 0.5, bar.get_y() + bar.get_height()/2, 
                f'{sup*100:.1f}%', ha='left', va='center', fontsize=9)
    
    plt.tight_layout()
    return fig

def visualizar_itemsets_por_tamanho(modelo_eclat):
    """
    Gráfico de barras mostrando distribuição de itemsets por tamanho
    """
    tamanhos = {}
    for itemset in modelo_eclat.itemsets_frequentes.keys():
        k = len(itemset)
        tamanhos[k] = tamanhos.get(k, 0) + 1
    
    fig, ax = plt.subplots(figsize=(10, 6))
    
    sizes = sorted(tamanhos.keys())
    counts = [tamanhos[s] for s in sizes]
    
    colors = plt.cm.plasma(np.linspace(0.3, 0.9, len(sizes)))
    bars = ax.bar(sizes, counts, color=colors, edgecolor='black', linewidth=1.5)
    
    ax.set_xlabel('Tamanho do Itemset', fontsize=12, fontweight='bold')
    ax.set_ylabel('Quantidade de Itemsets', fontsize=12, fontweight='bold')
    ax.set_title('Distribuição de Itemsets Frequentes por Tamanho', 
                 fontsize=14, fontweight='bold', pad=20)
    ax.set_xticks(sizes)
    ax.grid(axis='y', alpha=0.3, linestyle='--')
    
    # Adiciona valores nas barras
    for bar, count in zip(bars, counts):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height,
                f'{count}', ha='center', va='bottom', fontsize=11, fontweight='bold')
    
    plt.tight_layout()
    return fig

def visualizar_top_pares(modelo_eclat, top_n=10):
    """
    Gráfico de barras com os pares de produtos mais frequentes
    """
    # Filtra itemsets de tamanho 2
    pares = {
        itemset: suporte 
        for itemset, suporte in modelo_eclat.itemsets_frequentes.items() 
        if len(itemset) == 2
    }
    
    # Ordena e pega top N
    pares_sorted = sorted(pares.items(), key=lambda x: x[1], reverse=True)[:top_n]
    
    labels = [' + '.join(sorted(par)) for par, _ in pares_sorted]
    suportes = [sup * 100 for _, sup in pares_sorted]
    
    fig, ax = plt.subplots(figsize=(12, 8))
    y_pos = np.arange(len(labels))
    
    colors = plt.cm.coolwarm(np.linspace(0.2, 0.8, len(labels)))
    bars = ax.barh(y_pos, suportes, color=colors, edgecolor='black', linewidth=1)
    
    ax.set_yticks(y_pos)
    ax.set_yticklabels(labels, fontsize=10)
    ax.invert_yaxis()
    ax.set_xlabel('Suporte (%)', fontsize=12, fontweight='bold')
    ax.set_title(f'Top {top_n} Combinações de 2 Produtos', 
                 fontsize=14, fontweight='bold', pad=20)
    ax.grid(axis='x', alpha=0.3, linestyle='--')
    
    # Adiciona valores
    for bar, sup in zip(bars, suportes):
        width = bar.get_width()
        ax.text(width + 0.2, bar.get_y() + bar.get_height()/2,
                f'{sup:.1f}%', ha='left', va='center', fontsize=9)
    
    plt.tight_layout()
    return fig

def visualizar_regras_associacao(modelo_eclat, top_n=10):
    """
    Gráfico de dispersão: Confiança vs Lift das regras
    """
    if not modelo_eclat.regras:
        print("Nenhuma regra disponível para visualização")
        return None
    
    top_regras = modelo_eclat.regras[:top_n]
    
    confidencias = [r['confianca'] * 100 for r in top_regras]
    lifts = [r['lift'] for r in top_regras]
    suportes = [r['suporte'] * 100 for r in top_regras]
    labels = [f"{' + '.join(r['antecedente'])} → {' + '.join(r['consequente'])}" 
              for r in top_regras]
    
    fig, ax = plt.subplots(figsize=(12, 8))
    
    # Tamanho das bolhas proporcional ao suporte
    sizes = [s * 50 for s in suportes]
    
    scatter = ax.scatter(confidencias, lifts, s=sizes, alpha=0.6, 
                        c=lifts, cmap='RdYlGn', edgecolors='black', linewidth=1.5)
    
    ax.set_xlabel('Confiança (%)', fontsize=12, fontweight='bold')
    ax.set_ylabel('Lift', fontsize=12, fontweight='bold')
    ax.set_title(f'Top {top_n} Regras de Associação (tamanho = suporte)', 
                 fontsize=14, fontweight='bold', pad=20)
    ax.grid(True, alpha=0.3, linestyle='--')
    ax.axhline(y=1, color='red', linestyle='--', linewidth=2, alpha=0.7, label='Lift = 1 (independência)')
    
    # Colorbar
    cbar = plt.colorbar(scatter, ax=ax)
    cbar.set_label('Lift', fontsize=11, fontweight='bold')
    
    # Adiciona labels para as regras mais interessantes
    for i, (x, y, label) in enumerate(zip(confidencias, lifts, labels)):
        if i < 5:  # Apenas top 5
            ax.annotate(label, (x, y), xytext=(5, 5), textcoords='offset points',
                       fontsize=8, bbox=dict(boxstyle='round,pad=0.3', 
                       facecolor='yellow', alpha=0.7))
    
    ax.legend(fontsize=10)
    plt.tight_layout()
    return fig

def visualizar_metricas_regras(modelo_eclat, top_n=10):
    """
    Gráfico de barras agrupadas: Suporte, Confiança e Lift das top regras
    """
    if not modelo_eclat.regras:
        print("Nenhuma regra disponível para visualização")
        return None
    
    top_regras = modelo_eclat.regras[:top_n]
    
    labels = [f"{' + '.join(r['antecedente'][:1])} → {' + '.join(r['consequente'][:1])}" 
              for r in top_regras]
    
    suportes = [r['suporte'] * 100 for r in top_regras]
    confidencias = [r['confianca'] * 100 for r in top_regras]
    lifts = [r['lift'] * 10 for r in top_regras]  # Escala para visualização
    
    x = np.arange(len(labels))
    width = 0.25
    
    fig, ax = plt.subplots(figsize=(14, 8))
    
    bars1 = ax.bar(x - width, suportes, width, label='Suporte (%)', 
                   color='skyblue', edgecolor='black')
    bars2 = ax.bar(x, confidencias, width, label='Confiança (%)', 
                   color='lightcoral', edgecolor='black')
    bars3 = ax.bar(x + width, lifts, width, label='Lift (×10)', 
                   color='lightgreen', edgecolor='black')
    
    ax.set_xlabel('Regras', fontsize=12, fontweight='bold')
    ax.set_ylabel('Valor', fontsize=12, fontweight='bold')
    ax.set_title(f'Métricas das Top {top_n} Regras de Associação', 
                 fontsize=14, fontweight='bold', pad=20)
    ax.set_xticks(x)
    ax.set_xticklabels(labels, rotation=45, ha='right', fontsize=9)
    ax.legend(fontsize=11)
    ax.grid(axis='y', alpha=0.3, linestyle='--')
    
    plt.tight_layout()
    return fig

def visualizar_heatmap_coocorrencia(modelo_eclat, top_items=10):
    """
    Heatmap de co-ocorrência dos top items
    """
    items_individuais = {
        list(itemset)[0]: suporte 
        for itemset, suporte in modelo_eclat.itemsets_frequentes.items() 
        if len(itemset) == 1
    }
    
    top_items_list = sorted(items_individuais.items(), key=lambda x: x[1], reverse=True)[:top_items]
    top_items_names = [item for item, _ in top_items_list]
    
    n = len(top_items_names)
    matrix = np.zeros((n, n))
    
    for itemset, suporte in modelo_eclat.itemsets_frequentes.items():
        if len(itemset) == 2:
            items = list(itemset)
            if items[0] in top_items_names and items[1] in top_items_names:
                i = top_items_names.index(items[0])
                j = top_items_names.index(items[1])
                matrix[i][j] = suporte * 100
                matrix[j][i] = suporte * 100
    
    for i, item in enumerate(top_items_names):
        matrix[i][i] = items_individuais[item] * 100
    
    fig, ax = plt.subplots(figsize=(12, 10))
    
    im = ax.imshow(matrix, cmap='YlOrRd', aspect='auto')
    
    ax.set_xticks(np.arange(n))
    ax.set_yticks(np.arange(n))
    ax.set_xticklabels(top_items_names, rotation=45, ha='right')
    ax.set_yticklabels(top_items_names)
    
    # Adiciona valores na matriz
    for i in range(n):
        for j in range(n):
            if matrix[i][j] > 0:
                text = ax.text(j, i, f'{matrix[i][j]:.1f}',
                             ha="center", va="center", color="black", fontsize=8)
    
    ax.set_title('Heatmap de Co-ocorrência (Suporte %)', 
                 fontsize=14, fontweight='bold', pad=20)
    
    cbar = plt.colorbar(im, ax=ax)
    cbar.set_label('Suporte (%)', fontsize=11, fontweight='bold')
    
    plt.tight_layout()
    return fig

def gerar_relatorio_visual_completo(modelo_eclat):
    """
    Gera todos os gráficos e salva em arquivos
    """
    print("\n" + "="*80)
    print("GERANDO VISUALIZAÇÕES")
    print("="*80 + "\n")
    
    graficos = [
        ("top_items.png", visualizar_top_items, "Top Produtos"),
        ("itemsets_tamanho.png", visualizar_itemsets_por_tamanho, "Distribuição por Tamanho"),
        ("top_pares.png", visualizar_top_pares, "Top Pares"),
        ("regras_scatter.png", visualizar_regras_associacao, "Regras (Scatter)"),
        ("regras_metricas.png", visualizar_metricas_regras, "Métricas das Regras"),
        ("heatmap_coocorrencia.png", visualizar_heatmap_coocorrencia, "Heatmap Co-ocorrência"),
    ]
    
    for filename, func, descricao in graficos:
        try:
            print(f"Gerando: {descricao}...")
            fig = func(modelo_eclat)
            if fig:
                fig.savefig(filename, dpi=300, bbox_inches='tight')
                plt.close(fig)
                print(f"  ✓ Salvo em: {filename}")
        except Exception as e:
            print(f"  ✗ Erro ao gerar {descricao}: {e}")
    
    print("\n" + "="*80)
    print("VISUALIZAÇÕES CONCLUÍDAS")
    print("="*80)

def exibir_dashboard(modelo_eclat):
    """
    Exibe todos os gráficos em uma única janela
    """
    fig = plt.figure(figsize=(20, 12))
    
    gs = fig.add_gridspec(3, 2, hspace=0.3, wspace=0.3)
    
    print("Gerando dashboard interativo...")
    
    visualizar_top_items(modelo_eclat)
    visualizar_top_pares(modelo_eclat)
    visualizar_regras_associacao(modelo_eclat)
    visualizar_heatmap_coocorrencia(modelo_eclat)
    
    plt.show()
