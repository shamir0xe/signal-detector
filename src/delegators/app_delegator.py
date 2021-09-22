from __future__ import annotations
from libs.PythonLibrary.utils import debug_text
import json

from .argument_delegator import ArgumentDelegator
from .signal_delegator import SignalDelegator
from src.helpers.time.candle_to_timestamp import CandleToTimestamp
from src.models.signal_statuses import SignalStatuses
from src.handlers.config_handler import Config
from src.handlers.data_handler import DataFetcher
from src.helpers.signal.signal_examinator import SignalExaminator
from src.helpers.time.time_converter import TimeConverter
from src.helpers.price.price_calculator import PriceCalculator
from src.filters.trendlines_filter import TrendlinesFilter
from src.models.price_types import PriceTypes
from src.adapters.argument_data_adapter import ArgumentDataAdapter
from libs.PythonLibrary.utils import Timer
from src.helpers.database.candle_retriever import CandleRetriever


class App:
    def __init__(self) -> None:
        self.__init_variables()
        self.timer = Timer()
        self.config = Config()
        self.arguments = ArgumentDelegator()
        self.data_fetcher = DataFetcher()

    def __init_variables(self) -> None:
        self.out = self.market = self.interval = \
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
            if attribute in ['past_days']:
                setattr(self, attribute, int(getattr(self, attribute)))
        return self

    def fetch_data(self) -> App:
        if hasattr(self, 'memory'):
            self.market = self.market.lower()
            start_time, end_time = CandleToTimestamp.do(self.interval, (-self.past_days + 1, +1))
            self.data = CandleRetriever.find(
                market = self.market,
                interval = self.interval,
                start_time = start_time,
                end_time = end_time,
            )
        elif hasattr(self, 'data'):
            self.data = ArgumentDataAdapter.translate(self.data)
        else:
            self.data = self.data_fetcher.fetch(
                market=self.market,
                interval=self.interval,
                past_days=self.past_days
            )[:-1]
        # debug_text('last 10 candles: ')
        # for candle in self.data[-10:]:
        #     debug_text('candle: %', candle)
        return self

    def detect_signals(self) -> App:
        signal_delegator = SignalDelegator(self.data)
        for signal_name in self.signals:
            signal_delegator.process(signal_name)
        self.out = signal_delegator.get_signals()
        return self

    def examining_signals(self) -> App:
        if hasattr(self, 'no-examin'):
            return self
        for signal in self.out:
            exam_result = SignalExaminator().do(signal, self.data)
            signal.set_status(exam_result["status"])
            signal.set_gain(exam_result["gain"])
            signal.set_life(exam_result['life'])
        return self
    
    def filter_trendlines(self) -> App:
        # signals = self.out
        # self.out = []
        # self.pending_signals = []
        # for signal in signals:
        #     index = TrendlinesFilter().validate(signal, self.data)
        #     # debug_text('%, t:%, validation result: %', signal.type, TimeConverter.seconds_to_timestamp(signal.candle.time),index)
        #     if index > 0:
        #         signal.original_candle = signal.candle
        #         signal.candle = self.data[index]
        #         signal.index = index
        #         # debug_text('tt:%', TimeConverter.seconds_to_timestamp(signal.candle.time))
        #         self.out.append(signal)
        #     elif index == 0:
        #         self.pending_signals.append(signal)
        return self
    
    def calculate_success_rate(self) -> App:
        res = {}
        self.success_rate = {}
        for signal in self.out:
            if not signal.name in res:
                res[signal.name] = {
                    +1: 0,
                    -1: 0,
                    0: 0,
                    -2: 0,
                }
            res[signal.name][signal.status.value] += 1
        for signal_name in [*res]:
            denominator = res[signal_name][+1] + res[signal_name][-1]
            self.success_rate[signal_name] = 0
            if denominator > 0.5:
                self.success_rate[signal_name] = 1. * res[signal_name][+1] / denominator
        return self
    
    def print_summary(self) -> App:
        res = {}
        for signal in self.out:
            if not signal.name in res:
                res[signal.name] = {
                    +1: 0,
                    -1: 0,
                    0: 0,
                    -2: 0,
                    "gain": 0
                }
            res[signal.name][signal.status.value] += 1
            res[signal.name]["gain"] += signal.gain
        for signal_name in [*self.success_rate]:
            debug_text('%: % ~~ win:% loss:%', signal_name, res[signal_name]["gain"], res[signal_name][+1], res[signal_name][-1])
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
                'success_rate': self.success_rate[signal.name],
                'type': signal.type.name,
                'time': signal.candle.time,
                'market': self.market,
                'interval': self.interval,
                'gain': signal.gain,
                'life': signal.life,
                'status': 'OK' if signal.status is SignalStatuses.DONE
                 else 'Failed' if signal.status is SignalStatuses.FAILED 
                 else 'Pending' if signal.status is SignalStatuses.PENDING else 'Dumped',
                'details': {
                    'entry_price': signal.candle.closing,
                    'take_profit': signal.take_profit,
                    'stop_loss': signal.stop_loss,
                }
            })
        print(json.dumps(out))
        if hasattr(self, 'show-summary'):
            for signal in self.out:

                debug_text('time: %, gain: {}{:03f}, status: %'.format('+' if signal.gain > 0 else '', signal.gain), TimeConverter.seconds_to_timestamp(signal.candle.time), signal.status)
            self.print_summary()
            self.timer.time_stamp()
        return self
