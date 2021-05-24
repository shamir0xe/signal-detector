from typing import Dict, List

import ta
import pandas as pd

class EmaCalculator:
    def __init__(self, data: List[float], config: Dict) -> None:
        self.data = data
        self.config = config

    def do(self) -> List[float]:
        return ta.trend.EMAIndicator(
            close=pd.Series([data for data in self.data]),
            window=self.config.get('window'),
        ).ema_indicator().to_numpy().tolist()
