from typing import Any, Dict, List


class OverSoldCalculator:
    @staticmethod
    def calculate(data: Any, threshold: float, config: Dict) -> List[List[int]]:
        res = []
        index = config.get('window', 14)
        while index < len(data):
            while index < len(data) and data[index] > threshold:
                index += 1
            region = []
            while index < len(data) and data[index] <= threshold:
                region.append(index)
                index += 1
            if len(region) > 0 and (config.get('open-last-include') or index < len(data)):
                res.append(region)
        return res
