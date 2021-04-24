from libs.PythonLibrary.utils import debug_text
import os
from typing import Any
from libs.PythonLibrary.Helpers.json_helper import JsonHelper
from libs.PythonLibrary.files import File

class ConfigReader:
    def __init__(self, sub_path: str = '') -> None:
        self.sub_path = sub_path
        # debug_text(os.path.join('..', '..', '..', 'config', 'config.json'))
        self.json = File.read_json(os.path.join('.', '.', '.', 'config', 'config.json'))
    
    def get(self, selector: str, default: Any = None) -> Any:
        value = JsonHelper.selector_get_value(self.json, self.sub_path + '.' + selector)
        if value != {}:
            return value
        return default
