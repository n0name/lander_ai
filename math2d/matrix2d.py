import operator
import math

if __name__ == '__main__':
    from vec2d import *
else:
    from .vec2d import *

class Matrix2d:
    __slots__ = ['m', 'n', 'data']

    def __init__(self, m, n, data=None):
        self.m = m
        self.n = n
        if data is not None:
            if len(data) == m * n:
                self.data = data
            else:
                raise ValueError("Invalid data given")
        else:
            self.data = [0] * (m * n)

    def __len__(self):
        return self.m * self.n

    def __str__(self):
        def row(i):
            return " ".join(str(d) for d in self.data[i * self.n: (i + 1) * self.n])
        return "\n".join(row(i) for i in range(self.m))

    def __getitem__(self, key):
        if len(key) > 2:
            raise ValueError("Dimmension out of bounds")
        if len(key) == 2:
            if isinstance(key[0], slice):
                if isinstance(key[1], slice):
                    idc_i = key[0].indices(self.m)
                    idc_j = key[1].indices(self.n)
                    new_m = (idc_i[1] - idc_i[0]) // idc_i[2]
                    new_n = (idc_j[1] - idc_j[0]) // idc_j[2]
                    new_data = [0] * (new_m * new_n)
                    for ni, i in enumerate(range(*idc_i)):
                        for nj, j in enumerate(range(*idc_j)):
                            new_data[ni * new_n + nj] = self.data[i * self.n + j]
                    return Matrix2d(new_m, new_n, new_data)
                else:
                    res = []
                    for i in range(*key[0].indices(self.m)):
                        res.append(self.data[i * self.n + key[1]])
                    return res
            else:
                if isinstance(key[1], slice):
                    res = []
                    for j in range(*key[1].indices(self.n)):
                        res.append(self.data[key[0] * self.n + j])
                    return res
                else:
                    i, j = key
                    if i > self.m or j > self.n:
                        raise ValueError("Index Out of bounds")
                    else:
                        return self.data[i * self.n + j]

    def __setitem__(self, key, value):
        if len(key) > 2:
            raise ValueError("Dimmension out of bounds")
        if len(key) == 2:
            if isinstance(key[0], slice):
                if isinstance(key[1], slice):
                    for i in range(*key[0].indices(self.m)):
                        for j in range(*key[1].indices(self.n)):
                            self.data[i * self.n + j] = value
                else:
                    for i in range(*key[0].indices(self.m)):
                        self.data[i * self.n + key[1]] = value
            else:
                if isinstance(key[1], slice):
                    for j in range(*key[1].indices(self.n)):
                        self.data[key[0] * self.n + j] = value
                else:
                    i, j = key
                    if i > self.m or j > self.n:
                        raise ValueError("Index Out of bounds")
                    else:
                        self.data[i * self.n + j] = value

    def __mul__(self, other):
        if isinstance(other, Matrix2d):
            if self.n != other.m:
                raise ValueError("Matrices can be multiplied only if A_n == B_m")
            new_data = [0] * (self.m * other.n)
            for i in range(self.m):
                for j in range(other.n):
                    for k in range(self.n): # the same as other.m
                        new_data[i * other.n + j] += self[i, k] * other[k, j]

            return Matrix2d(self.m, other.n, new_data)

        elif isinstance(other, Vec2d):
            if self.n != 2:
                raise ValueError("Invalid transformation matrix for 2D vector")
            
            return v( sum(self[:, 0]) * other.x, sum(self[:, 1]) * other.y )

        elif isinstance(other, (int, float)):
            new_data = [0] * (self.m * self.n)
            for i in range(self.m):
                for j in range(self.n):
                    new_data = self[i, j] * other
            return Matrix2d(self.m, self.n, new_data)
        else:
            raise ValueError("Invalid value")

    def __imul__(self, other):
        if isinstance(other, (int, float)):
            for i in range(self.m):
                for j in range(self.n):
                    self[i, j] = self[i, j] * other
        else:
            raise ValueError("Invalid value")

        return self

    def __add__(self, other):
        if isinstance(other, Matrix2d):
            if self.m != other.m or self.n != other.n:
                raise ValueError("Matrices must have the same dimmensions")
            new = self.copy()
            for i in range(self.m):
                for j in range(self.n):
                    new[i, j] = self[i, j] + other[i, j]
            return new
        elif isinstance(other, (int, float)):
            new = self.copy()
            for i in range(self.m):
                for j in range(self.n):
                    new[i, j] = self[i, j] + other
            return new
        else:
            raise ValueError("Invalid value")
    __radd__ = __add__

    def __iadd__(self, other):
        if isinstance(other, Matrix2d):
            if self.m != other.m or self.n != other.n:
                raise ValueError("Matrices must have the same dimmensions")
            for i in range(self.m):
                for j in range(self.n):
                    self[i, j] = self[i, j] + other[i, j]
            return self
        elif isinstance(other, (int, float)):
            for i in range(self.m):
                for j in range(self.n):
                    self[i, j] = self[i, j] + other
            return self
        else:
            raise ValueError("Invalid value")




    def determinant(self):
        raise NotImplementedError()

    def copy(self):
        return Matrix2d(self.m, self.n, self.data.copy())

    def transpose(self):
        new_data = [0] * (self.m * self.n)
        for i in range(self.m):
            for j in range(self.n):
                new_data[i * self.n + j] = self.data[j * self.n + i]

        self.data = new_data
        self.m, self.n = self.n, self.m # swap m and n

    def transposed(self):
        temp = Matrix2d(self.m, self.n, self.data)
        temp.transpose()
        return temp


if __name__ == '__main__':
    # m = Matrix2d(4, 3, [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12])
    m = Matrix2d(5, 5)
    print(m)
    print('=' * 20)
    m[:, 1] = 2
    m[2, :] = 3
    m[:2, 3:5] = 9
    m[4, 0] = 6
    m *= 2
    m += 3
    print(m)
    print('=' * 20)
    print(m.transposed())