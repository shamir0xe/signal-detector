from abc import ABC
from typing import List
from src.models.signal import Signal

class Indicator(ABC):
    def get_signals(self) -> List[Signal]:
        return []
