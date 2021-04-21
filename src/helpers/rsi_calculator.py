from typing import Any, List
import ta
import pandas as pd
import numpy as np
from ..models.candle import Candle

class RsiCalculator:
    def __init__(self, data: List[Candle], config: Any) -> None:
        self.data = data
        self.config = config

    def calculate(self) -> Any:
        return ta.momentum.RSIIndicator(
            close = pd.Series([float(candle.closing) for candle in self.data]), 
            window = self.config.get('window', 14), 
            fillna = self.config.get('fillna', True)
        ).rsi().to_numpy()
