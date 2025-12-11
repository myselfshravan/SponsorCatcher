"""Configuration loading and validation."""

from dataclasses import dataclass
from pathlib import Path
import os

from dotenv import load_dotenv


@dataclass(frozen=True)
class Config:
    """Immutable configuration container for speed and safety."""

    email: str
    password: str
    login_url: str
    sponsor_url: str
    implicit_wait: float

    @classmethod
    def load(cls, env_path: Path | None = None) -> "Config":
        """Load configuration from .env file.

        Args:
            env_path: Optional path to .env file. Defaults to .env in current directory.

        Returns:
            Config instance with loaded values.

        Raises:
            KeyError: If required environment variables are missing.
        """
        if env_path:
            load_dotenv(env_path)
        else:
            load_dotenv()

        email = os.environ.get("SPONSOR_EMAIL")
        password = os.environ.get("SPONSOR_PASSWORD")

        if not email or not password:
            raise KeyError(
                "Missing required environment variables: SPONSOR_EMAIL and SPONSOR_PASSWORD. "
                "Please copy .env.example to .env and fill in your credentials."
            )

        return cls(
            email=email,
            password=password,
            login_url=os.getenv(
                "LOGIN_URL",
                "https://members.manufacturedhousing.org/account/login.aspx",
            ),
            sponsor_url=os.getenv(
                "SPONSOR_URL",
                "https://members.manufacturedhousing.org/sponsorships/become-a-sponsor",
            ),
            implicit_wait=float(os.getenv("IMPLICIT_WAIT", "0.5")),
        )
