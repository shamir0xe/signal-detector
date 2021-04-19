from libs.PythonLibrary.utils import debug_text
from typing import Dict, List, Optional
from ...libs.PythonLibrary.argument_parser import ArgumentParser


class ArgumentDelegator:
    def __init__(self) -> None:
        self.args = {}

    def read(self) -> Dict[str, str]:
        self.args = ArgumentParser(index=0).get_pairs(remove_prefix=True)
        return self.args

    def available_args(self) -> List[str]:
        return [*self.args]

    def get(self, name: str) -> Optional[str]:
        return self.args.get(name)

