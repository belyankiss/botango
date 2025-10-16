from jinja2 import Template

from botango.schemas.template_class import ManagerTemplate
from .enviroment_jinja import ENV

SETTINGS_TEMPLATE = ENV.from_string("""from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    BOT_TOKEN: str
    {% if mode.type == 'webhook' %}
    WEBHOOK_URL: str
    WEBHOOK_PORT: int
    WEBHOOK_PATH: str
    WEBHOOK_SECRET: str
    {% endif %}
    {% if database.name == 'postgresql' %}
    POSTGRES_HOST: str
    POSTGRES_PORT: int
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_NAME: str
    DEBUG: bool
    {% endif %}
    {% if database.name == 'aiosqlite' %}
    NAME_DATABASE: str
    DEBUG: bool
    {% endif %}
    
    @property
    def url_database(self) -> str:
        {% if database.name == 'postgresql' %}
        return (f"postgresql+asyncpg://
                {self.POSTGRES_USER}:
                {self.POSTGRES_PASSWORD}@
                {self.POSTGRES_HOST}:
                {self.POSTGRES_PORT}/
                {self.POSTGRES_NAME}")
        {% endif %}
        {% if database.name == 'aiosqlite' %}
        return f"sqlite+aiosqlite:///./{self.NAME_DATABASE}"
        {% endif %}
        
    @property
    def debug(self) -> bool:
        return self.DEBUG
    
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")
    
settings = Settings()
""")

class SettingsTemplate(ManagerTemplate):
    filename: str = "settings.py"
    template: Template = SETTINGS_TEMPLATE