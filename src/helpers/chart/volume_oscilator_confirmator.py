from libs.PythonLibrary.utils import debug_text
from src.helpers.time.time_converter import TimeConverter
from libs.PythonLibrary.geometry import Geometry
from typing import Dict, List
from src.helpers.geometry.convex_calculator import ConvexBound
from src.models.candle import Candle
from src.models.trend_types import TrendTypes
import ta
import pandas as pd


class VolumeOscilatorConfirmator:
    def __init__(self, data: List[Candle], config: Dict) -> None:
        self.config = config
        self.data = data[self.__start_index(len(data)):]

    def do(self, trend: TrendTypes) -> bool:
        volume_oscilator = ta.momentum.PercentageVolumeOscillator(
            volume = pd.Series([float(candle.volume) for candle in self.data]),
            window_slow = self.config.get('window-slow'),
            window_fast = self.config.get('window-fast')
        ).pvo().to_numpy().tolist()
        bounds = ConvexBound([
            Geometry.Point(i, volume_oscilator[i]) for i in 
            range(len(volume_oscilator) - 4, len(volume_oscilator))]).do(trend)
        bounds = bounds[::-1]
        
        bl = True
        bl &= bounds[-1].y > 1e-3 + self.config.get('min-volume-threshold')
        bl &= bounds[-1].y > 1e-3 + bounds[-2].y


        # if "05/04" in TimeConverter.seconds_to_timestamp(self.data[-1].time):
        #     debug_text('~~time: %', TimeConverter.seconds_to_timestamp(self.data[-1].time))
        #     debug_text('~~bounds[-1, -2]: %, %', bounds[-1].y, bounds[-2].y)
        #     debug_text('~~bounds[-1].y > 1e-3 + self.config.get("min-volume-threshold") ? %', bounds[-1].y > 1e-3 + self.config.get('min-volume-threshold'))
        #     debug_text('~~min volume: %', self.config.get('min-volume-threshold'))
        #     for point in bounds:
        #         debug_text('!!! %, %', point.x, point.y)
        #     debug_text("bl ? %", bl)

        return bl

    def __start_index(self, length: int):
        return max(
            0,
            length - 2 * self.config.get('window-slow')
        )
