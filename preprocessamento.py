# preprocessamento.py
import pandas as pd
import re
import unidecode
from collections import Counter

class PreprocessadorVestuario:
    """
    Pré-processador especializado em dados de vestuário com mapeamento para categorias.
    """

    def __init__(self):
        #Set de palavras irrelevantes 
        self.palavras_irrelevantes = {
            "pimpolho","micol","kids","baby","modas","luziane","italico","minasrey","bilu",
            "mrm","dengo","flaphy","rekorte","d","vystek","ld","needfeel","mecbee","rianna",
            "mic","boys","unissex","fem","masc","juvenil","infantil","unid","cm","moda",
            "intima","confeccoes","fashion","sergio","visual","mania","dom","matheus","sg","de","da","do","com","sem","para","no","na","ao","a","o","e","c","x","tag",
            "pares","cos","bojo","aberto","tradicional","algodao","elastico","cordao"
        }

        #Categorias extraídas por nós - Adicionar uma exploração com pandas no no projeto?  
        self.categorias_mapeamento = {
            # superiores
            "camisa": {"camisa","camiseta","blusa","polo","t shirt","tshirt"},
            "regata": {"regata","machao"},
            # inferiores
            "short": {"short","shorts","bermuda","mauricinho"},
            "calca": {"calca","jeans","sarja","moletom","legging"},
            "saia": {"saia"},
            # íntimos
            "calcinha": {"calcinha","tanga"},
            "cueca": {"cueca","boxer","cuecas"},
            "sutia": {"sutia","top"},
            "sunga": {"sunga"},
            # dormir
            "pijama": {"pijama","baby doll"},
            # outros
            "meia": {"meia","meia calca"},
            "body": {"body"},
            "macacao": {"macacao","macaquito"},
            "jaqueta": {"jaqueta","casaco","cardigan"},
            "vestido": {"vestido","vestidos"},
            "biquini": {"biquini","bikini"}
        }

    #Usa o unicode e o re pra padronizar os textos de descricao
    def limpar_descricao_produtos(self, texto: str) -> str:
        descricao = unidecode.unidecode(str(texto).lower())
        descricao = re.sub(r"[^a-z0-9\s;]", " ", descricao)
        descricao = re.sub(r"\b(p|m|g|gg|xg|2g|3g|4g|5g)\b", " ", descricao)
        descricao = re.sub(r"\d+", " ", descricao)
        for palavra in self.palavras_irrelevantes:
            descricao = re.sub(rf"\b{re.escape(palavra)}\b", " ", descricao)
        descricao = re.sub(r"\s+", " ", descricao).strip()
        return descricao

    #Verifica se as palavras em cada linha da descricao de produtos corresponde a alguma palavra do set de categorias. 
    # Assim, transforma cada produto em uma categoria, criando um set de produtos em cada linha
    def extrair_categorias(self, descricao_original: str) -> list[str]:
        if not isinstance(descricao_original, str) or not descricao_original.strip():
            return []
        descricao = unidecode.unidecode(descricao_original.lower())
        categorias = set()
        for categoria, palavras_correspondentes in self.categorias_mapeamento.items():
            for palavra in palavras_correspondentes:
                if palavra in descricao:
                    categorias.add(categoria)
                    break
        return sorted(categorias)

    #Processa os dados, retornando um DATAFRAME com o id de cada transação e uma lista de produtos(categorias) em cada linha. 
    def processar(self, caminho_csv: str) -> pd.DataFrame:
        print("Processando dados...")
        dados = pd.read_csv(caminho_csv, dtype={"id_transacao": str}).dropna(subset=["descricao_produtos"])

        dados["descricao_limpa"] = dados["descricao_produtos"].apply(self.limpar_descricao_produtos)
        """.apply é equivalente a 
                novos_valores = []
                for linha in dados["descricao_produtos"]:
                resultado = self.extrair_categorias(linha)
                novos_valores.append(resultado) """

        print("Usando CATEGORIAS de produtos")
        dados["lista_produtos"] = dados["descricao_produtos"].apply(self.extrair_categorias)

        dados["lista_produtos"] = dados["lista_produtos"].apply(lambda xs: sorted(set(xs)) if xs else [])
        dados = dados[dados["lista_produtos"].apply(len) > 0].copy()

        # Estatísticas simples -- Não sei também se nós sozinhos teríamos mantido isso
        todos = [item for xs in dados["lista_produtos"] for item in xs]
        contagem = Counter(todos)
        print(f"{len(dados)} transações válidas | {len(contagem)} itens/categorias únicos(as)")
        print("Top 10 itens/categorias:")
        for item, cnt in contagem.most_common(10):
            print(f"  • {item:15s}: {cnt:4d} ({cnt/len(dados):5.2%})")


        return dados[["id_transacao","lista_produtos"]]
    

# --------------------
#Não sei se a gente realmente faria essas funções de vizualização aqui.
def salvar_transacoes(df_proc: pd.DataFrame, caminho_out: str = "transacoes_categorias.csv"):
    """ Salva o dataset pré-processado no formato:
        id_transacao, lista_produtos (pipe-separated)
    """
    df_out = df_proc.copy()
    df_out["lista_produtos"] = df_out["lista_produtos"].apply(lambda xs: "|".join(xs))
    df_out.to_csv(caminho_out, index=False, encoding="utf-8")
    print(f"✓ Transações salvas em '{caminho_out}'")


def salvar_onehot(df_proc: pd.DataFrame, caminho_out: str = "matriz_onehot.csv"):
    """
    Salva matriz binária transacao × categoria (one-hot).
    """
    dfe = df_proc.copy().explode("lista_produtos").dropna(subset=["lista_produtos"])
    dfe["valor"] = 1
    # Pivot para matriz
    matriz = (
        dfe.pivot_table(index="id_transacao", columns="lista_produtos", values="valor", fill_value=0, aggfunc="max")
        .reset_index()
    )
    matriz.to_csv(caminho_out, index=False, encoding="utf-8")
    print(f"✓ Matriz one-hot salva em '{caminho_out}'")




