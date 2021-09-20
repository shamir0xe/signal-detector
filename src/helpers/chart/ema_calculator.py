from typing import Dict, List

import ta
import pandas as pd

class EmaCalculator:
    def __init__(self, data: List[float], config: Dict) -> None:
        self.config = config
        self.data = [*[data[0] for _ in range(self.config.get('window'))], *data]

    def do(self) -> List[float]:
        return ta.trend.EMAIndicator(
            close=pd.Series(self.data),
            window=self.config.get('window'),
        ).ema_indicator().to_numpy().tolist()[self.config.get('window'):]
