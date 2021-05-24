from typing import Any, Dict, List
from src.adapters.interval_adapter import IntervalAdapter

from libs.PythonLibrary.utils import debug_text

from .indicator_abstract import Indicator
from src.models.signal import Signal
from src.models.candle import Candle
from src.models.signal_types import SignalTypes
from src.helpers.indicators.rsi_calculator import RsiCalculator
from src.helpers.chart.overbought_calculator import OverBoughtCalculator
from src.helpers.chart.oversold_calculator import OverSoldCalculator
from src.helpers.config.config_reader import ConfigReader
from src.helpers.chart.atr_calculator import ATRCalculator
from src.facades.config import Config
from src.helpers.chart.ema_calculator import EmaCalculator

class Rsi(Indicator):
    def __init__(self, data: List[Candle]) -> None:
        self.name = 'rsi'
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
        rsi = RsiCalculator(self.data, self.config).calculate()

        up_threshold = self.config.get('indicators.rsi.upperbound_threshold')
        # res = [*res, *self.__short_signals(rsi, up_threshold)]

        lo_threshold = self.config.get('indicators.rsi.lowerbound_threshold')
        res = [*res, *self.__long_signals(rsi, lo_threshold)]
        return res

    def __add_limits(self, fresh_signals: List[Signal]):
        signals = []
        for signal in fresh_signals:
            if signal.type is SignalTypes.LONG:
                # sl = IntervalDivider.do(
                #     start=self.lines[signal.index]['base'],
                #     end=self.lines[signal.index - self.medium_window]['cloud-bottom'],
                #     portion=0.5
                # )
                # signal.stop_loss = sl
                # signal.take_profit = 3 * self.data[signal.index].closing - 2 * sl

                delta = ATRCalculator(self.data[:signal.index + 1], {
                    'window': self.config.get('indicators.rsi.stoploss.window'),
                }).do()[-1] * self.config.get('indicators.rsi.stoploss.multiplier')
                signal.stop_loss = self.data[signal.index].lowest - delta
                signal.take_profit = self.data[signal.index].closing + delta * self.config.get('indicators.rsi.take-profit.multiplier')
                signals.append(signal)
        return signals
    
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
        ema = EmaCalculator([candle.closing for candle in self.data], {
            'window': self.config.get('indicators.rsi.ema.window')
        }).do()
        for region in over_boughts:
            for index in region[-1:]:
                bl = True
                if self.data[index].closing + 1e-5 > ema[index]:
                    bl = False
                if bl and len(res) > 0 and index - res[-1].index <= (Config.get('models.signal.life') >> 1):
                    bl = False
                if bl:
                    res.append(Signal(
                        self.name, 
                        SignalTypes.LONG,
                        self.data[index],
                        index
                    ))
        return res
