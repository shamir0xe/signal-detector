from libs.PythonLibrary.geometry import Geometry
from src.models.line_sides import LineSides

class LinePointSide:
    @staticmethod
    def do(line: Geometry.Line, point: Geometry.Point) -> LineSides:
        sign = Geometry.side_sign(line.p1, line.p2, point)
        if sign == +1:
            return LineSides.TOP
        if sign == -1:
            return LineSides.BOTTOM
        return LineSides.ON


