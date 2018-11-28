import math

if __name__ == '__main__':
    from vec2d import *
    from rect2d import *
    from circle import Circle2D
else:
    from ..vec2d import *
    from ..rect2d import *
    from .circle import Circle2D


class Arc2D(Circle2D):
    def __init__(self, center, radius, startAngle, sweep):
        super().__init__(center, radius)
        self.startAngle = startAngle
        self.sweep = sweep

    @property
    def beg(self):
        return center + v(1, 0).rotated(self.startAngle) * self.radius

    @property
    def end(self):
        return center + v(1, 0).rotated(self.startAngle + sweep) * self.radius