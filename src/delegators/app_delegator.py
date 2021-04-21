from __future__ import annotations
from libs.PythonLibrary.utils import debug_text
import json
from .argument_delegator import ArgumentDelegator
from .signal_delegator import SignalDelegator
from ..handlers.config_handler import Config
from ..handlers.data_handler import DataFetcher
from ..helpers.signal.signal_examinator import SignalExaminator
from ..helpers.time.time_converter import TimeConverter
from ..helpers.price.price_calculator import PriceCalculator
from ..filters.trendlines_filter import TrendlinesFilter
from ..models.price_types import PriceTypes


class App:
    def __init__(self) -> None:
        self.__init_variables()
        self.config = Config()
        self.arguments = ArgumentDelegator()
        self.data_fetcher = DataFetcher()

    def __init_variables(self) -> None:
        self.out = self.data = self.market = self.interval = \
        self.past_days = self.signals = self.pending_signals = None

    def apply_config(self) -> App:
        self.config.read()
        for attribute in self.config.available_configs():
            setattr(self, attribute, self.config.get(attribute))
        return self

    def apply_arguments(self) -> App:
        self.arguments.read()
        for attribute in self.arguments.available_args():
            setattr(self, attribute, self.arguments.get(attribute))
        return self

    def fetch_data(self) -> App:
        self.data = self.data_fetcher.fetch(
            market=self.market,
            interval=self.interval,
            past_days=self.past_days
        )
        return self

    def detect_signals(self) -> App:
        signal_delegator = SignalDelegator(self.data)
        for signal_name in self.signals:
            signal_delegator.process(signal_name)
        self.out = signal_delegator.get_signals()
        return self

    def examining_signals(self) -> App:
        for signal in self.out:
            signal.set_status(SignalExaminator().do(signal, self.data))
        return self
    
    def filter_trendlines(self) -> App:
        signals = self.out
        self.out = []
        self.pending_signals = []
        for signal in signals:
            index = TrendlinesFilter().validate(signal, self.data)
            # debug_text('%, t:%, validation result: %', signal.type, TimeConverter.seconds_to_timestamp(signal.candle.time),index)
            if index > 0:
                signal.original_candle = signal.candle
                signal.candle = self.data[index]
                signal.index = index
                # debug_text('tt:%', TimeConverter.seconds_to_timestamp(signal.candle.time))
                self.out.append(signal)
            elif index == 0:
                self.pending_signals.append(signal)
        return self
    
    def print_indicators_summary(self) -> App:
        res = {}
        for signal in self.out:
            if not signal.name in res:
                res[signal.name] = {
                    +1: 0,
                    -1: 0,
                    0: 0,
                    -2: 0,
                }
            res[signal.name][signal.status] += 1
        for signal_name in [*res]:
            denominator = res[signal_name][+1] + res[signal_name][-1]
            if denominator > 0.5:
                debug_text('%: %', signal_name, 1. * res[signal_name][+1] / denominator)
        return self

    def remove_duplicates(self) -> App:
        signals = self.out[:]
        self.out = []
        for signal in signals:
            found = False
            for old_one in self.out:
                if signal.equals(old_one):
                    found = True
                    break
            if found:
                continue
            self.out.append(signal)
        return self

    def print_results(self) -> App:
        self.out.sort(key=lambda signal: signal.candle.time)
        out = []
        for signal in self.out:
            out.append({
                'name': signal.name,
                'type': signal.type.name,
                'time': signal.candle.time,
                'status': 'OK' if signal.status == +1 else 'Failed' if signal.status == -1 else 'Pending' if signal.status == 0 else 'Dumped',
                'details': {
                    'entry': PriceCalculator(self.data, signal).do(PriceTypes.ENTRY_PRICE),
                    'sell_price': PriceCalculator(self.data, signal).do(PriceTypes.SELL_PRICE),
                    'stop_loss': PriceCalculator(self.data, signal).do(PriceTypes.STOP_LOSS),
                }
            })
        print(json.dumps(out))
        # for signal in self.out:
        #     debug_text(
        #         '%/% - t:% - o:%, %', 
        #         signal.name, 
        #         signal.type, 
        #         TimeConverter.seconds_to_timestamp(signal.candle.time), 
        #         TimeConverter.seconds_to_timestamp(signal.original_candle.time) if not signal.original_candle is None else None, 
        #         'OK' if signal.status == +1 else 'Failed' if signal.status == -1 else 'Pending' if signal.status == 0 else 'Dumped'
        #     )
        return self

