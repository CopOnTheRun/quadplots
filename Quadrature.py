#!/usr/bin/env python3

"""
Module used to create and visulize Riemann sums.

Goals:
    * I'm learning about the factory method, and because there are different implementations with the same interface, it seems like this module could be a good way to practice the factory method pattern.
    * refresher+practice with matplotlib or whatever plotting library I choose to work with
    * replicate the picture on the wikipedia page for Riemann sums
    * upload said picture to wikipedia in svg format (current is jpg I think)
"""

from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Iterable
from itertools import zip_longest

import numpy as np
import matplotlib

from Interval import AnnotatedFunction, Interval, Method, Point, Points

class Quadrature(ABC):
    """Abstract base class for methods of numerical integration which partition an interval into subintervals in order to calculate a definite intergral of a function."""

    def __init__(self, func: AnnotatedFunction, interval: Interval, method: Method) -> None:
        self.func = func
        self.interval = interval
        self.method = method

    @property
    def points(self) -> Points:
        return Points([self.method.choose(self.func.func,p) for p in self.interval])

    @property
    @abstractmethod
    def areas(self) -> list[float]:
        """Returns a list of areas based on the partitions calculated for each interval"""

    def calc(self) -> float:
        """The calculated output of the method used to approximate the function."""
        return sum(self.areas)

    def error(self) -> float:
        if (integral := self.func.integral):
            calculated = self.calc()
            actual = integral(self.interval.end) - integral(self.interval.start)
            return (calculated-actual)/actual
        raise ValueError("No integral was provided for this function.")

    @abstractmethod
    def graph(self, ax: matplotlib.axes.Axes, color: str = None) -> None:
        """Takes a matplotlib axes and graphs the instance's shapes onto the axes"""

class Riemann(Quadrature):

    @property
    def areas(self) -> list[float]:
        areas: list[float] = []
        for partition, y in zip(self.interval, self.points.y):
            areas.append(partition.length * y)
        return areas

    def graph(self, ax: matplotlib.axes.Axes, color=None) -> matplotlib.axes.Axes:
        """Return and possibly write to a file, a graphic representation of the Riemann sum"""
        #creating the bars
        starts = [x.start for x in self.interval]
        lengths = [x.length for x in self.interval]
        ys = self.points.y
        ax.bar(starts, ys, width=lengths, align="edge",color=color, edgecolor="black", linewidth=.5)

class Trapezoid(Quadrature):

    def __init__(self, func: AnnotatedFunction, interval: Interval):
        super().__init__(func, interval, Method.left())

    @property
    def points(self) -> Points:
        """The same as super, but add an endpoint"""
        x = self.interval.end
        y = self.func.func(x)
        return Points(super().points.points + [Point(x,y)])

    @property
    def areas(self) -> list[float]:
        areas: list[float] = []
        for partition in self.interval:
            h = partition.length
            a = self.func.func(partition.start)
            b = self.func.func(partition.end)
            areas.append((a+b)/2*h)
        return areas

    def graph(self, ax: matplotlib.axes.Axes, color: str = None) -> None:
        for point in self.points:
            ax.vlines(point.x,0,point.y,color="black",lw=.5)
        ax.plot(self.points.x,self.points.y,lw=.5,color="black")
        ax.fill_between(self.points.x,self.points.y,color=color)
        ax.hlines(0,self.interval.start,self.interval.end,lw=.5,color="black")

class Simpson(Quadrature):
    def __init__(self, func: AnnotatedFunction, interval: Interval) -> None:
        if len(interval.partitions) % 2 != 0:
            message = "Simson's rule only works with an even number of partitions."
            raise ValueError(message)
        super().__init__(func, interval, Method.left())

    @property
    def points(self) -> Points:
        """The same as super, but add an endpoint"""
        x = self.interval.end
        y = self.func.func(x)
        return Points(super().points.points + [Point(x,y)])

    def parabolas(self) -> list[tuple[float,float,float]]:
        parabolas = []
        for p0,p1 in chunk_iter(self.interval,2):
            y0 = self.func.func(p0.start)
            y1 = self.func.func(p1.start)
            y2 = self.func.func(p1.end)
            h = p0.end - p0.start
            k = p1.end - p1.start
            #I'll have to add the derivation to the docs, but it's the same
            #as the textbook example, but things don't come out as nicely.
            A: float = (h*(y2-y1)+k*(y0-y1))/(h*k*(h+k))
            B: float = (h**2*(y2-y1) + k**2*(y1-y0))/(h*k*(h+k))
            C: float = y1
            parabolas.append((A,B,C))
        return parabolas

    @property
    def areas(self) -> list[float]:
        areas: list[float] = []
        parabs = iter(self.parabolas())
        for p0,p1 in chunk_iter(self.interval,2):
            A,B,C = next(parabs)
            h = p0.end - p0.start
            k = p1.end - p1.start
            areas.append(1/3*A*(k**3+h**3) + 1/2*B*(k**2-h**2) + C*(k+h))
        return areas

    def graph(self, ax: matplotlib.axes.Axes, color: str = None) -> None:
        parabs = iter(self.parabolas())
        for point in self.points:
            ax.vlines(point.x,0,point.y,color="black",lw=.5)

        for par0,par1 in chunk_iter(self.interval,2):
            x = np.linspace(par0.start,par1.end)
            h = par0.end - par0.start
            k = par1.end - par1.start
            p = np.linspace(-h,k)
            A,B,C = next(parabs)
            y = A*p**2 + B*p + C
            #parabola arcs
            ax.plot(x,y,lw=.5,color = "black")
            #parabola fill
            ax.fill_between(x,y,color=color)

        ax.hlines(0,self.interval.start,self.interval.end,lw=.5,color="black")

def chunk_iter(iters: Iterable[Any], chunk_size: int) -> Any:
    chunks = [iter(iters)] * chunk_size
    return zip_longest(*chunks)

