# -*- coding: utf-8 -*-
from prefect import Flow, Parameter
from prefect.run_configs import LocalRun
from prefect.storage import Local

from pipelines.tasks import (
    download_data,
    parse_data,
    save_report,
    load_to_postgres,
    run_dbt
)
from pipelines.schedules import every_minute_schedule
# from pipelines import *


with Flow("EMD: BRT - Ingerir dados da API BRT", schedule=every_minute_schedule) as brt_flow:
    # Tasks
    data = download_data()
    df = parse_data(data)
    save_report(df)
    load_to_postgres(df)
    run_dbt()


# brt_flow.schedule = every_minute_schedule  # atribui o scheduler do flow ao que foi definido no arquivo schedules.py
brt_flow.storage = Local('./data')
brt_flow.run_config = LocalRun()
