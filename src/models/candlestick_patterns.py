from enum import Enum

class CandlestickPatterns(Enum):
    LONG_WICK_CANDLE = 'long_wick_candle'
    INSIDE_BAR_CANDLE = 'inside_bar_candle'
    MOMENTUM_CANDLE = 'momentum_candle'
    MULTIPLE_REJECTION = 'multiple_rejection'
    SHRINKING_CANDLES = 'shrinking_candles'
    CANDLES_COLOR_CHANGE = 'candles_color_change'
