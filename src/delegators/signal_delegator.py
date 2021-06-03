from typing import Any, List

from src.models.signal import Signal
from src.models.candle import Candle
from src.indicators.rsi import Rsi
from src.indicators.stoch import Stoch
from src.indicators.stoch_rsi import StochRsi
from src.indicators.rsi_divergence import RsiDivergence
from src.indicators.ichimoku import Ichimoku
from src.indicators.candlestick_pattern import CandlestickPattern
from src.indicators.chart_pattern import ChartPattern


class SignalDelegator:
    def __init__(self, data: List[Candle]) -> None:
        self.data = data
        self.signals = []

    def process(self, signal_name: str) -> None:
        if signal_name == 'rsi':
            self.signals = [*self.signals, *Rsi(self.data).get_signals()]
        elif signal_name == 'stoch':
            self.signals = [*self.signals, *Stoch(self.data).get_signals()]
        elif signal_name == 'rsi-divergence':
            self.signals = [*self.signals, *RsiDivergence(self.data).get_signals()]
        elif signal_name == 'stoch-rsi':
            self.signals = [*self.signals, *StochRsi(self.data).get_signals()]
        elif signal_name == 'ichimoku':
            self.signals = [*self.signals, *Ichimoku(self.data).get_signals()]
        elif signal_name == 'candlestick-pattern':
            self.signals = [*self.signals, *CandlestickPattern(self.data).get_signals()]
        elif signal_name == 'chart-pattern':
            self.signals = [*self.signals, *ChartPattern(self.data).get_signals()]



    def get_signals(self) -> List[Signal]:
        return self.signals
