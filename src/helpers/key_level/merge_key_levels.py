from src.models.key_level import KeyLevel
from src.facades.config import Config


class MergeKeyLevels:
    @staticmethod
    def do(
        a: KeyLevel, 
        b: KeyLevel
    ) -> KeyLevel:
        if b.index < a.index:
            c = a
            a = b
            b = c
        discount_factor = Config.get('key-level.discount-factor')
        a_count = int(a.count * discount_factor)
        b_count = a.count + b.count - a_count
        level = (a.level * a_count + b.level * b_count) / (a_count + b_count)
        width = (a.width * a_count + b.width * b_count) / (a_count + b_count)
        count = a_count + b_count
        return KeyLevel(
            level=level,
            width=width,
            index=b.index,
            count=count
        )
