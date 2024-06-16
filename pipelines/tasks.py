# -*- coding: utf-8 -*-
from io import StringIO
import pandas as pd
from prefect import task
import requests
from requests.exceptions import HTTPError, RequestException
from pipelines.utils import log


global_quantidade_execucoes = 0

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

    url = 'https://dados.mobilidade.rio/gps/brt'

    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json().get('veiculos')
        log("Dados baixados com sucesso!")
        global_quantidade_execucoes += 1

    except RequestException as err:
        log(f'Request error ocurred: {err}')
        data = {'error': err}

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
    df = pd.DataFrame(data)
    log("Dados convertidos em DataFrame com sucesso!")
    return df


@task
def save_report(dataframe: pd.DataFrame) -> None:
    """
    Salva o DataFrame em um arquivo CSV.

    Args:
        dataframe (pd.DataFrame): DataFrame do Pandas.
    """
    global global_quantidade_execucoes

    dataframe.to_csv(f"./data/brt_gps{global_quantidade_execucoes}.csv", index=False)
    log("Dados salvos em report.csv com sucesso!")
