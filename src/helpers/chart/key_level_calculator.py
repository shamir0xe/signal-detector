from libs.PythonLibrary.utils import debug_text
from typing import Dict, List
from src.models.candle import Candle
from src.models.key_level import KeyLevel
from src.helpers.key_level.key_levels_overlap import KeyLevelsOverlap
from src.helpers.key_level.merge_key_levels import MergeKeyLevels

class KeyLevelCalculator:
    def __init__(self, data: List[Candle], config: Dict) -> None:
        self.config = config
        self.data = []
        self.key_levels = []
        for candle in data:
            self.add_candle(candle)
        self.update_levels()
    
    def get_key_levels(self):
        return self.key_levels

    def add_candle(self, candle: Candle) -> List[KeyLevel]:
        self.data.append(candle)
        index = len(self.data) - self.config.get('left-window')
        sz = len(self.data)
        if self.config.get('left-window') <= index <= sz - self.config.get('right-window'):
            changed = self.check_and_add_level(index)
            if changed:
                self.update_levels()
        return self.key_levels
    
    def check_and_add_level(self, index: int) -> bool :
        left = index - self.config.get('left-window')
        right = index + self.config.get('right-window')
        # debug_text('l, i, r: %, %, %', left, i, right)
        maxi = max([candle.highest for candle in self.data[left: right + 1]])
        mini = min([candle.lowest for candle in self.data[left: right + 1]])
        added = False
        # debug_text('maxi: %', maxi)
        if self.data[index].closing > self.data[index].openning:
            # candle is green
            if self.data[index].highest == maxi:
                self.key_levels.append(KeyLevel(
                    level=self.data[index].closing,
                    width=(self.data[index].highest - self.data[index].closing) * 0.33,
                    index=index,
                ))
                added = True
            if self.data[index].lowest == mini:
                self.key_levels.append(KeyLevel(
                    level=self.data[index].openning,
                    width=(self.data[index].openning - self.data[index].lowest) * 0.33,
                    index=index,
                ))
                added = True
        else:
            # candle is red
            if self.data[index].lowest == mini:
                self.key_levels.append(KeyLevel(
                    level=self.data[index].closing,
                    width=(self.data[index].closing - self.data[index].lowest) * 0.33,
                    index=index,
                ))
                added = True
            if self.data[index].highest == maxi:
                self.key_levels.append(KeyLevel(
                    level=self.data[index].openning,
                    width=(self.data[index].highest - self.data[index].openning) * 0.33,
                    index=index,
                ))
                added = True
        return added
    
    def update_levels(self) -> None:
        changed = True
        while changed:
            changed = False
            for i in range(len(self.key_levels)):
                a = self.key_levels[i]
                for j in range(len(self.key_levels)):
                    if i >= j:
                        continue
                    b = self.key_levels[j]
                    if KeyLevelsOverlap.do(a, b):
                        c = MergeKeyLevels.do(a, b)
                        self.key_levels.append(c)
                        self.key_levels = [
                            *self.key_levels[:i], 
                            *self.key_levels[i + 1: j], 
                            *self.key_levels[j + 1:]
                        ]
                        changed = True
                        break;
                if changed:
                    break;
