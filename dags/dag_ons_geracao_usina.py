# -*- coding: utf-8 -*-
"""DAG utilizada para popular a collection ons_geracao_usinas."""
from datetime import datetime, timedelta
import logging

from airflow.decorators import dag, task
from airflow.exceptions import AirflowSkipException
from infra_copel.email.send_email import notificacao_erro_airflow

# Log
logger = logging.getLogger()

# Sharepoint
SHAREPOINT_SITE = 'PowerBIInsightsComercializacao'
SHAREPOINT_FOLDER = 'Base de Dados/Dados ONS'

# Collections e CKAN
CKAN_PACKAGE = 'geracao-usina-2'
FREQ_DADOS = 'H'
COLLECTION_DADOS = 'ons_geracao_usinas'
SHAREPOINT_FILE = 'geracao_usinas.xlsx'


@dag(schedule_interval='27 8,20 * * *',
     start_date=datetime(2023, 1, 1),
     catchup=False,
     tags=['energia', 'ONS', 'SharePoint', 'MongoDB', 'PowerBI'],
     default_args={
         "on_failure_callback": notificacao_erro_airflow
     })
def ons_geracao_usinas():
    """
    DAG para dados de Geração das Usinas.
    Esses dados são obtidos do site https://dados.ons.org.br

    Dados sendo utilizados em relatório do Jupyter Notebook
    Power BIs relacionados à geração eólica também estão usando essas informações
    """

    @task(
        execution_timeout=timedelta(minutes=59),
        retries=3,
        retry_delay=timedelta(minutes=1),
    )
    def update_collection():

        from dados_ons import OnsDadosAbertos
        from infra_copel import MongoHistoricoOficial
        from lib_local import MongoDadosAbertosUpdate

        mdb_oficial = MongoHistoricoOficial()
        dados_abertos = OnsDadosAbertos()

        mongo_ons_update = MongoDadosAbertosUpdate(mdb_oficial,
                                                   dados_abertos,
                                                   '_dados_abertos_ons')

        updated = mongo_ons_update.update_collection(COLLECTION_DADOS,
                                                     CKAN_PACKAGE,
                                                    )

        if not updated:
            raise AirflowSkipException('Nada modificado.')

    @task(retries=3, retry_delay=timedelta(minutes=5))
    def upload_sharepoint():
        """Coloca no SharePoint o que for necessário."""
        # Importação dentro da task, para não rodar a cada heartbeat
        import pandas as pd

        from infra_copel import MongoHistoricoOficial
        from infra_copel import SharepointSiteCopel

        # Conexão com o banco
        mdb = MongoHistoricoOficial()


        ano_corrente = datetime.now().year
        mes_pesquisa_limite = datetime.now().month - 1 if datetime.now().month > 1 else 1
        # Consulta ao banco
        # Limitando a consulta no banco de dados devido a limitação do excel: uma planilha não pode ter mais de 1.048.576 linhas
        docs = mdb[COLLECTION_DADOS].find(
            filter={'periodo': {'$gte': datetime(ano_corrente, mes_pesquisa_limite, 1)}},
            projection={'_id': 0},
            sort=[('periodo', 1)],
            )

        # Transforma em DataFrame
        df = pd.DataFrame(docs)
        df['periodo'] = pd.PeriodIndex(df['periodo'], freq=FREQ_DADOS)

        # Salva no sharepoint
        sp = SharepointSiteCopel(SHAREPOINT_SITE)
        sp.write_df_to_excel(df, SHAREPOINT_FOLDER, SHAREPOINT_FILE)

    # %% Relacionamento entre as tasks
    update_collection() >> upload_sharepoint()

# %% Criação da DAG
dag = ons_geracao_usinas()
