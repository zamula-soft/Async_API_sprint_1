import os
from logging import config as logging_config

from pydantic import BaseSettings

from core.logger import LOGGING


class Settings(BaseSettings):
    PROJECT_NAME: str
    REDIS_HOST: str
    REDIS_PORT: str
    ELASTIC_HOST: str
    ELASTIC_PORT: str
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    class Config:
        env_file = '.env'
        env_file_encoding = 'utf-8'


settings = Settings()

logging_config.dictConfig(LOGGING)
