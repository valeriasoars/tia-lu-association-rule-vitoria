import math
from collections import defaultdict
from itertools import combinations
import pandas as pd

class MineradorECLAT:
    """
    ECLAT no formato vertical (TID-lists) com geração de regras.
    """

    def __init__(self, min_suporte: float = 0.01, min_confianca: float = 0.4, min_lift: float = 1.1):
        self.min_suporte = min_suporte
        self.min_confianca = min_confianca
        self.min_lift = min_lift
        self.transacoes = []
        self.total_transacoes = 0
        self.itemsets_frequentes = {}   # {frozenset: contagem}
        self.regras = []

    def _construir_tidlist(self, transacoes):
        tidlist = defaultdict(set) #Cria dicionário onde cada item adicionado(chave) é acompanhado de um conjunto vazio(valor) -- set porque evita duplicatas
        for id_transacao, lista_itens in enumerate(transacoes): #percorre todas as transações passadas e dá um id a elas(através do enumerate)
            for produto in lista_itens: #percorre cada produto da lista de produtos
                tidlist[produto].add(id_transacao) #cria o produto como item no dicionário (se ele já não existir) e adciona a transação presente. 
        return {item: frozenset(tids) for item, tids in tidlist.items()} #transforma cada conjunto de produtos (conjunto de traasações - valor dos items do dict) em um frozenset(conjunto que não pode ter alterado)  
        #Retorna um TID List (Dicionario com item e conjunto de tranasações)

    def _eclat(self, tidlist, min_count):
        
        itens_frequentes = [(frozenset([item]), transacoes) for item, transacoes in tidlist.items() if len(transacoes) >= min_count] #Adicona cada 
        #item no formato frozen e sua respectiva lista de tranasações(TID) 
        #na lista_frequentes caso possuam a quantidade de transações estipulada. 
        itens_frequentes.sort(key=lambda x: len(x[1])) #Ordena a lista de frequentes do menos para mais frequente

        combinacoes_frequentes = {} #dicionario vazio que terá as combinações

        def dfs(prefix_items, prefix_tids, tail): #prefix_items é o conjunto atual de itens que estamos combinando(vazio no começo), prefix_tids é o conjunto de transações onde os itens aparecem juntos e tail é a lista dos proximos itens candidatos a combinar com o prefixo.  
            for indice_item in range(len(tail)):
                itens_atuais, transacoes_atuais = tail[indice_item] #Desempacota a tupla em dois elementos (os itens e as combinações em que ele está presente)
                novo_items = prefix_items | itens_atuais if prefix_items else itens_atuais
                novo_tids  = (prefix_tids & transacoes_atuais) if prefix_items else transacoes_atuais
                suport = len(novo_tids)
                if suport >= min_count:
                    combinacoes_frequentes[novo_items] = suport
                    novo_tail = []
                    for proximo_items, proximo_tids in tail[indice_item + 1:]:
                        interceccao = novo_tids & proximo_tids
                        if len(interceccao) >= min_count:
                            novo_tail.append((proximo_items, interceccao))
                    novo_tail.sort(key=lambda x: len(x[1]))
                    dfs(novo_items, novo_tids, novo_tail)

        dfs(frozenset(), frozenset(), itens_frequentes)
        return combinacoes_frequentes

    def ajustar(self, transacoes, max_tamanho: int = None):
        self.transacoes = [sorted(set(t)) for t in transacoes if t]
        self.total_transacoes = len(self.transacoes)
        min_count = max(1, math.ceil(self.min_suporte * self.total_transacoes))

        print(f"Minerando itemsets (N={self.total_transacoes}, suporte mínimo={self.min_suporte:.2%} => {min_count})")
        tidlist = self._construir_tidlist(self.transacoes)
        freq_counts = self._eclat(tidlist, min_count)

        # opcional: limitar por tamanho do itemset
        if max_tamanho is not None:
            freq_counts = {k: v for k, v in freq_counts.items() if len(k) <= max_tamanho}

        self.itemsets_frequentes = freq_counts
        print(f"Itemsets frequentes: {len(self.itemsets_frequentes)}")
        return self

    def gerar_regras(self):
        regras = []
        N = self.total_transacoes
        for itemset, sup_xy_count in self.itemsets_frequentes.items():
            if len(itemset) < 2:
                continue
            supp_xy = sup_xy_count / N
            itens = list(itemset)
            for r in range(1, len(itens)):
                for A in combinations(itens, r):
                    A = frozenset(A)
                    B = itemset - A
                    sup_a = self.itemsets_frequentes.get(A, 0)
                    sup_b = self.itemsets_frequentes.get(B, 0)
                    if sup_a == 0 or sup_b == 0:
                        continue
                    conf = supp_xy / (sup_a / N)
                    lift = conf / (sup_b / N)
                    if conf >= self.min_confianca and lift >= self.min_lift:
                        regras.append({
                            "antecedente": tuple(sorted(A)),
                            "consequente": tuple(sorted(B)),
                            "suporte": supp_xy,
                            "confianca": conf,
                            "lift": lift
                        })
        regras.sort(key=lambda r: (-r["lift"], -r["confianca"], -r["suporte"]))
        self.regras = regras
        print(f"Regras geradas: {len(self.regras)}")
        return self

    def regras_df(self) -> pd.DataFrame:
        if not self.regras:
            return pd.DataFrame()
        return pd.DataFrame(self.regras)

    def recomendar(self, itens_carrinho, top_n=5):
        carrinho = set(itens_carrinho)
        rank = defaultdict(float)
        for r in self.regras:
            ant = set(r["antecedente"])
            if ant.issubset(carrinho):
                for c in r["consequente"]:
                    if c not in carrinho:
                        rank[c] += r["lift"] * r["confianca"]
        return sorted(rank.items(), key=lambda x: x[1], reverse=True)[:top_n]
