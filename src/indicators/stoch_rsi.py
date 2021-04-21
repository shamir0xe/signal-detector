from typing import List

from ..models.candle import Candle
from .indicator_abstract import Indicator
from ..models.signal import Signal

class StochRsi(Indicator):
    def __init__(self, data: List[Candle]) -> None:
        self.name = 'rsi'
        self.data = data
        self.config = self.__read_config()

    def __read_config(self) -> None:
        pass
    
    def get_signals(self) -> List[Signal]:
        res = []
        return res
