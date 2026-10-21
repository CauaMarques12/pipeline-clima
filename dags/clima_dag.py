from datetime import datetime, timedelta
from airflow.decorators import dag, task
from pathlib import Path
import sys, os

sys.path.insert(0, '/opt/airflow/src')

from dotenv import load_dotenv
from extract_data import extrair_dados
from load_data import carregar_dados
from transform_data import transformar_dados

env_path = Path(__file__).resolve().parent.parent / 'config' / '.env'
load_dotenv(env_path)

API_KEY = os.getenv('api_key')
url = f'https://api.openweathermap.org/data/2.5/weather?q=Ipatinga,BR&units=metric&appid={API_KEY}'


@dag(
    dag_id='clima_dag',
    default_args={
        'owner': 'airflow',
        'depends_on_past': False,
        'retries': 2,
        'retry_delay': timedelta(minutes=5),
    },
    description='ETL - clima ipatinga',
    schedule= '0 */1 * * *',  
    start_date=datetime(2026, 10, 20),
    catchup=False,
    tags=['clima', 'ipatinga'],
)

def clima_pipeline ():

    @task
    def extract():
        extrair_dados(url)

    @task
    def transform():
        df = transformar_dados()
        df.to_parquet('/opt/airflow/data/temp_data.parquet', index=False)

    @task
    def load():
        import pandas as pd
        df = pd.read_parquet('/opt/airflow/data/temp_data.parquet')
        carregar_dados('mg_clima', df)

    
    extract() >> transform() >> load()

clima_pipeline()