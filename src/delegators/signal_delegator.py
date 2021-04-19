from typing import Any, List
from ..models.signal import Signal
from ..models.candle import Candle


class SignalDelegator:
    def __init__(self, signal_name: str, data: List[Candle]) -> None:
        self.signal_name = signal_name
        self.data = data
        self.signals = []

    def process(self) -> None:
        pass

    def get_signals(self) -> List[Signal]:
        return self.signals
