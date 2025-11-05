# eclat.py
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
        tid = defaultdict(set)
        for t_id, itens in enumerate(transacoes):
            for it in itens:
                tid[it].add(t_id)
        return {item: frozenset(tids) for item, tids in tid.items()}

    def _eclat(self, tidlist, min_count):
        # 1-itemsets
        L1 = [(frozenset([i]), tids) for i, tids in tidlist.items() if len(tids) >= min_count]
        L1.sort(key=lambda x: len(x[1]))
        freq = {}

        def dfs(prefix_items, prefix_tids, tail):
            for idx in range(len(tail)):
                Xi_items, Xi_tids = tail[idx]
                novo_items = prefix_items | Xi_items if prefix_items else Xi_items
                novo_tids  = (prefix_tids & Xi_tids) if prefix_items else Xi_tids
                sup = len(novo_tids)
                if sup >= min_count:
                    freq[novo_items] = sup
                    novo_tail = []
                    for Yj_items, Yj_tids in tail[idx+1:]:
                        inter = novo_tids & Yj_tids
                        if len(inter) >= min_count:
                            novo_tail.append((Yj_items, inter))
                    novo_tail.sort(key=lambda x: len(x[1]))
                    dfs(novo_items, novo_tids, novo_tail)

        dfs(frozenset(), frozenset(), L1)
        return freq

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
