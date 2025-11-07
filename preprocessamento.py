import pandas as pd
import re
import unidecode
from collections import Counter

class PreprocessadorVestuario:
    """
    Pré-processador especializado em dados de vestuário com mapeamento para categorias.
    """

    def __init__(self):
        self.palavras_irrelevantes = {
            "pimpolho","micol","kids","baby","modas","luziane","italico","minasrey","bilu",
            "mrm","dengo","flaphy","rekorte","d","vystek","ld","needfeel","mecbee","rianna",
            "mic","boys","unissex","fem","masc","juvenil","infantil","unid","cm","moda",
            "intima","confeccoes","fashion","sergio","visual","mania","dom","matheus","sg","de","da","do","com","sem","para","no","na","ao","a","o","e","c","x","tag",
            "pares","cos","bojo","aberto","tradicional","algodao","elastico","cordao"
        }
  
        self.categorias_mapeamento = {
            "camisa": {"camisa","camiseta","blusa","polo","gola polo","t shirt","tshirt", "t-shirt","baby look","bata","cropped","camisa manga" },
            "regata": {"regata","machao","machão"},
            "short": {"short","shorts","bermuda","mauricinho", "tactel","short-saia","short saia", "bermudinha" },
            "calca": {"calca","jeans","sarja","moletom","legging","leggue","legin","jogger","calça" },
            "saia": {"saia"},
            "calcinha": {"calcinha","tanga","fio dental","calcinha box"},
            "cueca": {"cueca","boxer","cuecas", "cueca box"},
            "sutia": { "sutia","top","sutiã","top cropped","bojo"},
            "sunga": {"sunga", "sungas"},
            "fralda_pano": {"fralda","fraldinha","cueiro"},
            "pijama": {"pijama","baby doll","camisola","pijama longo","pijama curto"},
            "meia": {"meia","meia calca", "meiao", "meias"},
            "body": {"body","bory","bodie"},
            "mijao": {"mijao","mijão","mijão aberto","mijao aberto"},
            "macacao": {  "macacao","macaquito","macacão","jardineira","macacao curto","macacao longo"},
            "jaqueta": {"jaqueta","casaco","cardigan"},
            "vestido": {"vestido","vestidos"},
            "biquini": { "biquini","bikini","maio","maiô"},
            "toalha": {"toalha","toalhas","toalha rosto","toalha banho","toalha de rosto","toalha de banho"},
            "roupa_cama": {"lencol","lençol","jogo de cama","fronha","edredom","coberta","cobertor","manta","cobre leito","travesseiro", "protetor"}
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
        descricao = unidecode.unidecode(descricao_original.lower()) ##Tirar? 
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

        dados["lista_produtos"] = dados["lista_produtos"].apply(lambda lista_itens: sorted(set(lista_itens)) if lista_itens else [])
        dados = dados[dados["lista_produtos"].apply(len) > 0].copy()

        return dados[["id_transacao","lista_produtos"]]

