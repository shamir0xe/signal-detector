from typing import Any, Dict, List

from libs.PythonLibrary.utils import debug_text

from .indicator_abstract import Indicator
from src.models.signal import Signal
from src.models.candle import Candle
from src.models.signal_types import SignalTypes
from src.helpers.indicators.rsi_calculator import RsiCalculator
from src.helpers.chart.overbought_calculator import OverBoughtCalculator
from src.helpers.chart.oversold_calculator import OverSoldCalculator
from src.helpers.config.config_reader import ConfigReader


class Rsi(Indicator):
    def __init__(self, data: List[Candle]) -> None:
        self.name = 'rsi'
        self.data = data
        self.config = self.__read_config()

    def __read_config(self) -> Dict:
        return ConfigReader('indicators.rsi')
    
    def get_signals(self) -> List[Signal]:
        res = []
        rsi = RsiCalculator(self.data, self.config).calculate()

        up_threshold = self.config.get('upperbound_threshold')
        res = [*res, *self.__short_signals(rsi, up_threshold)]

        lo_threshold = self.config.get('lowerbound_threshold')
        res = [*res, *self.__long_signals(rsi, lo_threshold)]
        return res
    
    def __short_signals(self, rsi: Any, threshold: float) -> List[Signal]:
        res = []
        over_boughts = OverBoughtCalculator().calculate(rsi, threshold=threshold, config=self.config)
        for region in over_boughts:
            for index in region[-1:]:
                res.append(Signal(
                    name = self.name, 
                    type = SignalTypes.SHORT,
                    candle = self.data[index],
                    index = index
                ))
        return res

    def __long_signals(self, rsi: Any, threshold: float) -> List[Signal]:
        res = []
        over_boughts = OverSoldCalculator().calculate(rsi, threshold=threshold, config=self.config)
        for region in over_boughts:
            for index in region[-1:]:
                res.append(Signal(
                    name = self.name, 
                    type = SignalTypes.LONG,
                    candle = self.data[index],
                    index = index
                ))
        return res
