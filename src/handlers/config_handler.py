import os
from typing import Dict, List, Optional
from libs.PythonLibrary.files import File


class Config:
    def __init__(self) -> None:
        self.path = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'config', 'config.json'))
        self.config = {}

    def read(self) -> Dict:
        self.config = File.read_json(self.path)
        return self.config

    def available_configs(self) -> List[str]:
        return [*self.config]

    def get(self, attribute: str) -> Optional[str]:
        return self.config.get(attribute)
