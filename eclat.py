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
        
        combinacoes_frequentes= {} #cria dict vazio para guardar as combinações frequentes

        def gerar_combinacoes_frequentes(itens_prefixo, itens_restantes, combinacoes_frequentes): #recebe o prefixo(inicialmente vazio), os itens para combinar com o prefixo e o dict

            itens_restantes_ordenados = sorted(itens_restantes.items(), key= lambda lista_itens: len(lista_itens[1])) #Ordena os itens restantes, inicialmente, todos os itens. 

            for index, (item_atual, transacoes_atuais) in enumerate(itens_restantes_ordenados): #passa por todos os itens e suas transações em itens_restantes_ordenados
                nova_combinacao = itens_prefixo | item_atual #une o prefixo(inicialmente vazio) e o item atual
                suporte  = len(transacoes_atuais)/self.total_transacoes #calcula suporte do item atual

                if suporte >= self.min_suporte: #verifica se suporte atende o mínimo suporte definido
                    combinacoes_frequentes[nova_combinacao] = suporte #adiciona a combinação nova e seu suporte no set de combinações frequentes
                
                novos_itens_restantes = {} #cria dict de itens restantes
                for proximo_item, proxima_transacao in itens_restantes_ordenados[index + 1:]: #passa por todos os itens restantes depois do item atual que já analisamos
                    interceccao = transacoes_atuais & proxima_transacao #verifica se existe intersecção entre o item que analisamos e o item que estamos analisando agora
                    if len(interceccao) >= min_count: #se a intersecção for maior do que o minimo definido, colocamos o proximo item e suas transações que que também estão no item que analisamos na lista de novos itens a serem analisados
                        novos_itens_restantes[proximo_item] = interceccao
                    
                if novos_itens_restantes: #se o dict de novos_itens_restantes não estiver vazio, chama a propria função, agora com o prefixo do item que analisamos primeiro, os novos itens restantes(que possuem alguma intersecao com os intensd de prefixo)
                    gerar_combinacoes_frequentes(nova_combinacao, novos_itens_restantes, combinacoes_frequentes)

        gerar_combinacoes_frequentes(frozenset(), dict(itens_frequentes), combinacoes_frequentes) #chama a função combinar para passar por todos os itens frequentes
        return combinacoes_frequentes #retorna todas as combinações encontradas

    def minerar_itemsets(self, transacoes, max_tamanho: int = None): #trocar nome
        self.transacoes = [sorted(set(transacao)) for transacao in transacoes if transacao] #Remove transacoes vazias, duplicatas e ordena cada transação.
        self.total_transacoes = len(self.transacoes) #Encontra o total de transações
        min_count = max(1, math.ceil(self.min_suporte * self.total_transacoes)) #faz o contador mínimo, sendo 1 ou o valor que der a conta do suporte minimo. 

        print(f"Minerando itemsets (N={self.total_transacoes}, suporte mínimo={self.min_suporte:.2%} => {min_count})")
        tidlist = self._construir_tidlist(self.transacoes) #chama a função de construir o TIDLIST
        combinacoes_encontradas = self._eclat(tidlist, min_count) #chama o eclat

        if max_tamanho is not None: #filtra para tamanho máximo de conjuntos de itens (se houver)
            combinacoes_encontradas = {conjunto_itens: transacoes_itens for conjunto_itens, transacoes_itens in combinacoes_encontradas.items() if len(conjunto_itens) <= max_tamanho}

        self.itemsets_frequentes = combinacoes_encontradas #atribui os itens frequentes as combinações encontradas no eclat
        print(f"Itemsets frequentes: {len(self.itemsets_frequentes)}") 
        return self #retorna o proprio objeto

    def gerar_regras(self):
        regras = [] #Cria lista vaia de regras

        for itemset, suporte_itemset in self.itemsets_frequentes.items(): #passa por todos os itens e seus respsctivos suportes em itens frequentes encontrados
            if len(itemset) < 2: #só continua se houver combinação (mais de um item)
                continue

            itens = list(itemset) #(transforma o itemset em lista)
            for idx in range(1, len(itens)): #itera sobre a quantidade de itens no itemset
                for itens_antecedentes in combinations(itens, idx): #combina todos os itens atecedentes (que começa com um só graças ao idx) com os itens consequencia
                    itens_antecedentes = frozenset(itens_antecedentes) #gera um frozenset com os itens antecedentes
                    itens_consequencia = itemset - itens_antecedentes #gera os itens consequencia

                    suporte_itens_antecedentes = self.itemsets_frequentes.get(itens_antecedentes, 0) #pega o suporte dos itens antecedentes
                    suporte_itens_restantes = self.itemsets_frequentes.get(itens_consequencia, 0) #pega o suporte dos intens consequencia
                    if suporte_itens_antecedentes == 0 or suporte_itens_restantes == 0: #verifica se esse suporte realmente existe
                        continue

                    confianca = suporte_itemset / suporte_itens_antecedentes #calcula a confiança (probabilidade de B ocorrer dado que A ocorreu.)
                    lift = confianca / suporte_itens_restantes #calcula o lift (Mede o quanto a presença de A aumenta (ou não) a chance de B.)

                    if confianca >= self.min_confianca and lift >= self.min_lift: #adiciona a regra a lista de regras se passar pela confiação e lift minimos

                        regras.append({
                            "antecedente": tuple(sorted(itens_antecedentes)), #transforma em tupla porque conjuntos (set) não podem ser salvos diretamente em CSV ou DataFrame.
                            "consequente": tuple(sorted(itens_consequencia)),
                            "suporte": suporte_itemset,
                            "confianca": confianca,
                            "lift": lift
                        })

        regras.sort(key=lambda r: (-r["lift"], -r["confianca"], -r["suporte"])) #ordena as regras
        self.regras = regras #atribui as regras
        print(f"Regras geradas: {len(self.regras)}")
        return self 

    def regras_df(self) -> pd.DataFrame:
        if not self.regras:
            return pd.DataFrame()
        return pd.DataFrame(self.regras)

    def recomendar(self, itens_carrinho, top_n=5):
        carrinho = set(itens_carrinho)
        rank = defaultdict(float)
        for regra in self.regras:
            antecedente = set(regra["antecedente"])
            if antecedente.issubset(carrinho):
                for consequente in regra["consequente"]:
                    if consequente not in carrinho:
                        rank[consequente] += regra["lift"] * regra["confianca"]
        return sorted(rank.items(), key=lambda x: x[1], reverse=True)[:top_n]
