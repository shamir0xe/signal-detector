from typing import Optional, Tuple


class KeyLevel:
    def __init__(
        self,
        level: float,
        width: float,
        index: int,
        count: Optional[int] = 1
    ) -> None:
        self.level = level
        self.width = width
        self.index = index
        self.count = count

    def get_edges(self) -> Tuple[float, float]:
        return (
            self.level - self.width, 
            self.level + self.width
        )

    def __str__(self) -> str:
        return '[L: {}, W: {}, I: {}, C: {}]'.format(
            self.level,
            self.width,
            self.index,
            self.count
        )
