from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str
    openai_api_key: str
    openai_model: str = "gpt-4o"
    teacher_user_id: str = "seed_teacher_id"

    class Config:
        env_file = ".env"


settings = Settings()
