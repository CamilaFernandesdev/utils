# -*- coding: utf-8 -*-
"""DAG de atualização do PLD no banco de dados e no sharepoint."""

# pylint: disable=import-error
# pylint: disable=import-outside-toplevel
# pylint: disable=invalid-name

from datetime import datetime, timedelta
import logging

from airflow.decorators import dag
from airflow.decorators import task
from airflow.exceptions import AirflowSkipException
from airflow.models import Variable
from airflow.operators.dummy_operator import DummyOperator
from infra_copel.email.send_email import notificacao_erro_airflow


# Log
logger = logging.getLogger('airflow.task')

# Constantes
COLLECTION_PLD = 'pld_horario'
SITE_SHAREPOINT = 'PowerBIInsightsComercializacao'
FOLDER_SHAREPOINT = 'Base de Dados/Dados CCEE'


@dag(schedule_interval='0 2 * * *',
     start_date=datetime(2022, 9, 1),
     catchup=False,
     tags=['CCEE', 'MongoDB', 'SharePoint', 'PLD'],
     default_args={
         "on_failure_callback": notificacao_erro_airflow
     }
     )
def atualizar_pld():
    """DAG de atualização do PLD no banco de dados e no sharepoint."""

    @task
    def verificar_ultima_data():
        """Verifica a última data do banco e retorna a próxima."""
        import pandas as pd
        from infra_copel import MongoHistoricoOficial

        # Tenta buscar a data do documento mais atual na collection
        mdb = MongoHistoricoOficial()
        doc = mdb[COLLECTION_PLD].find_one(projection={'_id': 0,
                                                       'hora': 1},
                                           sort=[('hora', -1)])
        try:
            last_date = doc['hora']
            # Caso a collection não exista ou esteja vazia,
            # define a data inicial dos registros (-1)
        except TypeError:
            last_date = pd.to_datetime("2020/12/31", dayfirst=True)

        # Verifica se a collection está atualizada
        hoje_23h = pd.to_datetime('today').replace(hour=23,
                                                   minute=0,
                                                   second=0,
                                                   microsecond=0)
        if last_date < hoje_23h:
            return (last_date + pd.offsets.Hour()).strftime("%d/%m/%y")

        return False

    @task
    def nada_a_atualizar(next_date):
        """Verifica se está tudo atualizado."""
        if next_date:
            raise AirflowSkipException('Atualizando.')

    @task
    def atualizar_mongodb(next_date):
        """Atualiza o mongodb."""
        from infra_copel import MongoHistoricoOficial
        from dados_ccee.site_ccee.painel_precos.acesso import consulta_site_pld

        if not next_date:
            raise AirflowSkipException('Banco de dados já atualizado.')

        # Faz o download das novas informações
        chromedriver_path = Variable.get('chromedriver_path')
        pld_horario = consulta_site_pld(chromedriver_path,
                                        data_inicial=next_date,
                                        data_final="today")
        pld_horario.reset_index(inplace=True)

        # Insere os dados no mongodb
        mdb = MongoHistoricoOficial()
        mdb[COLLECTION_PLD].insert_many(pld_horario.to_dict("records"))

    @task(trigger_rule='one_success', retries=3, retry_delay=timedelta(minutes=5))
    def atualizar_sharepoint():
        """Atualiza o SharePoint com dados semanais."""
        from infra_copel import SharepointSiteCopel
        from infra_copel import MongoHistoricoOficial
        from infra_copel.sharepoint.errors import NotFoundError

        # Dados
        filename = 'pld_horario.xlsx'

        # Dataframe dos dados do sharepoint
        sp = SharepointSiteCopel(SITE_SHAREPOINT)
        try:
            df_sharepoint = sp.read_df_from_excel(FOLDER_SHAREPOINT, filename)
        except NotFoundError:
            df_sharepoint = False

        # Dataframe dos dados do mongoDB
        mdb = MongoHistoricoOficial()
        df_mongodb = mdb.df_pld_horario.reset_index()
        df_pld_30m = (mdb.df_pld_horario[mdb.df_pld_horario.index >= '2023.04.29']
                         .resample('30T')
                         .ffill()
                         .reset_index()
        )

        # Comparação
        if df_sharepoint is not False:
            if df_mongodb.equals(df_sharepoint):
                raise AirflowSkipException('Já atualizado.')
        # Salva no sharepoint
        sp.write_df_to_excel(df_mongodb, FOLDER_SHAREPOINT, filename)
        sp.write_df_to_excel(df_pld_30m, FOLDER_SHAREPOINT, 'pld_horario_30m.xlsx')

    # Task só para juntar a atualização ou não do mongodb
    mongodb_atualizado = DummyOperator(task_id='mongodb_atualizado',
                                       trigger_rule='one_success')

    # %% Relacionamento entre as tasks
    data_a_atualizar = verificar_ultima_data()
    [atualizar_mongodb(data_a_atualizar),
     nada_a_atualizar(data_a_atualizar)] >> mongodb_atualizado
    mongodb_atualizado >> atualizar_sharepoint()


# %% Criação da DAG
dag = atualizar_pld()
