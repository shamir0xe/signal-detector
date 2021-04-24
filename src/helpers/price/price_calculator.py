from typing import List

from ...helpers.config.config_reader import ConfigReader
from ...delegators.trendline_delegator import TrendlineDelegator

from ...helpers.trend.trend_calculator import TrendCalculator

from ...models.signal_types import SignalTypes
from ...models.signal import Signal
from ...models.price_types import PriceTypes
from ...models.candle import Candle

class PriceCalculator:
    def __init__(self, data: List[Candle], signal: Signal) -> None:
        self.data = data
        self.signal = signal
        self.config = self.__read_config()

    def do(self, price_type: PriceTypes) -> float:
        if self.signal.type is SignalTypes.SHORT:
            return self.__short_price(price_type)
        if self.signal.type is SignalTypes.LONG:
            return self.__long_price(price_type)
        return -1

    def __read_config(self):
        return ConfigReader("helpers.price.price-calculator")

    def __average_candle_size(self) -> float:
        index = self.signal.index
        start = max(0, index - self.config.get('farthest_candle'))
        return sum([self.data[i].get_size() for i in range(start, index + 1)]) / (index + 1 - start)

    def __short_price(self, price_type: PriceTypes) -> float:
        candle_size = self.__average_candle_size()
        trendline_height = TrendlineDelegator(self.signal, self.data).uptrend().get_trendline_hegiht()
        if price_type is PriceTypes.ENTRY_PRICE:
            return self.signal.candle.closing
        if price_type is PriceTypes.SELL_PRICE:
            # return self.signal.candle.closing - candle_size * self.config.get('candle_margin') 
            return max(
                self.signal.candle.closing - candle_size * self.config.get('candle_margin'), 
                self.signal.candle.closing - trendline_height / 2
            )
        if price_type is PriceTypes.STOP_LOSS:
            # return self.signal.candle.closing + candle_size * self.config.get('candle_margin')
            return max(
                self.signal.candle.closing + candle_size * self.config.get('candle_margin'),
                self.signal.candle.closing + trendline_height / 2
            )
        return 0
    
    def __long_price(self, price_type: PriceTypes) -> float:
        candle_size = self.__average_candle_size()
        trendline_height = TrendlineDelegator(self.signal, self.data).downtrend().get_trendline_hegiht()
        if price_type is PriceTypes.ENTRY_PRICE:
            return self.signal.candle.closing
        if price_type is PriceTypes.SELL_PRICE:
            # return self.signal.candle.closing + candle_size * self.config.get('candle_margin') 
            return min(
                self.signal.candle.closing + candle_size * self.config.get('candle_margin'),
                self.signal.candle.closing + trendline_height / 2
            )
        if price_type is PriceTypes.STOP_LOSS:
            # return self.signal.candle.closing - candle_size * self.config.get('candle_margin')
            return min(
                self.signal.candle.closing - candle_size * self.config.get('candle_margin'),
                self.signal.candle.closing + trendline_height / 2
            )
        return 0
