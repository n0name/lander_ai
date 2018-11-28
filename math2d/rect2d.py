import operator
import math

if __name__ == '__main__':
    from vec2d import *
else:
    from .vec2d import *


class Rect2d:
    """
    2D Rectangle and utility functions
    """
    __slots__ = ['l', 't', 'r', 'b']

    (INIT_EMPTY,
     INIT_NULL,
     INIT_INFINITE) = range(3)

    def __init__(self, *args, init_type=INIT_EMPTY):
        if len(args) == 4:
            self.l, self.t, self.r, self.b = args
        elif len(args) == 2:
            x, y = args[0]
            w, h = args[1]
            self.l, self.t = x, y
            self.r, self.b = x + w, y + h
            pass
        elif len(args) == 1:
            if isinstance(args[0], tuple):
                self.l, self.t, self.r, self.b = args[0]
            else:
                raise ValueError("Invalid parameters given")
        elif len(args) == 0:
            if init_type == Rect2d.INIT_NULL:
                self.set_null()
            elif init_type == Rect2d.INIT_INFINITE:
                self.set_infinite()
            else:
                self.set_empty()
        else:
            raise ValueError("Invalid parameters given")

    def __len__(self):
        return 4
    
    def __and__(self, other):
        """
        Calculates a rect including both self and other
        """
        if isinstance(other, Rect2d):
            return Rect2d(
                min(self.l, other.l),
                min(self.t, other.t),
                max(self.r, other.r),
                max(self.b, other.b)
            )
        elif isinstance(other, Vec2d):
            return Rect2d(
                min(self.l, other.x),
                min(self.t, other.y),
                max(self.r, other.x),
                max(self.b, other.y)
            )
        elif isinstance(other, [list, tuple]) and len(other) == 2:
            x, y = other
            return Rect2d(
                min(self.l, x),
                min(self.t, y),
                max(self.r, x),
                max(self.b, y)
            )
        else:
            raise ValueError("Invalid Argument")

    def __or__(self, other):
        """
        Calculates the intersection between rects
        """
        if not isinstance(other, Rect2d):
            return ValueError("Invalid Argument")

        # non intersecting case
        if not self.is_inside(other.pos()) and not other.is_inside(self.pos()):
            return Rect2d(init_type=self.INIT_EMPTY)

        return Rect2d(
            max(self.l, other.l),
            max(self.t, other.t),
            min(self.r, other.r),
            min(self.b, other.b)
        )

    def set(self, *args):
        if len(args) == 4:
            self.l, self.t, self.r, self.b = args
        elif len(args) == 2:
            x, y = args[0]
            w, h = args[1]
            self.l, self.t = x, y
            self.r, self.b = x + w, y + h
            pass
        elif len(args) == 1:
            if isinstance(args[0], tuple):
                self.l, self.t, self.r, self.b = args[0]
            else:
                raise ValueError("Invalid parameters given")
        else:
            raise ValueError("Invalid parameters given")

    def pos(self):
        return (self.l, self.t)

    def vec_pos(self):
        return v(self.l, self.t)

    def int_pos(self):
        return (int(self.l), int(self.t))

    def size(self):
        return (self.width(), self.height())

    def int_size(self):
        return (int(self.width()), int(self.height()))

    def width(self):
        return self.r - self.l

    def height(self):
        return self.b - self.t

    def area(self):
        return self.width() * self.height()

    def check_valid(self):
       return not self.is_null() and not self.is_infinite()

    def set_null(self):
        self.l, self.t, self.r, self.b = (
            float('inf'),
            float('inf'),
            -float('inf'),
            -float('inf')
        )

    def is_null(self):
        inf = float('inf')
        return self.l == inf or self.t == inf or self.r == -inf or self.b == -inf

    def set_empty(self):
        self.l, self.t, self.r, self.b = 0, 0, 0, 0

    def is_empty(self):
        w, h = self.width(), self.height()
        return w == 0 and h == 0

    def set_infinite(self):
        inf = float('inf')
        self.l, self.t = -inf, -inf
        self.r, self.b = inf, inf

    def is_infinite(self):
        inf = float('inf')
        return self.l == -inf or self.t == -inf or self.r == inf or self.b == inf

    def is_inside(self, pt_or_x, y=None):
        if not self.check_valid():
            return False

        if isinstance(pt_or_x, Vec2d):
            _x, _y = pt_or_x.x, pt_or_x.y
        elif isinstance(pt_or_x, tuple):
            _x, _y = pt_or_x
        elif isinstance(pt_or_x, (float, int)) and y is not None:
            _x = pt_or_x
            _y = y
        else:
            raise ValueError("Invalid argument")
        if _x >= self.l and _x <= self.r:
            if _y >= self.t and _y <= self.b:
                return True

        return False

    def center(self):
        return (
            (self.l + self.r) / 2,
            (self.t + self.b) / 2,
        )

    def vec_center(self):
        return v(
            (self.l + self.r) / 2,
            (self.t + self.b) / 2,
        )

    def int_center(self):
        return (
            int((self.l + self.r) / 2),
            int((self.t + self.b) / 2),
        )

    def inflate_x(self, dx):
        half_dx = dx / 2
        self.l -= half_dx
        self.r += half_dx

    def inflate_y(self, dy):
        half_dy = dy / 2
        self.t -= half_dy
        self.b += half_dy

    def inflate(self, x_or_tup, y=None):
        if isinstance(x_or_tup, tuple) and len(x_or_tup) == 2:
            dx, dy = x_or_tup
        elif isinstance(x_or_tup, (int, float)) and y is not None:
            dx = x_or_tup
            dy = y
        else:
            raise ValueError("Invalid Argument")

        self.inflate_x(dx)
        self.inflate_y(dy)

    def translate(self, x_or_vec, y=None):
        if isinstance(x_or_vec, tuple) and len(x_or_tup) == 2:
            dx, dy = x_or_vec
        elif isinstance(x_or_vec, Vec2d):
            dx, dy = x_or_vec.x, x_or_vec.y
        elif isinstance(x_or_vec, (int, float)) and y is not None:
            dx, dy = x_or_vec, y
        else:
            raise ValueError("Invalid Argument")
        
        self.l += dx
        self.r += dx
        self.t += dy
        self.b += dy

    def rotate90(self):
        """
        Rotate the rect by 90 degrees
        """
        c = self.vec_center()
        w, h = self.size()
        new_pos = c - v(h / 2, w / w)
        self.set(new_pos.as_tup(), (h, w))

    def as_tup(self):
        return (self.l, self.t, self.r, self.b)

    def as_int_tup(self):
        return (int(self.l), int(self.t), int(self.r), int(self.b))

    def as_tup_tup(self):
        return self.pos(), self.size()

    def as_int_tup_tup(self):
        return self.int_pos(), self.int_size()


def rc(*arg, **kwarg):
    '''
    Utility function to make constructing rectangles more comapct
    '''
    return Rect2d(*arg, **kwarg)

# ==============================================================
# Tests
# ==============================================================

import sys
import unittest

class RectTest(unittest.TestCase):
    def test_init_empty(self):
        r = Rect2d()
        self.assertEqual(r.is_empty(), True)
        self.assertEqual(r.is_null(), False)
        self.assertEqual(r.is_infinite(), False)

    def test_init_null(self):
        r = Rect2d(init_type=Rect2d.INIT_NULL)
        self.assertEqual(r.is_empty(), False)
        self.assertEqual(r.is_null(), True)
        self.assertEqual(r.is_infinite(), False)

    def test_init_infinite(self):
        r = Rect2d(init_type=Rect2d.INIT_INFINITE)
        self.assertEqual(r.is_empty(), False)
        self.assertEqual(r.is_null(), False)
        self.assertEqual(r.is_infinite(), True)

    def test_init_values(self):
        r = Rect2d(1, 1, 2, 2)
        self.assertEqual(r.is_empty(), False)
        self.assertEqual(r.is_null(), False)
        self.assertEqual(r.is_infinite(), False)
        self.assertEqual(r.l, 1)
        self.assertEqual(r.t, 1)
        self.assertEqual(r.r, 2)
        self.assertEqual(r.b, 2)
        self.assertEqual(r.width(), 1)
        self.assertEqual(r.height(), 1)
    
    def test_init_one_tuple(self):
        vals = (1, 1, 2, 2)
        r = Rect2d(vals)
        self.assertEqual(r.is_empty(), False)
        self.assertEqual(r.is_null(), False)
        self.assertEqual(r.is_infinite(), False)
        self.assertEqual(r.l, 1)
        self.assertEqual(r.t, 1)
        self.assertEqual(r.r, 2)
        self.assertEqual(r.b, 2)
        self.assertEqual(r.width(), 1)
        self.assertEqual(r.height(), 1)

    def test_init_pair_of_tuples(self):
        pos = (1, 1)
        size = (3, 5)
        r = Rect2d(pos, size)
        self.assertFalse(r.is_empty())
        self.assertFalse(r.is_null())
        self.assertFalse(r.is_infinite())
        self.assertEqual(r.l, pos[0])
        self.assertEqual(r.t, pos[1])
        self.assertEqual(r.r, pos[0] + size[0])
        self.assertEqual(r.b, pos[1] + size[1])
        self.assertEqual(r.width(), size[0])
        self.assertEqual(r.height(), size[1])

    def test_width_height(self):
        r = Rect2d((0, 0), (5, 10))
        self.assertEqual(r.width(), 5)
        self.assertEqual(r.height(), 10)

    def test_area(self):
        r = Rect2d((0, 0), (5, 10))
        self.assertEqual(r.area(), 50)

    def test_inside(self):
        r = Rect2d((0, 0), (5, 5))
        self.assertTrue(r.is_inside(3, 3))
        self.assertFalse(r.is_inside(6, 3))
        self.assertFalse(r.is_inside(3, 6))
        self.assertTrue(r.is_inside((3, 3)))
        self.assertFalse(r.is_inside((6, 3)))
        self.assertFalse(r.is_inside((3, 6)))
        self.assertTrue(r.is_inside(v(3, 3)))
        self.assertFalse(r.is_inside(v(6, 3)))
        self.assertFalse(r.is_inside(v(3, 6)))

    def test_and(self):
        r = Rect2d(init_type=Rect2d.INIT_NULL)
        self.assertTrue(r.is_null())
        r = r & v(1, 1)
        self.assertEqual(r.l, 1)
        self.assertEqual(r.t, 1)
        self.assertEqual(r.r, 1)
        self.assertEqual(r.b, 1)
        self.assertTrue(r.is_empty())
        r = r & v(2, 2)
        self.assertFalse(r.is_empty())
        self.assertEqual(r.width(), 1)
        self.assertEqual(r.height(), 1)
        self.assertEqual(r.l, 1)
        self.assertEqual(r.t, 1)
        self.assertEqual(r.r, 2)
        self.assertEqual(r.b, 2)

    def test_or(self):
        r1 = Rect2d((0, 0), (5, 5))
        r2 = Rect2d((2, 2), (5, 5))
        r3 = Rect2d((10, 10), (5, 5))

        # Intersecting
        ri = r1 | r2
        self.assertEqual(ri.l, 2)
        self.assertEqual(ri.t, 2)
        self.assertEqual(ri.r, 5)
        self.assertEqual(ri.b, 5)

        ri = r2 | r1
        self.assertEqual(ri.l, 2)
        self.assertEqual(ri.t, 2)
        self.assertEqual(ri.r, 5)
        self.assertEqual(ri.b, 5)

        # Intersect with self
        ri = r1 | r1
        self.assertEqual(ri.l, 0)
        self.assertEqual(ri.t, 0)
        self.assertEqual(ri.r, 5)
        self.assertEqual(ri.b, 5)

        # NonIntersecting
        ri = r1 | r3
        self.assertTrue(ri.is_empty())



if __name__ == '__main__':
    unittest.main()