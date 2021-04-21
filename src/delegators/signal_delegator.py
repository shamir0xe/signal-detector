from typing import Any, List

from ..models.signal import Signal
from ..models.candle import Candle
from ..indicators.rsi import Rsi
from ..indicators.stoch import Stoch
from ..indicators.stoch_rsi import StochRsi
from ..indicators.rsi_divergence import RsiDivergence


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

    def get_signals(self) -> List[Signal]:
        return self.signals
