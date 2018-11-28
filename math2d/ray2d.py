import operator
import math

if __name__ == '__main__':
    from vec2d import *
else:
    from .vec2d import *


class Ray2D:
    """
    2D Ray
    """

    __slots__ = ['origin', 'direction']

    def __init__(self, o, d):
        self.origin = o
        self.direction = d


    def intersect(self, other):
        if not isinstance(other, Ray2D):
            return ValueError('Rays intersect only with rays')

        ao = self.origin
        ad = self.direction
        bo = other.origin
        bd = other.direction

        if bd.x != 0:
            u = (ao.y*bd.x + bd.y*bo.x - bo.y*bd.x - bd.y*ao.x ) / (ad.x*bd.y - ad.y*bd.x)
            v = (ao.x + ad.x * u - bo.x) / bd.x
        elif ad.x != 0:
            v = -((bo.y - ao.y) * ad.x + (ao.x - bo.x) * ad.y) / (bd.y * ad.x + bd.x*ad.y)
            u = (bo.x - ao.x + v * bd.x) / ad.x
        else:
            return None

        if u >= 0 and v >= 0:
            return ao + u * ad
        else:
            return None