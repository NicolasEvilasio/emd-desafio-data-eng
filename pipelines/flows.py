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


with Flow(
    name="EMD: BRT - Ingerir dados da API BRT", 
    schedule=every_minute_schedule,
    # run_config=LocalRun(labels=["brt-flow"]),
    storage=Local('./data')
) as brt_flow:
    # Tasks
    data = download_data()
    
    df = parse_data(data)
    df.set_upstream(data)
    
    task_save_report = save_report(df)
    task_save_report.set_upstream(df)
    
    task_load_to_postgres = load_to_postgres(df)
    task_load_to_postgres.set_upstream(task_save_report)
    
    task_run_dbt = run_dbt()
    task_run_dbt.set_upstream(task_load_to_postgres)