import pandas as pd
from pathlib import Path
import json

import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

path_name = Path(__file__).parent.parent / 'data' / 'weather_data.json'
columns_names_to_drop = ['weather', 'weather_icon', 'sys.type']
columns_names_to_rename = {
        "base": "base",
        "visibility": "visibility",
        "dt": "datetime",
        "timezone": "timezone",
        "id": "city_id", 
        "name": "city_name",
        "cod": "code",
        "coord.lon": "longitude",
        "coord.lat": "latitude",
        "main.temp": "temperature",
        "main.feels_like": "feels_like",
        "main.temp_min": "temp_min",
        "main.temp_max": "temp_max",
        "main.pressure": "pressure",
        "main.humidity": "humidity",
        "main.sea_level": "sea_level",
        "main.grnd_level": "grnd_level",
        "wind.speed": "wind_speed",
        "wind.deg": "wind_deg",
        "wind.gust": "wind_gust",
        "clouds.all": "clouds", 
        "sys.type": "sys_type",                 
        "sys.id": "sys_id",                
        "sys.country": "country",                
        "sys.sunrise": "sunrise",                
        "sys.sunset": "sunset",
    }
columns_to_normalize_datetime = ['datetime', 'sunrise', 'sunset']



def criar_dataframe(path_name:str) -> pd.DataFrame:

    logging.info(f"Criando DF do arquivo JSON: {path_name}")
    path = path_name

    if not path.exists():
        raise FileNotFoundError(f"Arquivo {path} não encontrado.")


    with open(path) as f:
        data = json.load(f)

    df = pd.json_normalize(data)
    logging.info(f"\nDataFrame criado com sucesso. {len(df)} linha(s)")

    return df

def normalizar_colunas_weather(df: pd.DataFrame) -> pd.DataFrame:
    logging.info("Normalizando colunas do DataFrame")

    df_weather = pd.json_normalize(df['weather'].apply(lambda x: x[0]))

    df_weather = df_weather.rename(columns={
        'id': 'weather_id',
        'main': 'weather_main',
        'description': 'weather_description',
        'icon': 'weather_icon'
    })

    df = pd.concat([df, df_weather], axis=1)
    logging.info("Coluna normalizada - {len(df.columns)} colunas")
    return df 

def descartar_colunas(df: pd.DataFrame, columns_names:list[str]) -> pd.DataFrame:

    df = df.drop(columns=columns_names)
    logging.info(f"Colunas descartadas: {columns_names}")

    return df

def renomear_colunas (df: pd.DataFrame, columns_names:dict[str, str]) -> pd.DataFrame:
    logging.info(f"Renomeando {len(columns_names)} colunas")
    df = df.rename(columns=columns_names)
    return df

def normalizar_datetime(df: pd.DataFrame, columns_names:list[str]) -> pd.DataFrame:
    logging.info(f"Convertendo colunas de data/hora: {columns_names}")

    for name in columns_names:
        df[name] = pd.to_datetime(df[name], unit='s', utc=True).dt.tz_convert('America/Sao_Paulo')

    return df


def transformar_dados():
    print("\n Iniciando transformação de dados...")
    df = criar_dataframe(path_name)
    df = normalizar_colunas_weather(df)
    df = descartar_colunas(df, columns_names_to_drop)
    df = renomear_colunas(df, columns_names_to_rename)
    df = normalizar_datetime(df, columns_to_normalize_datetime)

    logging.info(f"Transformação de dados concluída. {len(df)} linha(s")
    return df



