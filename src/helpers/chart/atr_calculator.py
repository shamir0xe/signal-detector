from typing import Dict, List
from src.models.candle import Candle
import ta
import pandas as pd


class ATRCalculator:
    def __init__(self, data: List[Candle], config: Dict) -> None:
        self.data = data
        self.config = config

    def do(self) -> List[float]:
        return ta.volatility.AverageTrueRange(
            high=pd.Series([float(candle.highest) for candle in self.data]),
            low=pd.Series([float(candle.lowest) for candle in self.data]),
            close=pd.Series([float(candle.closing) for candle in self.data]),
            window=min(self.config.get('window'), len(self.data))
        ).average_true_range().to_numpy().tolist()
