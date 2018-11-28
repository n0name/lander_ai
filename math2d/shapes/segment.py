import math

if __name__ == '__main__':
    from vec2d import *
    from rect2d import *
    from ray2d import *
else:
    from ..vec2d import *
    from ..rect2d import *
    from ..ray2d import *


class Segment2D:
    def __init__(self, beg, end):
        self.beg = beg
        self.end = end

    def length(self):
        return (self.end - self.beg).get_length()

    def tangent_vector(self):
        v = self.end - self.beg
        return v.normalized()

    def normal_vector(self):
        tv = self.tangent_vector()
        return v(-tv.y, tv.x)

    def intersect_with(self, other):
        if isinstance(other, Segment2D):
            v1 = self.tangent_vector()
            v2 = other.tangent_vector()
            if v1.cross(v2) == 0: # they are parallel
                return []

            r1 = Ray2D(self.beg, v1)
            r2 = Ray2D(other.beg, v2)
            cross = r1.intersect(r2)
            if cross is not None:
                if self.beg.get_distance(cross) <= self.length() and other.beg.get_distance(cross) <= other.length():
                    return [cross]
            
            return []
        else:
            raise ValueError('Unsupported type')
