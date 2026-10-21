from sqlalchemy import create_engine, text
from urllib.parse import quote_plus
import os 
from pathlib import Path
import pandas as pd
from dotenv import load_dotenv

import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

env_path = Path(__file__).resolve().parent.parent / 'config' / '.env'
load_dotenv(env_path)

user = os.getenv('user')
password = os.getenv('password')
database = os.getenv('database')
host = 'localhost'
#host = 'host.docker.internal'

def get_connection():
    logging.info("Criando conexão em {host}:5432/{database}")
    return create_engine(f"postgresql+psycopg2://{user}:{quote_plus(password)}@{host}:5432/{database}")

engine = get_connection()

def carregar_dados (table_name: str, df): 
    df.to_sql(
        name=table_name,
        con=engine,
        if_exists='append',
        index=False
    )
    logging.info(f"Dados carregados com sucesso na tabela {table_name}. {len(df)} linha(s) inserida(s)")
    df_check = pd.read_sql(f'SELECT * FROM {table_name}', con=engine)
    logging.info(f"Verificação: {len(df_check)} linha(s) na tabela {table_name}")