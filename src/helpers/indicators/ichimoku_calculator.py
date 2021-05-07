from typing import Any, Dict, List

from src.models.candle import Candle
import ta
import pandas as pd
from libs.PythonLibrary.utils import debug_text

class IchimokuCalculator:
    def __init__(self, data: List[Candle], config: Dict) -> None:
        self.data = data
        self.config = config

    def calculate(self) -> List[Dict]:
        res = {}
        ichimoku = ta.trend.IchimokuIndicator(
            high = pd.Series([float(candle.highest) for candle in self.data]),
            low = pd.Series([float(candle.lowest) for candle in self.data]),
            window1 = self.config.get('window1'),
            window2 = self.config.get('window2'),
            window3 = self.config.get('window3'),
        )
        res['cloud-green'] = ichimoku.ichimoku_a().to_numpy().tolist()
        # debug_text('green: %', res['cloud-green'])
        res['cloud-red'] = ichimoku.ichimoku_b().to_numpy().tolist()
        res['cloud-top'] = [max(res['cloud-red'][i], res['cloud-green'][i]) for i in range(len(res['cloud-red']))]
        res['cloud-bottom'] = [min(res['cloud-red'][i], res['cloud-green'][i]) for i in range(len(res['cloud-red']))]
        res['conversion'] = ichimoku.ichimoku_conversion_line().to_numpy().tolist()
        # debug_text('conversion: %', ichimoku.ichimoku_conversion_line())
        res['base'] = ichimoku.ichimoku_base_line().to_numpy().tolist()
        # for item in [*res]:
        #     debug_text('item[%] = % %', item, len(res[item]), res[item])
        array = []
        for i in range(len(res['cloud-red'])):
            array.append({
                'cloud-red': res['cloud-red'][i],
                'cloud-green': res['cloud-green'][i],
                'cloud-top': res['cloud-top'][i],
                'cloud-bottom': res['cloud-bottom'][i],
                'conversion': res['conversion'][i],
                'base': res['base'][i],
            })
        return array
