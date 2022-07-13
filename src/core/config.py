import os
from logging import config as logging_config
from pathlib import Path

from pydantic import BaseSettings

from src.core.logger import LOGGING

logging_config.dictConfig(LOGGING)

BASE_DIR = Path(__file__).resolve().parent


class Settings(BaseSettings):
    PROJECT_NAME: str = 'movies'
    REDIS_HOST: str = '127.0.0.1'
    REDIS_PORT: str = '6379'
    ELASTIC_HOST: str = '127.0.0.1'
    ELASTIC_PORT: str = '9200'

    class Config:
        env_file = os.path.join(BASE_DIR, '.env')
        env_file_encoding = 'utf-8'


settings = Settings()
