from pydantic import BaseModel, BaseSettings


class Settings(BaseSettings):
    psql_dbname: str = "movies_database"
    psql_user: str = "app"
    psql_password: str = "123qwe"
    psql_host: str = "127.0.0.1"
    psql_port: str = "5432"
    file_path: str = "etl_state.json"
