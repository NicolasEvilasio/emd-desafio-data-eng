# -*- coding: utf-8 -*-
import os
from io import StringIO
import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError
import psycopg2
from prefect import task
from prefect.engine.signals import SKIP
import requests
from requests.exceptions import RequestException
from pipelines.utils import log
from datetime import datetime
import pytz
import subprocess


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
        global_quantidade_execucoes += 1

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
def save_report(dataframe: pd.DataFrame) -> None:
    """
    Salva o DataFrame em um arquivo CSV.

    Args:
        dataframe (pd.DataFrame): DataFrame do Pandas.
    """
    global global_quantidade_execucoes

    if global_quantidade_execucoes >= 10:
        timestamp = datetime.now(timezone).strftime("%Y%m%d%H%M")  # Obter data e hora atual para nomear o arquivo
        dataframe.to_csv(f"./data/brt_gps_{timestamp}.csv", index=False)
        log("Dados salvos em report.csv com sucesso!")
        # global_quantidade_execucoes = 0
    else:
        log(f"Coletando dados para formar o CSV - {global_quantidade_execucoes} / 10")
        raise SKIP("Pulando tarefa: condição específica não atendida")


@task
def load_to_postgres(dataframe: pd.DataFrame) -> None:
    """
    Carrega os dados de um pandas.DataFrame em um PostgreSQL database.

    Args:
        dataframe: parse_data(data)
    """
    global global_quantidade_execucoes
    load_dotenv()

    if global_quantidade_execucoes >= 10:
        try:
            # Parâmetros de conexão com o PostgreSQL
            db_host = os.getenv('DB_HOST')
            db_port = os.getenv('DB_PORT')
            db_database = os.getenv('DB_DATABASE')
            db_user = os.getenv('DB_USER')
            db_password = os.getenv('DB_PASSWORD')

            # Criar uma conexão com o PostgreSQL usando SQLAlchemy
            engine = create_engine(f'postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_database}')

            # Nome da tabela no PostgreSQL
            table_name = "brt_data"

            # Inserir dados no PostgreSQL usando df.to_sql()
            dataframe.to_sql(table_name, engine, if_exists='append', index=False)

            log('Dados carregados no PostgreSQL.')

            global_quantidade_execucoes = 0 # resetar a contagem

        except KeyError as e:
            # Capturar falha na definição de alguma variável de ambiente
            raise ValueError(f"Erro ao interagir com o PostgreSQL: {e}")

        except SQLAlchemyError as e:
            # Se ocorrer um erro de SQLAlchemy ao conectar ou inserir dados
            raise RuntimeError(f"Erro ao interagir com o PostgreSQL: {e}")

        except Exception as e:
            # Para outros erros não especificados
            raise RuntimeError(f"Erro inesperado ao carregar dados para PostgreSQL: {e}")
    else:
        log(f"Coletando dados para formar o CSV - {global_quantidade_execucoes} / 10")
        raise SKIP("Pulando tarefa: condição específica não atendida")


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
    global global_quantidade_execucoes

    if global_quantidade_execucoes >= 10:
        # Salvar o diretório raíz do projeto
        current_dir = os.getcwd()

        # Alterar para a pasta do dbt
        os.chdir('dbt_brt')

        # Executar o comando dbt run
        result = subprocess.run(["dbt", "run"], capture_output=True, text=True)

        # Retornar para a pasta raíz do projeto
        os.chdir(current_dir)

        return result.stdout
    else:
        log(f"Coletando dados para formar o CSV - {global_quantidade_execucoes} / 10")
        raise SKIP("Pulando tarefa: condição específica não atendida")
