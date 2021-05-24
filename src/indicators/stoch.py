from typing import Any, Dict, List

from .indicator_abstract import Indicator
from src.models.signal import Signal
from src.models.candle import Candle
from src.models.signal_types import SignalTypes
from libs.PythonLibrary.utils import debug_text
from src.helpers.indicators.stoch_calculator import StochCalculator
from src.helpers.chart.overbought_calculator import OverBoughtCalculator
from src.helpers.chart.oversold_calculator import OverSoldCalculator
from src.helpers.config.config_reader import ConfigReader
from src.helpers.chart.atr_calculator import ATRCalculator
from src.facades.config import Config


class Stoch(Indicator):
    def __init__(self, data: List[Candle]) -> None:
        self.name = 'stoch'
        self.data = data
        self.config = self.__read_config()

    def __read_config(self) -> Dict:
        return ConfigReader()
    
    def get_signals(self) -> List[Signal]:
        signals = self.__calculate_signals()
        signals = self.__add_limits(signals)
        return signals

    def __calculate_signals(self):
        res = []
        stoch = StochCalculator(self.data, self.config).calculate()

        up_threshold = self.config.get('indicators.stoch.upperbound_threshold')
        # res = [*res, *self.__short_signals(stoch, up_threshold)]

        lo_threshold = self.config.get('indicators.stoch.lowerbound_threshold')
        res = [*res, *self.__long_signals(stoch, lo_threshold)]
        return res

    def __add_limits(self, fresh_signals: List[Signal]):
        signals = []
        for signal in fresh_signals:
            if signal.type is SignalTypes.LONG:
                delta = ATRCalculator(self.data[:signal.index + 1], {
                    'window': self.config.get('indicators.stoch.stoploss.window'),
                }).do()[-1] * self.config.get('indicators.stoch.stoploss.multiplier')
                signal.stop_loss = self.data[signal.index].lowest - delta
                signal.take_profit = self.data[signal.index].closing + delta * self.config.get('indicators.stoch.take-profit.multiplier')
                signals.append(signal)
        return signals
    
    def __short_signals(self, stoch: Any, threshold: float) -> List[Signal]:
        res = []
        over_boughts = OverBoughtCalculator().calculate(stoch, threshold=threshold, config=self.config)
        for region in over_boughts:
            index = region[-1]
            # if index >= len(self.data):
                # continue
            res.append(Signal(
                self.name, 
                SignalTypes.SHORT,
                self.data[index],
                index
            ))
        return res

    def __long_signals(self, stoch: Any, threshold: float) -> List[Signal]:
        res = []
        over_boughts = OverSoldCalculator().calculate(stoch, threshold=threshold, config=self.config)
        for region in over_boughts:
            index = region[-1]
            res.append(Signal(
                self.name, 
                SignalTypes.LONG,
                self.data[index],
                index
            ))
        return res

