# -*- coding: utf-8 -*-
from genericpath import exists
import os
import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError
import psycopg2
from prefect import task
from prefect.engine.runner import ENDRUN
from prefect.engine.state import Skipped
# from prefect.engine.signals import SKIP
import requests
from requests.exceptions import RequestException
from pipelines.constants import constants
from pipelines.utils import log
from datetime import datetime, timedelta
import pytz
import subprocess
from pipelines.utils import (
    redis_h_set, 
    redis_h_get, 
)
from pathlib import Path

global_quantidade_execucoes = 0
global_df = pd.DataFrame()
timezone = pytz.timezone("America/Sao_Paulo")


@task
def download_data() -> list[dict]:
    """
    Baixa dados da API https://dados.mobilidade.rio/gps/brt e retorna uma lista de dicionários com os dados.

    Returns:
        list[dict]: Uma lista com dicionários contendo os dados da API.

    Exemplo de retorno bem-sucedido:
        [{
            "codigo": "XXXXXX",
            "placa": "YYYYYY",
            "linha": "ZZZZZZ",
            "latitude": -00.000000,
            "longitude": -00.000000,
            "dataHora": 1234567890123,
            "velocidade": 0,
            "id_migracao_trajeto": "AAAAAA",
            "sentido": "BBBBBB",
            "trajeto": "CCCCCC",
            "hodometro": 12345.6,
            "direcao": "DDDDDD"
        },
        ...]
    """
    global global_quantidade_execucoes

    url = "https://dados.mobilidade.rio/gps/brt"

    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json().get("veiculos")
        log("Dados baixados com sucesso!")

    except RequestException as err:
        log(f"Request error ocurred: {err}")
        data = {"error": err}

    return data


@task
def parse_data(data: list[dict]) -> pd.DataFrame:
    """
    Cria um DataFrame do Pandas a partir de um dict, para facilitar sua manipulação.

    Args:
        data (dict): texto em formato CSV.

    Returns:
        pd.DataFrame: DataFrame do Pandas.
    """
    global global_df

    df = pd.DataFrame(data)
    global_df = pd.concat([global_df, df], ignore_index=True)

    log("Dados convertidos em DataFrame com sucesso!")
    return global_df


@task
def save_report(dataframe: pd.DataFrame, batch_minutes_interval: int=10) -> None:
    """
    Salva o DataFrame em um arquivo CSV.

    Args:
        dataframe (pd.DataFrame): DataFrame do Pandas.
    """
    redis_last_date = redis_h_get(
        name=constants.REDIS_BRT_GPS_NAME.value, 
        key=constants.REDIS_BRT_GPS_KEY_LAST_FILE_TIMESTAMP_CREATED.value
    )
    
    current_timestamp = datetime.now(pytz.utc)  # Obter data e hora atual em UTC para nomear o arquivo
    
    if redis_last_date is None or str(current_timestamp - timedelta(minutes=batch_minutes_interval)) > redis_last_date:
        current_timestamp_str = current_timestamp.strftime("%Y%m%d_%H%M")
        file_name = f"brt_gps_{current_timestamp_str}.csv"
        
        dataframe.to_csv(Path.cwd() / "data" / file_name, index=False, mode="w")
        log(f"Dados salvos em {file_name} com sucesso!")
        
        # reseta o timestamp do último arquivo salvo
        redis_h_set(
            name=constants.REDIS_BRT_GPS_NAME.value, 
            values={
                constants.REDIS_BRT_GPS_KEY_LAST_FILE_TIMESTAMP_CREATED.value: str(current_timestamp)
            }
        )
        
        if not redis_last_date:
            minutes_passed = 1
        
            log_msg = f"Coletando dados para carregar no PostgreSQL - {minutes_passed} / {batch_minutes_interval} min"
            log(log_msg)
            skip = Skipped(message=log_msg)
            raise ENDRUN(state=skip)
            
        else:
            minutes_passed = round((current_timestamp - datetime.fromisoformat(redis_last_date)).total_seconds() / 60)
            log_msg = f"Dados suficientes coletados para carregar no PostgreSQL - {minutes_passed} / {batch_minutes_interval} min"
            log(log_msg)
            
    else:
        redis_last_date_datetime = datetime.strptime(redis_last_date, "%Y-%m-%d %H:%M:%S.%f%z")
        redis_last_date_str = redis_last_date_datetime.strftime("%Y%m%d_%H%M")
        file_name = f"brt_gps_{redis_last_date_str}.csv"
        
        if exists(Path.cwd() / "data" / file_name):
            dataframe.to_csv(Path.cwd() / "data" / file_name, index=False, header=False, mode="a")
        else:
            dataframe.to_csv(Path.cwd() / "data" / file_name, index=False, mode="w")
        
        log(f"Dados salvos em {file_name} com sucesso!")
    
        minutes_passed = round((current_timestamp - datetime.fromisoformat(redis_last_date)).total_seconds() / 60)
               
        log_msg = f"Coletando dados para carregar no PostgreSQL - {minutes_passed} / {batch_minutes_interval} min"
        log(log_msg)
        
        skip = Skipped(message=log_msg)
        raise ENDRUN(state=skip)
      
        
@task
def load_to_postgres(dataframe: pd.DataFrame) -> None:
    """
    Carrega os dados de um pandas.DataFrame em um PostgreSQL database.

    Args:
        dataframe: parse_data(data)
    """
    global global_quantidade_execucoes
    load_dotenv()

    try:
        # Parâmetros de conexão com o PostgreSQL
        db_host = os.getenv('DB_HOST')
        db_port = os.getenv('DB_PORT')
        db_database = os.getenv('DB_DATABASE')
        db_user = os.getenv('DB_USER')
        db_password = os.getenv('DB_PASSWORD')

        # Testar conexão antes de prosseguir
        test_conn = psycopg2.connect(
            host=db_host,
            port=db_port,
            database=db_database,
            user=db_user,
            password=db_password
        )
        log("Conexão com o PostgreSQL estabelecida com sucesso!")
        test_conn.close()
        
        # Criar uma conexão com o PostgreSQL usando SQLAlchemy
        engine = create_engine(f'postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_database}')

        # Nome da tabela no PostgreSQL
        table_name = "brt_data"

        # Inserir dados no PostgreSQL usando df.to_sql()
        dataframe.to_sql(table_name, con=engine, schema='bronze', if_exists='append', index=False)

        log('Dados carregados no PostgreSQL.')


    except KeyError as e:
        # Capturar falha na definição de alguma variável de ambiente
        raise ValueError(f"Erro ao interagir com o PostgreSQL: {e}")

    except SQLAlchemyError as e:
        # Se ocorrer um erro de SQLAlchemy ao conectar ou inserir dados
        raise RuntimeError(f"Erro ao interagir com o PostgreSQL: {e}")

    except Exception as e:
        # Para outros erros não especificados
        raise RuntimeError(f"Erro inesperado ao carregar dados para PostgreSQL: {e}")


@task
def run_dbt() -> str:
    """
    Executa o DBT no diretório do projeto DBT e retorna a saída padrão.

    Esta tarefa muda para o diretório 'dbt_brt', executa o comando 'dbt run',
    e então retorna ao diretório original. A saída padrão do comando 'dbt run'
    é capturada e retornada como uma string.

    Returns:
        str: A saída padrão do comando 'dbt run'.

    Exemplo:
         run_dbt()
        'Running with dbt=0.18.1\n...\nDone.'
    """
    # Salvar o diretório raíz do projeto
    current_dir = os.getcwd()

    # Alterar para a pasta do dbt
    os.chdir('dbt_brt')

    # Executar o comando dbt run
    result = subprocess.run(["dbt", "run", "--target", "gold", "--select", "gold"], capture_output=True, text=True)

    # Retornar para a pasta raíz do projeto
    os.chdir(current_dir)

    return result.stdout
