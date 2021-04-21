from typing import List
from libs.PythonLibrary.geometry import Geometry

from libs.PythonLibrary.utils import debug_text
from ..helpers.show_plot import ShowGeometryPlot

class UpperBoundConvex:
    def __init__(self, data: List[Geometry.Point]) -> None:
        self.data = data

    def do(self) -> List[Geometry.Point]:
        data = self.data[:]
        data.sort(key=lambda p: p.x)
        data = data[::-1]
        p1 = data[0]
        data[1:].sort(key=lambda p: p1.cross(p))
        stack = [p1]
        i = 1
        while i < len(data):
            while len(stack) >= 2 and data[i].subtract(stack[-1]).cross(stack[-2].subtract(stack[-1])) <= 0:
                stack.pop()
            stack.append(data[i])
            i += 1
        # ShowGeometryPlot().do(data, stack)
        return stack


class LowerBoundConvex:
    def __init__(self, data: List[Geometry.Point]) -> None:
        self.data = data

    def do(self) -> List[Geometry.Point]:
        data = self.data[:]
        # for point in data:
            # debug_text('p: %', point)
        data.sort(key=lambda p: p.x)
        data = data[::-1]
        p1 = data[0]
        # debug_text('p1: %', p1)
        data[1:].sort(key=lambda p: -p1.cross(p))
        stack = [p1]
        i = 1
        while i < len(data):
            while len(stack) >= 2 and data[i].subtract(stack[-1]).cross(stack[-2].subtract(stack[-1])) >= 0:
                stack.pop()
            stack.append(data[i])
            i += 1
        # ShowGeometryPlot().do(data, stack)
        return stack
