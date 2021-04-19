from ..helpers.time_converter import TimeConverter

class Candle:
    def __init__(
        self, 
        time: int, 
        openning: float, 
        closing: float, 
        highest: float,
        lowest: float,
        volume: float,
        amount: float,
        market: str
    ) -> None:
        self.time = time
        self.openning = openning
        self.closing = closing
        self.highest = highest
        self.lowest = lowest
        self.volume = volume
        self.amount = amount
        self.market = market


    def __str__(self) -> str:
        return '[market: {}, time: {}, o: {}, c: {}, h: {}, l: {}, v: {}, amount: {}]'.format(
            self.market,
            TimeConverter.seconds_to_timestamp(self.time),
            self.openning,
            self.closing,
            self.highest,
            self.lowest,
            self.volume,
            self.amount
        )
