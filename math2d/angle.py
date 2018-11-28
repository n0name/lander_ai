import math

class Angle:
    def __init__(self, *, deg=None, rad=None):
        if deg is not None and rad is not None:
            raise ValueError("Set either deg or rad")
        
        if deg is not None:
            if isinstance(deg, (int, float)):
                self.val = math.radians(deg)
            else:
                raise ValueError("Enter int or float")
        elif rad is not None:
            if isinstance(rad, (int, float)):
                self.val = rad
            else:
                raise ValueError("Enter int or float")

        else:
            raise ValueError("Enter either deg or rad")

    @property
    def deg(self):
        return math.degrees(self.val)

    @deg.setter
    def deg(self, val):
        self.val = math.radians(val)

    @property
    def rad(self):
        return self.val
    
    @rad.setter
    def rad(self, val):
        self.val = val