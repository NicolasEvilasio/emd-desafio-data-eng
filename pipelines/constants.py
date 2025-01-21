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
