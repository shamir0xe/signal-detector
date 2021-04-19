from __future__ import annotations
from libs.PythonLibrary.utils import debug_text
from .argument_delegator import ArgumentDelegator
from .signal_delegator import SignalDelegator
from ..handlers.config_handler import Config
from ..handlers.data_handler import DataFetcher


class App:
    def __init__(self) -> None:
        self.__init_variables()
        self.config = Config()
        self.arguments = ArgumentDelegator()
        self.data_fetcher = DataFetcher()

    def __init_variables(self) -> None:
        self.out = self.data = self.market = self.interval = \
        self.past_days = self.signals = None

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
        self.out = []
        for signal_name in self.signals:
            signal_delegator = SignalDelegator(signal_name, self.data)
            signal_delegator.process()
            self.out = [*self.out, *signal_delegator.get_signals()]
        return self

    def output_results(self) -> None:
        print('the end')
        print(self.out)
