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
from matplotlib import pyplot

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

    @abstractmethod
    def graph(self, ax: matplotlib.axes.Axes) -> None:
        """Takes a matplotlib axes and graphs the instance's shapes onto the axes"""

class Riemann(Quadrature):

    @property
    def areas(self) -> list[float]:
        areas: list[float] = []
        for partition, y in zip(self.interval, self.points.y):
            areas.append(partition.length * y)
        return areas

    def graph(self, ax: matplotlib.axes.Axes) -> matplotlib.axes.Axes:
        """Return and possibly write to a file, a graphic representation of the Riemann sum"""
        #creating the bars
        starts = [x.start for x in self.interval]
        lengths = [x.length for x in self.interval]
        ys = self.points.y
        ax.bar(starts, ys, width=lengths, align="edge", edgecolor="black", linewidth=.5)

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

    def graph(self, ax: matplotlib.axes.Axes) -> None:
        """Return and possibly write to a file, a graphic representation of the Riemann sum"""
        for point in self.points:
            ax.vlines(point.x,0,point.y,color="black",lw=.5)
        traps = ax.plot(self.points.x,self.points.y,lw=.5,color="black")
        ax.fill_between(self.points.x,self.points.y)
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
        size = self.interval[0].length
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

    def graph(self, ax: matplotlib.axes.Axes) -> None:
        parabs = iter(self.parabolas())
        colors = matplotlib.rcParams['axes.prop_cycle'].by_key()['color']
        for point in self.points:
            ax.vlines(point.x,0,point.y,color="black",lw=.5)

        for par0,par1 in chunk_iter(self.interval,2):
            x = np.linspace(par0.start,par1.end)
            h = par0.end - par0.start
            k = par1.end - par1.start
            p = np.linspace(-h,k)
            A,B,C = next(parabs)
            y = A*p**2 + B*p + C
            ax.plot(x,y,lw=.5,color="black")
            ax.fill_between(x,y,color=colors[0])

        ax.hlines(0,self.interval.start,self.interval.end,lw=.5,color="black")

def chunk_iter(iters: Iterable[Any], chunk_size: int) -> Any:
    chunks = [iter(iters)] * chunk_size
    return zip_longest(*chunks)

def graph(quad: Quadrature, file_name: str = None) -> matplotlib.axes.Axes:
    """Return and possibly write to a file, a graphic representation of the Riemann sum"""
    #setting up matplotlib
    matplotlib.use("svg")
    pyplot.style.use("seaborn")
    matplotlib.rcParams['text.usetex'] = True

    #creating the figure
    fig = pyplot.figure()
    ax = fig.add_subplot(1,1,1)

    #this makes it so that the function curve goes past the bounds of the interval. Purely asthetics.
    overshoot = .025*abs(quad.interval.length)
    start = quad.interval.start - overshoot
    end = quad.interval.end + overshoot

    #creating function curve
    x = np.linspace(start, end, 200)
    y = quad.func.func(x)
    label = f"$y = {quad.func.string}$" if quad.func.string else "$y=f(x)$"
    ax.plot(x, y, color="black", label=label)
    ax.legend()

    #plotting the points used for quadrature
    ax.plot(quad.points.x,quad.points.y,".",color="black")

    #creating the shapes
    quad.graph(ax)

    fig.tight_layout()

    if file_name:
        fig.savefig(file_name)

    return fig
