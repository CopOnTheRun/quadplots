from __future__ import annotations
from functools import wraps
from random import uniform
from typing import NamedTuple, TypeVar, Any, Optional
from collections.abc import Callable, Iterator
from dataclasses import dataclass

class Point(NamedTuple):
    """Class representing a point on a 2-dimensional plane"""
    #I think this is marginally better than a dataclass or regular class
    x: float
    y: float

@dataclass
class Points:
    points: list[Point]

    @property
    def y(self) -> list[float]:
        return [point.y for point in self.points]

    @property
    def x(self) -> list[float]:
        return [point.x for point in self.points]

    def __getitem__(self, item: Any) -> Point:
        return self.points[item]

def recursive(meth: M) -> M:
    @wraps(meth)
    def wrapper(self: Interval, *args: Any, **kwargs: Any) -> Interval:
        new_parts: list[Interval] = []
        for p in self.partitions:
            if p.partitions:
                new_parts.append(wrapper(p, *args, **kwargs))
            else:
                new_parts.append(meth(p, *args, **kwargs))

        new_interval = meth(self, *args, **kwargs)
        new_interval.partitions = new_parts
        return new_interval
    return wrapper

class Interval:
    """Interval, composed of a start, end, and partitions."""
    def __init__(
        self,
        start: float,
        end: float,
        partitions: Optional[Partition] = None) -> None:

        self.start: float = start
        self.end: float = end
        if partitions:
            self.partitions: Partition = partitions
        else:
            self.partitions = []

    @property
    def length(self) -> float:
        """Returns the lazily calulated length of the Interval instance"""
        return self.end - self.start

    @property
    def mid(self) -> float:
        return self.start + self.length * .5

    def partition(
        self,
        num: int,
        scheme: Function = lambda x: 1,
        ) -> list[Interval]:
        """First we space the points out the way we want, then we scale the points to fit the interval length, then we shift the points to the interval position. I call it the ole space-scale-shift."""

        spaced: Partition = self._space(self.start, self.end, num, scheme)
        scale_factor = self.length/(spaced[-1].end - spaced[0].start)
        scaled: Partition = self._scale(scale_factor,spaced)
        shift_factor = self.start - scaled[0].start
        shifted: Partition = self._shift(shift_factor,scaled)
        return shifted

    @staticmethod
    def _space(start: float, end: float, num: int, scheme: Function) -> Partition:
        #it's important to start with 1 so simple things like x**2 don't give a partition size of 0. That's not to say (x-1)**2 won't though!
        partition = [Interval(start,start+scheme(1))]
        for x in range(2,num+1):
            start = partition[-1].end
            end = start + scheme(x)
            partition.append(Interval(start,end))

        return partition

    @staticmethod
    def _scale(size: float, partition: Partition,) -> Partition:
        start = partition[0].start
        new_end = start + partition[0].length*size
        scaled = [Interval(start,new_end)]

        for p in partition[1:]:
            start = scaled[-1].end
            end = start+p.length*size
            scaled.append(Interval(start,end))
        return scaled

    @staticmethod
    def _shift(shift: float, partitions: Partition) -> Partition:
        return [Interval(x.start+shift,x.end+shift) for x in partitions]

    @recursive
    def __add__(self, other: float) -> Interval:
        """Shift an interval and all subintervals by some amount."""
        return type(self)(self.start+other, self.end+other)
    def __sub__(self, other: float) -> Interval:
        """Shift an interval and all subintervals by some amount."""
        return self + -other

    def __mul__(self, other: float) -> Interval:
        """Need to make recursive, but I can't just slap the @recursive decorator on yet, I've got to probably restructure the class"""

        new_parts = []
        if self.partitions:
            new_parts = self._scale(other,self.partitions)

        return type(self)(self.start,self.start+self.length*other,new_parts)

    def __truediv__(self, other: float) -> Interval:
        return self*(1/other)

    def __floordiv__(self, num: int) -> Interval:
        """Returns the current interval partitioned into num partitions. Probably an abuse of operator overloading but the floordiv symbol just looks like a partition so I had to."""
        partitions = self.partition(num)
        return type(self)(self.start,self.end,partitions)

    def __mod__(self, other: Function) -> Interval:
        num = len(self.partitions)
        new_partitions = self.partition(num,other)
        return type(self)(self.start,self.end,new_partitions)

    def __eq__(self, other: object) -> bool:
        """Equal if all partitions are the same. Need to make recursive."""
        if not isinstance(other, Interval):
            return NotImplemented

        if self.start != other.start or self.end != other.end:
            return False
        else:
            return True


    def __repr__(self) -> str:
        """repr for Interval. Need to make recursive?"""
        return f"Interval({self.start},{self.end})"

    def __str__(self, level: int = 0) -> str:
        """Recursive string representation of Interval"""

        string = f"{'  '*level}[{self.start:.3g},{self.end:.3g}]\n"
        level += 1
        for x in self.partitions:
            if x.partitions:
                string += x.__str__(level)
            else:
                string += f"{'  '*level}[{x.start:.3g},{x.end:.3g}]\n"
        return string

    def __iter__(self) -> Iterator[Interval]:
        return self.partitions.__iter__()

    def __getitem__(self, key: int) -> Interval:
        return self.partitions[key]

    def __setitem__(self, key: int, value: Interval) -> None:
        self.partitions[key] = value

class Method:
    def __init__(self, chooser: PointGetter) -> None:
        self.chooser = chooser

    def choose(self, f: Function, i: Interval) -> Point:
        return self.chooser(f,i)

    @classmethod
    def max(cls) -> Method:
        def get_max(f: Function, interval: Interval) -> Point:
            """Splits the interval into 101 Points, then returns the Point with the max y value."""
            points = [Point(i.start,f(i.start)) for i in interval // 100]

            #very important last point gets added as it's usually the max/min point on the interval
            points.append(Point(interval.end,f(interval.end)))
            use_y: Callable[[Point], float]= lambda point: point.y.real
            return max(points, key=use_y)
        return cls(get_max)

    @classmethod
    def min(cls) -> Method:
        def get_min(f: Function, interval: Interval) -> Point:
            """Splits the interval into 101 Points, then returns the Point with the min y value."""
            points = [Point(i.start,f(i.start)) for i in interval // 100]

            #very important last point gets added as it's usually the max/min point on the interval
            points.append(Point(interval.end,f(interval.end)))
            use_y: Callable[[Point], float] = lambda point: point.y.real
            return min(points, key=use_y)
        return cls(get_min)

    @classmethod
    def left(cls) -> Method:
        """Returns the leftmost point in the interval"""
        method: PointGetter = lambda f,i : Point(i.start,f(i.start))
        return cls(method)

    @classmethod
    def mid(cls) -> Method:
        method: PointGetter = lambda f,i : Point(i.mid,f(i.mid))
        return cls(method)

    @classmethod
    def right(cls) -> Method:
        """Returns the rightmost point in the interval"""
        method: PointGetter = lambda f,i : Point(i.end,f(i.end))
        return cls(method)

    @classmethod
    def random(cls) -> Method:
        def get_rand(f: Function, i: Interval) -> Point:
            x = uniform(i.start,i.end)
            return Point(x,f(x))

        return cls(get_rand)

@dataclass
class AnnotatedFunction:
    func: Function
    string: Optional[str] = None
    integral: Optional[Function] = None

Function = Callable[[float],float]
PointGetter = Callable[[Function, Interval], Point]
Partition = list[Interval]
M = TypeVar("M", bound=Callable[..., Interval])
