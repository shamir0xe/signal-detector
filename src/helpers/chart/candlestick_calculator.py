from src.facades.config import Config
from src.helpers.time.time_converter import TimeConverter
from libs.PythonLibrary.utils import debug_text
import math
from typing import List, Optional, Tuple
from src.models.trend_types import TrendTypes
from src.models.key_level import KeyLevel
from src.models.candle import Candle
from src.models.candlestick_patterns import CandlestickPatterns

class CandlestickCalculator:
    def __init__(
        self,
        data: List[Candle],
        key_levels: List[KeyLevel]
    ) -> None:
        self.data = data
        self.key_levels = sorted(key_levels, key=lambda level: -level.index)
        self.key_level = None

    def do(self, trend_type: TrendTypes) -> Tuple[int, Optional[KeyLevel]]:
        point = self.get(CandlestickPatterns.MOMENTUM_CANDLE, trend_type)
        if point <= 0:
            return 0, None
        # debug_text()
        # debug_text('TIME: %', TimeConverter.seconds_to_timestamp(self.data[-1].time))
        # debug_text('available key levels')
        # for key_level in self.key_levels:
        #     debug_text('    %', key_level)
        points = 0
        points += self.get(CandlestickPatterns.CANDLES_COLOR_CHANGE, trend_type)
        points += self.get(CandlestickPatterns.LONG_WICK_CANDLE, trend_type)
        points += self.get(CandlestickPatterns.INSIDE_BAR_CANDLE, trend_type)
        points += self.get(CandlestickPatterns.SHRINKING_CANDLES, trend_type)
        points += self.get(CandlestickPatterns.MULTIPLE_REJECTION, trend_type)
        # if points > 0:
        #     debug_text('hell yea, points: %', points)
        return (points, self.key_level)
    
    def get(self, pattern: CandlestickPatterns, *args) -> int:
        return getattr(self, '{}'.format(pattern.value))(*args)
    
    def __cross_down(
        self, 
        level: float, 
        just_touch: Optional[bool] = False
    ) -> Tuple[bool, KeyLevel]:
        supp = self.key_level.level - self.key_level.width
        if just_touch:
            supp = self.key_level.level + self.key_level.width
        if level <= supp:
            return True, self.key_level
        return False, KeyLevel(0, 0, 0)

    def __cross_up(
        self,
        level: float,
        just_touch: Optional[bool] = False
    ) -> Tuple[bool, KeyLevel]:
        for key_level in self.key_levels:
            supp = key_level.level + key_level.width
            if just_touch:
                supp = key_level.level - key_level.width
            if level >= supp:
                return True, key_level
        return False, KeyLevel(0, 0, 0)
    
    def side(self, level: float) -> int:
        sign = 0
        for candle in self.data[-Config.get('key-level.breakthrough-window'):]:
            cur = +1 if candle.highest > level else -1 if candle.lowest < level else 0
            if sign == 0:
                sign = cur
            if cur != 0 and sign != cur:
                return 0
        return sign
    
    def long_wick_candle(self, trend_type: TrendTypes) -> int:
        bl = True
        if trend_type is TrendTypes.DOWN:
            bl = False
            # -2 candle should be red
            for i in range(Config.get('key-level.long-wick-backward')):
                gk = True
                index = -2 - i
                # -2 candle should be red
                gk &= self.data[index].closing < self.data[index].openning
                # -2 candle lowest part should cross key_level
                gk &= self.__cross_down(self.data[index].lowest, True)[0]
                # -2 candle body should not cross key_level
                gk &= not self.__cross_down(self.data[index].openning)[0]
                # -2 candle body should be small prior to highest/lowest
                gk &= (self.data[index].highest - self.data[index].lowest) > Config.get('key-level.long-wick-body-ratio') * \
                    self.data[index].get_size()
                bl |= gk
                if bl:
                    break
        # if bl:
        #     debug_text('LOW_WICK_CANDLE')
        return +1 if bl else 0

    def inside_bar_candle(self, trend_type: TrendTypes) -> int:
        bl = True
        if trend_type is TrendTypes.DOWN:
            # -3 candle should be red
            # bl &= self.data[-3].closing < self.data[-3].openning
            # -3 candle highest > -2 candle highest
            bl &= self.data[-3].highest > self.data[-2].highest
            # -3 candle lowest < -2 candle lowest
            bl &= self.data[-3].lowest < self.data[-2].lowest
        # if bl:
        #     debug_text('INSIDE_BAR_CANDLE')
        return +1 if bl else 0

    def get_mixed_level(self, trend_type: TrendTypes) -> Optional[KeyLevel]:
        for key_level in self.key_levels:
            cur_side = self.side(key_level.level)
            if cur_side == 0:
                return key_level
        return None

    def momentum_candle(self, trend_type: TrendTypes) -> int:
        bl = True
        # -1 candle should be green
        bl &= self.data[-1].closing > self.data[-1].openning
        # -1 candle body > -2 candle body
        bl &= self.data[-1].get_size() > self.data[-2].get_size()
        # all of the candles should be above levels till reaching mixed level
        # in the mixed level:
        #                       candle -1 should be closed above the level
        if not bl:
            return 0
        # debug_text('we have need to find key level')
        mixed_level = self.get_mixed_level(trend_type)
        self.key_level = mixed_level
        bl &= mixed_level != None and self.data[-1].closing > mixed_level.level
        # last closing should be more higher than openning according to level
        # bl &= self.data[-1].closing - level.level > level.level - self.data[-1].openning
        # -2 candle should be red
        # bl &= self.data[-2].closing < self.data[-2].openning
        return +1 if bl else 0

    def multiple_rejection(self, trend_type: TrendTypes) -> int:
        bl = True
        if trend_type is TrendTypes.DOWN:
            count = 0
            for candle in self.data:
                count += 1 if candle.highest > self.key_level.level else 0
            bl &= count > round(Config.get('key-level.min-touch-ratio') * len(self.data))
        # if bl:
        #     debug_text('MULTIPLE REJECTION')
        return +1 if bl else 0

    def shrinking_candles(self, trend_type: TrendTypes) -> int:
        bl = True
        if trend_type is TrendTypes.DOWN:
            # bl = False
            # size should be shrinking before reaching -1
            # for i in range(1):
            size = 1e20
            for candle in self.data[len(self.data) - Config.get('key-level.shrinking-candles-backward'):-Config.get('key-level.shrinking-candles-offset')]:
                temp = candle.openning - candle.closing
                bl &= size > temp 
                size = temp
            # if gk and "Mon 21/05/24" in TimeConverter.seconds_to_timestamp(self.data[-1].time):
            #     debug_text('~~~~ i is %', i)
            #     for candle in self.data[:-i]:
            #         temp = candle.closing - candle.openning
            #         debug_text('    size: %', temp)
        # if bl:
        #     debug_text('SHRINKING_CANDLE')
        return +1 if bl else 0

    def candles_color_change(self, trend_type: TrendTypes) -> int:
        bl = True
        if trend_type is TrendTypes.DOWN:
            # color should be all red till -1
            for candle in self.data[-Config.get('key-level.candles-color-backward'):-Config.get('key-level.candles-color-offset')]:
                bl &= candle.closing < candle.openning
        # if bl:
        #     debug_text('CANDLES_COLOR_CHANGE')
        return +1 if bl else 0
    