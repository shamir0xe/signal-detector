from datetime import datetime
from libs.PythonLibrary.utils import debug_text

class TimeConverter:
    @staticmethod
    def seconds_to_timestamp(seconds: float) -> str:
        return datetime.fromtimestamp(seconds).strftime("%a %y/%m/%d %H:%M:%S")
