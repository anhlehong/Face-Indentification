from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DB_URL: str
    FACE_MATCH_THRESHOLD: float
    MODEL_NAME: str

    CTX_ID: int
    DET_SIZE: int

    EMBEDDING_DIM: int = 512
    DB_MIN_CONN: int = 1
    DB_MAX_CONN: int = 10

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore"
    )


settings = Settings()
