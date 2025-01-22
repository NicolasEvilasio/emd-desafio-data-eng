# -*- coding: utf-8 -*-
from enum import Enum


class constants(Enum):  # pylint: disable=c0103
    """
    Constant values
    """

    PATH_BASE_DADOS = "/data/brt_gps.csv"
    DATASET_ID = "emd-desafio-data-eng"
    TABLE_ID = "brt_dados_gps"

    EMD_DESAFIO_AGENT_LABEL = 'brt-flow'
    
    ### REDIS ###
    REDIS_BRT_GPS_NAME = 'redis_brt_gps'
    REDIS_BRT_GPS_KEY_EXECUTIONS_QUANTITY = 'executions_quantity'
    REDIS_BRT_GPS_KEY_LAST_FILE_TIMESTAMP_CREATED = 'last_file_timestamp_created'
    