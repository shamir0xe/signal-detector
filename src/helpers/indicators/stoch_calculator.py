from typing import Any, List
import ta
import pandas as pd
import numpy as np
from ...models.candle import Candle

class StochCalculator:
    def __init__(self, data: List[Candle], config: Any) -> None:
        self.data = data
        self.config = config

    def calculate(self) -> Any:
        return ta.momentum.StochasticOscillator(
            close = pd.Series([float(candle.closing) for candle in self.data]), 
            high = pd.Series([float(candle.highest) for candle in self.data]), 
            low = pd.Series([float(candle.lowest) for candle in self.data]), 
            window = self.config.get('window', 14), 
            smooth_window = self.config.get('smooth_window', 1),
            fillna = self.config.get('fillna', True)
        ).stoch().to_numpy()

