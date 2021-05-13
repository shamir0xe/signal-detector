from typing import Any, List

from src.models.signal_types import SignalTypes
from src.models.candle import Candle
from src.models.signal import Signal
from src.delegators.trendline_delegator import TrendlineDelegator


class TrendlinesFilter:
    def validate(self, signal: Signal, data: List[Candle]) -> int:
        if signal.type == SignalTypes.LONG:
            return self.validate_downtrend(signal, data)
        return self.validate_uptrend(signal, data)
    
    def validate_downtrend(self, signal: Signal, data: List[Candle]) -> int:
        return TrendlineDelegator(signal, data) \
                .downtrend() \
                .check_passline()
    
    def validate_uptrend(self, signal: Signal, data: List[Candle]) -> int:
        return TrendlineDelegator(signal, data) \
                .uptrend() \
                .check_passline()
 