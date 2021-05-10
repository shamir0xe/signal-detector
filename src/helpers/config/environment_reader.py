import os
from typing import Any
from libs.PythonLibrary.utils import debug_text
from libs.PythonLibrary.Helpers.json_helper import JsonHelper
from libs.PythonLibrary.files import File

class EnvironmentReader:
    def __init__(self, sub_path: str = '') -> None:
        self.sub_path = sub_path
        if sub_path != '':
            self.sub_path = sub_path + '.'
        self.json = File.read_json(os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..', 'env.json')))
    
    def get(self, selector: str, default: Any = None) -> Any:
        value = JsonHelper.selector_get_value(self.json, self.sub_path + selector)
        if value != {}:
            return value
        return default

