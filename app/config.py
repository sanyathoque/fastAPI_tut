from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


# Central app configuration. Pydantic reads these values from environment
# variables first, then falls back to the defaults below.
class Settings(BaseSettings):
    # These class variables become settings you can access later, like:
    # settings.app_name, settings.app_env, and settings.database_url.
    app_name: str = "FastAPI SQLAlchemy API"
    app_env: str = "development"

    # SQLite database file. The three slashes are part of SQLAlchemy's URL style.
    database_url: str = "sqlite:///./app.db"

    # React dev servers commonly run on ports 3000 or 5173. These origins are
    # allowed to call the API from a browser.
    backend_cors_origins: str = Field(
        default="http://localhost:3000,http://localhost:5173"
    )

    # .env lets you configure the app locally without changing source code.
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @property
    def cors_origins(self) -> list[str]:
        # @property makes this act like a variable:
        # settings.cors_origins instead of settings.cors_origins().
        #
        # backend_cors_origins is stored as one comma-separated string:
        # "http://localhost:3000,http://localhost:5173"
        #
        # FastAPI's CORS middleware needs a real Python list:
        # ["http://localhost:3000", "http://localhost:5173"]
        return [
            # strip() removes accidental spaces around each URL.
            origin.strip()
            # split(",") breaks the string into pieces at every comma.
            for origin in self.backend_cors_origins.split(",")
            # This skips empty pieces, for example if there is a double comma.
            if origin.strip()
        ]


@lru_cache
def get_settings() -> Settings:
    # @lru_cache remembers the first Settings() object it creates.
    # Every later call returns the same object instead of reading .env again.
    return Settings()
