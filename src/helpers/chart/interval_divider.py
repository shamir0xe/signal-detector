class IntervalDivider:
    @staticmethod
    def do(start: float, end: float, portion: float = 0.5) -> float:
        return start + (end - start) * portion
