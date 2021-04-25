from typing import List
import json

from ..models.candle import Candle


class ArgumentDataAdapter:
    @staticmethod
    def translate(data: str) -> List[Candle]:
        data = json.loads(data)
        data = data['data']
        res = []
        for candle_data in data:
            res.append(Candle(*candle_data))
        return res
