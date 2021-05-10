class IntervalAdapter:
    @staticmethod
    def plug(interval: str) -> int:
        if interval == '1min':
            return 60
        if interval == '5min':
            return 60 * 5
        if interval == '15min':
            return 60 * 15
        if interval == '30min':
            return 60 * 30
        if interval == '1hour':
            return 60 * 60
        if interval == '4hour':
            return 60 * 60 * 4
        return 0
