import math

if __name__ == '__main__':
    from vec2d import *
    from vec2d import *
else:
    from ..vec2d import *
    from ..rect2d import *


class Circle2D:
    def __init__(self, center, radius):
        self.center = center
        self.radius = radius
