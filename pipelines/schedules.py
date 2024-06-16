# -*- coding: utf-8 -*-
"""
Schedules for the database dump pipeline
"""
from prefect.schedules import Schedule
from prefect.schedules.clocks import IntervalClock
from datetime import timedelta
import pendulum
from pipelines.constants import constants


# Definir o intervalo de 1 minuto para o agendamento
every_minute_schedule = Schedule(
    clocks=[
        IntervalClock(
            interval=timedelta(minutes=1), # definindo o flow para executar a cada 1 minuto
            start_date=pendulum.datetime(2024, 6, 16, 18, 35, 0,
                                         tz="America/Sao_Paulo"),
            labels=[
                # definir qual agent o flow deve usar
                constants.EMD_DESAFIO_AGENT_LABEL.value
            ],
            parameter_defaults={
                'materialize_after_dum': True,
                'materialization_mode': 'dev',
            },
        )
    ]
)
