from src.extract_data import extrair_dados
from src.load_data import carregar_dados
from src.transform_data import transformar_dados

import os
from pathlib import Path
from dotenv import load_dotenv

import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

env_path = Path(__file__).resolve().parent.parent / 'config' / '.env'
load_dotenv(env_path)

API_KEY = os.getenv('api_key')

url = f'https://api.openweathermap.org/data/2.5/weather?q=Ipatinga,BR&units=metric&appid={API_KEY}'
table_name = 'mg_clima'

def pipeline():
     try:
         logging.info("ETAPA 1: EXTRACT")
         extrair_dados(url)
       
         logging.info("ETAPA 2: TRANSFORM")
         df = transformar_dados()
       
         logging.info("ETAPA 3: LOAD")
         carregar_dados(table_name, df)
       
         print("\n" + "="*60)
         print("Pipeline concluído com sucesso!")
         print("="*60)
       
     except Exception as e:
         logging.error(f"ERRO no Pipeline: {e}")
         import traceback
         traceback.print_exc()
   
pipeline()
