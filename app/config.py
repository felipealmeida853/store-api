from pydantic import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str
    MONGO_INITDB_DATABASE: str

    BUCKET_SERVICE_NAME: str
    BUCKET_REGION: str
    BUCKET_ACCESS_KEY_ID: str
    BUCKET_SECRET_ACCESS_KEY: str
    BUCKET_ENDPOINT_URL: str
    BUCKET_NAME: str
    JWT_SECRET: str
    JWT_ALGORITHM: str
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int

    class Config:
        env_file = "../.env"


settings = Settings()
