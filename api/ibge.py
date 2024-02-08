import pandas as pd
import requests

URL_IPCA = "https://apisidra.ibge.gov.br/values/t/1737/n1/all/v/2266/p/all/d/v2266%2013"

class IbgeApi:
    """
    Classe que acessa as APIs disponibilizadas pelo IBGE
    """    
    @classmethod
    def carregar_dados_completos_ipca(cls) -> pd.DataFrame:
        """
        Carrega todos os dados de IPCA disponíveis

        Returns
        -------
        pd.DataFrame
            DataFrame com todos os dados de IPCA
            OBS: A data está no campo _id para que ela seja usado como identificador da collection (o conse)
        """

        dados = requests.get(URL_IPCA, verify=False).json()

        # Transforma em DataFrame
        df_result = pd.DataFrame(dados, columns=['D3C', 'V'])
        df_result.drop(0, inplace=True)
        df_result.columns = ['_id', 'num_indice']
        df_result['_id'] = pd.to_datetime(df_result['_id'], format="%Y%m")
        df_result['num_indice'] = pd.to_numeric(df_result['num_indice'])
        
        return df_result
