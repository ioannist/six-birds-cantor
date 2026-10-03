"""Outward rational intervals for mathematical certificates.

Every arithmetic endpoint is rounded outwards to a fixed rational grid.
Square roots use integer square roots; logarithms use a rational power
series with an explicit positive remainder. No floating-point transcendental
routine participates in a certificate.
"""
from dataclasses import dataclass
from fractions import Fraction as Q
from math import isqrt

GRID = 10**25


def _down(x):
    return Q(x.numerator*GRID//x.denominator, GRID)


def _up(x):
    return -_down(-x)


@dataclass(frozen=True)
class Interval:
    lo: Q
    hi: Q

    def __init__(self, lo, hi=None):
        lo=Q(lo); hi=lo if hi is None else Q(hi)
        if lo>hi:
            raise ValueError("reversed interval")
        object.__setattr__(self,"lo",lo)
        object.__setattr__(self,"hi",hi)

    @staticmethod
    def rounded(lo,hi):
        return Interval(_down(lo),_up(hi))

    def __add__(self, other):
        other=as_interval(other)
        return self.rounded(self.lo+other.lo,self.hi+other.hi)
    __radd__=__add__

    def __neg__(self):
        return Interval(-self.hi,-self.lo)

    def __sub__(self,other):
        return self+-as_interval(other)

    def __rsub__(self,other):
        return as_interval(other)+-self

    def __mul__(self,other):
        other=as_interval(other)
        p=[a*b for a in (self.lo,self.hi) for b in (other.lo,other.hi)]
        return self.rounded(min(p),max(p))
    __rmul__=__mul__

    def __truediv__(self,other):
        other=as_interval(other)
        if other.lo<=0<=other.hi:
            raise ValueError("division interval contains zero")
        return self*self.rounded(1/other.hi,1/other.lo)

    def __rtruediv__(self,other):
        return as_interval(other)/self

    def square(self):
        lo=0 if self.lo<=0<=self.hi else min(self.lo**2,self.hi**2)
        return self.rounded(Q(lo),max(self.lo**2,self.hi**2))

    def abs(self):
        lo=0 if self.lo<=0<=self.hi else min(abs(self.lo),abs(self.hi))
        return Interval(lo,max(abs(self.lo),abs(self.hi)))

    def sqrt(self):
        if self.lo<0:
            raise ValueError("negative square-root interval")
        def floor_root(x):
            return isqrt(x.numerator*GRID**2//x.denominator)
        a,b=floor_root(self.lo),floor_root(self.hi)
        # An exact endpoint does not need the additional upper grid unit.
        upper=Q(b,GRID) if Q(b,GRID)**2==self.hi else Q(b+1,GRID)
        return Interval(Q(a,GRID),upper)

    def log(self):
        if self.lo<=0:
            raise ValueError("nonpositive logarithm interval")
        return Interval(_log_point(self.lo).lo,_log_point(self.hi).hi)

    def exp(self):
        return Interval(_exp_point(self.lo).lo,_exp_point(self.hi).hi)

    def clamp(self,lo,hi):
        lo,hi=Q(lo),Q(hi)
        return Interval(max(lo,min(hi,self.lo)),max(lo,min(hi,self.hi)))


def as_interval(value):
    return value if isinstance(value,Interval) else Interval(value)


def maximum(*values):
    values=[as_interval(v) for v in values]
    return Interval(max(v.lo for v in values),max(v.hi for v in values))


def minimum(*values):
    values=[as_interval(v) for v in values]
    return Interval(min(v.lo for v in values),min(v.hi for v in values))


def _log_series(y):
    # 1 <= y <= 2, t <= 1/3. Truncate after 60 terms.
    t=(as_interval(y)-1)/(as_interval(y)+1)
    power=t; total=Interval(0)
    for k in range(60):
        total=total+2*power/Q(2*k+1)
        power=power*t.square()
    remainder=2*power/(Q(121)*(1-t.square()))
    return Interval(total.lo,total.hi+remainder.hi)


_LOG_TWO=None


def _log_point(x):
    global _LOG_TWO
    exponent=0
    while x<1:
        x*=2; exponent-=1
    while x>2:
        x/=2; exponent+=1
    if _LOG_TWO is None:
        _LOG_TWO=_log_series(Q(2))
    return _log_series(x)+exponent*_LOG_TWO


def _exp_point(x):
    if x<0:
        return 1/_exp_point(-x)
    halvings=0
    while x>1:
        x/=2; halvings+=1
    power=Interval(1)
    total=power
    for k in range(1,61):
        power=power*x/k
        total=total+power
    # Taylor's remainder: exp(x) <= 3 for 0 <= x <= 1.
    remainder=3*power*x/61
    result=Interval(total.lo,total.hi+remainder.hi)
    for _ in range(halvings):
        result=result.square()
    return result
