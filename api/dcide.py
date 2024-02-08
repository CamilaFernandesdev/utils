# -*- coding: utf-8 -*-
"""Consulta aos dados da DCIDE via API."""
from time import sleep
import requests

import datetime

import pandas as pd
from tqdm import tqdm

from infra_copel.config import cfg_dcide_api

URL_CURVA = 'https://curva-compilada-api.denergia.com.br/v1'
URL_POOL = 'https://pool.denergia.com.br/api/curva'


def apirequest(method, url, **kwargs):
    """Realiza um request via API e retorna o resultado."""
    # Apenas para limitar os requests a 5 por segundo.
    # TODO: Melhorar futuramente
    sleep(0.2)

    response = requests.request(method, url, **kwargs)
    if response.status_code != 200:
        raise Exception('Erro na requisição', response)

    resp_dict = response.json()
    if resp_dict.get('error'):
        raise Exception('Erro na requisição', resp_dict.get('msg'))
    if resp_dict.get('success') or resp_dict.get('error') is False:
        return resp_dict['result']


class DcideApi:
    """
    Classe que representa conexão com o 'historico_oficial' no MongoDB.

    Attributes
    ----------
    session_key: str
    username: str

    """

    data_mais_antiga = pd.to_datetime('02/01/2012', dayfirst=True)
    data_mais_antiga_fontes_ext = pd.to_datetime('23/10/2016', dayfirst=True)

    # %% Construtor

    def __init__(self):

        # Autenticação
        url = f'{URL_CURVA}/auth/login'
        cfg = cfg_dcide_api()
        self._verify_ssl = cfg.get('verify_ssl')
        if self._verify_ssl is False:
            # Desabilita warnings
            requests.packages.urllib3.disable_warnings(
                requests.packages.urllib3.exceptions.InsecureRequestWarning
                )
        dados_login = {'userName': cfg['userName'],
                       'senha': cfg['senha']}
        resp_auth = apirequest('POST', url, data=dados_login,
                               verify=self._verify_ssl)
        self.session_key = resp_auth['sessionKey']
        self.username = resp_auth['userName']

    # %% Métodos da API

    def _api_metricas(self):

        url = f'{URL_CURVA}/metricas'
        headers = {'Authorization': self.session_key}

        response = apirequest('GET', url, headers=headers,
                              verify=self._verify_ssl)

        return response

    def _api_fontes(self):

        url = f'{URL_CURVA}/fontes'
        headers = {'Authorization': self.session_key}

        response = apirequest('GET', url, headers=headers,
                              verify=self._verify_ssl)

        return response

    def _api_curva(self, data: str):
        # Pesquisa Curva

        url = f'{URL_CURVA}/curva'
        headers = {'Authorization': self.session_key}

        data = pd.to_datetime(data, dayfirst=True)
        params = {'data_referencia': data.strftime('%d/%m/%Y'),
                  'estrutura': 'captura',
                  'metrica': 'media',
                  'ponto_entrega': 'sudeste',
                  'fonte': 'convencional',
                  'tipo_preco': 'preco_cheio',
                  },

        resp_curva = apirequest(url,
                                params=params,
                                headers=headers,
                                verify=self._verify_ssl)

        return resp_curva

    def _api_pool(self, data: str):

        data = pd.to_datetime(data, dayfirst=True)

        # Data limite da API
        if data < self.data_mais_antiga:
            raise Exception('Data muito antiga para a consulta.')

        fontes = ['forward_incentivada50_se',
                  'forward_competitiva_se',
                  ]

        # A partir desta data novas fontes estão disponíveis na API
        if data > self.data_mais_antiga_fontes_ext:
            fontes_ext = ['submercado_s',
                          'submercado_ne',
                          'submercado_n',
                          ]
            fontes.extend(fontes_ext)

        series = ['curva',
                  'media',
                  'mpd',
                  'liquidez',
                  'desvio_padrao,'
                  'metrica_consenso_queda',
                  'metrica_consenso_estabilidade',
                  'metrica_consenso_crescimento',
                  ]

        # Pesquisa POOL
        params = {
            'fonte': ','.join(fontes),
            'data': data.strftime('%d/%m/%Y'),
            'series': ','.join(series),
        }
        header = {
            'token': self.session_key,
            'userName': self.username,
        }
        resp_pool = apirequest('GET',
                               URL_POOL,
                               params=params,
                               headers=header,
                               verify=self._verify_ssl)

        if not resp_pool['data_publicacao']:
            raise ValueError(f'Valores ainda não publicados para a data {data}')

        return resp_pool

    # %% Métodos tratados

    def _pool_dataframes(self, data: str):

        pool = self._api_pool(data)

        fonte_df = {'semana': pool['semana'],
                    'data_base': pool['data_base'],
                    'fonte_energia': pool['fonte_energia']}
        for fonte in pool['fonte_energia']:
            dados = pool[fonte]
            df_dados = pd.DataFrame({k: v for k, v in dados.items() if v})
            df_dados['maturidades'] = pool['maturidades']
            df_dados['legendas'] = pool['legendas']
            df_dados.set_index(['maturidades', 'legendas'], inplace=True)
            fonte_df[fonte] = df_dados

        return fonte_df

    def pool_df_semana(self,
                     periodo_semana: pd.PeriodIndex,
                     ) -> pd.DataFrame:
        """
        Consulta o pool da DCIDE para uma semana.

        Parameters
        ----------
        data : pd.PeriodIndex
            Período da semana para a consulta.

        Returns
        -------
        DataFrame

        """
        pool = self._api_pool(periodo_semana.start_time.strftime('%d/%m/%Y'))

        fonte_df = {}
        for fonte in pool['fonte_energia']:
            dados = pool[fonte]
            
            df_dados = pd.DataFrame({k: v for k, v in dados.items() if v})

            df_dados['data_ini_vig'] = pool['data_base']
            df_dados['data_fim_vig'] = periodo_semana.end_time
            df_dados['semana'] = periodo_semana.week
            df_dados['maturidade'] = pool['maturidades']
            df_dados['legenda'] = pool['legendas']

            df_dados = self._tratar_dataframe_api(df_dados)

            df_dados.set_index(['data_ini_vig', 'data_fim_vig','semana', 'maturidade', 'legenda'], inplace=True)

            fonte_df[fonte] = df_dados

        df = pd.concat(fonte_df, names=['fonte_energia'])
        df.reset_index(inplace=True)
        df.set_index(['data_ini_vig', 'fonte_energia', 'data_fim_vig','semana', 'maturidade', 'legenda'],
                     inplace=True)
        return df

    def pool_df_data(self, data: datetime.datetime) -> pd.DataFrame:
        """
        Consulta o pool da DCIDE para uma deterninada data

        Parameters
        ----------
        data : datetime.datetime
            Data para a obtenção dos dados

        Returns
        -------
        pd.DataFrame
            DataFrame
        """
        semana = pd.period_range(data, data, freq='W').to_list()[0]
        
        return self.pool_df_semana(semana)
    
    def pool_df_data_range(self,
                           data_inicial: str,
                           data_final: str,
                           ) -> pd.DataFrame:
        """
        Consulta o pool da DCIDE para um período.

        Parameters
        ----------
        data_inicial : str
            Data inicial da consulta.
        data_final : str
            Data final da consulta.

        Returns
        -------
        DataFrame

        """
        # TODO: verificar range de datas válidas
        data_inicial = pd.to_datetime(data_inicial, dayfirst=True)
        data_final = pd.to_datetime(data_final, dayfirst=True)
        data_range = pd.period_range(data_inicial,
                                     data_final,
                                     freq='W',
                                     ).to_list()
        list_df = []
        for data in tqdm(data_range):
            df = self.pool_df_semana(data)
            list_df.append(df)

        return pd.concat(list_df)

    def _tratar_dataframe_api(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Trata o dataframe resultante da pesquisa da API
        O tratamento consiste em deixar os campos no tipo esperado
        
        Parameters
        ----------
        df : pd.DataFrame
            DataFrame criado a partir dos dados do API dcide
        """    
        df['data_ini_vig'] = pd.to_datetime(df['data_ini_vig'], format='%d/%m/%Y')

        
        return df
