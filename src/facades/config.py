from typing import Any
from src.helpers.config.config_reader import ConfigReader

class Config:
    @staticmethod
    def get(selector: str, default: Any = None) -> Any:
        return ConfigReader().get(selector=selector, default=default)


