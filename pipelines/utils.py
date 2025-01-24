# -*- coding: utf-8 -*-
import os
import prefect
import redis

def log(message) -> None:
    """Logs a message"""
    prefect.context.logger.info(f"\n{message}")


def get_redis_client(
    host: str,
    port: int,
    username: str,
    password: str,
    decode_responses: bool=True
) -> redis.Redis:
    return redis.Redis(
        host=host,
        port=port,
        decode_responses=decode_responses,
        username=username,
        password=password,
    )
    
def redis_h_set(name: str, values: dict[str, any], client: redis.Redis = None) -> None:
    if client is None:
        client = get_redis_client(
            host=os.getenv('REDIS_HOST'),
            port=os.getenv('REDIS_PORT'),
            username=os.getenv('REDIS_USERNAME'),
            password=os.getenv('REDIS_PASSWORD')
        )
    client.hset(
        name=name, 
        mapping=values
    )

def redis_h_get(
    name: str, 
    key: str,
    client: redis.Redis = None
) -> any:
    if client is None:
        client = get_redis_client(
            host=os.getenv('REDIS_HOST'),
            port=os.getenv('REDIS_PORT'),
            username=os.getenv('REDIS_USERNAME'),
            password=os.getenv('REDIS_PASSWORD'),
        )
    return client.hget(name=name, key=key)

def redis_h_get_all(
    name: str,
    client: redis.Redis = None
) -> dict[str, any]:
    if client is None:
        client = get_redis_client(
            host=os.getenv('REDIS_HOST'),
            port=os.getenv('REDIS_PORT'),
            username=os.getenv('REDIS_USERNAME'),
            password=os.getenv('REDIS_PASSWORD'),
        )
    return client.hgetall(name=name)
