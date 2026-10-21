import requests
import json
from pathlib import Path

import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def extrair_dados(url:str) -> list:
    response = requests.get(url)
    data = response.json()

    if response.status_code != 200:
       logging.error("Erro ao extrair dados da API: {response.status_code} - {response.text}")
       return []

    if not data:
        logging.warn("Nenhum dado retornado pela API")
        return []
    
    output_path ='data/weather_data.json'
    output_dir = Path(output_path).parent
    output_dir.mkdir(parents=True, exist_ok=True)

    with open(output_path, 'w') as f:
        json.dump(data, f, indent=4)

    logging.info(f"Dados extraídos e salvos em {output_path}")
    return data


