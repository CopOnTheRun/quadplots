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
from typing import Optional

import numpy as np
import matplotlib
from matplotlib import pyplot

from Interval import Function, Interval, Method, Point

class Quadrature(ABC):
    """Abstract base class for methods of numerical integration which partition an interval into subintervals in order to calculate a definite intergral of a function."""

    def __init__(self, func: Function, interval: Interval, method: Method) -> None:
        self.func = func
        self.interval = interval
        self.method = method

    @property
    def points(self) -> list[Point]:
        return [self.method.choose(self.func,p) for p in self.interval]

    @abstractmethod
    def calc(self) -> float:
        """The calculated output of the method used to approximate the function."""

class Riemann(Quadrature):
    """A function on an interval. Take the sum using a certain method."""
    def calc(self) -> float:
        total: float = 0

        for partition, point, in zip(self.interval, self.points):
            total += partition.length * point.y

        return total

    def graph(self, file_name: Optional[str] = None) -> matplotlib.axes.Axes:
        """Return and possibly write to a file, a graphic representation of the Riemann sum"""
        #setting up matplotlib
        matplotlib.use("svg")
        pyplot.style.use("seaborn")

        #creating the figure
        fig = pyplot.figure()
        ax = fig.add_subplot(1,1,1)

        #this makes it so that the function curve goes past the bounds of the interval. Purely asthetics.
        overshoot = .025*abs(self.interval.length)
        start = self.interval.start - overshoot
        end = self.interval.end + overshoot

        #creating function curve
        x = np.linspace(start, end, 200)
        y = self.func(x)
        ax.plot(x,y,color="black")

        #plotting the points used for quadrature
        x_coor, y_coor = zip(*self.points)
        ax.plot(x_coor,y_coor,".",color="black")

        #creating the bars
        starts = [x.start for x in self.interval]
        lengths = [x.length for x in self.interval]
        ax.bar(starts, y_coor, width=lengths, align="edge", edgecolor="black", linewidth=.5)

        fig.tight_layout()

        if file_name:
            fig.savefig(file_name)

        return fig

class Trapezoid(Quadrature):

    def __init__(self, func: Function, interval: Interval):
        super().__init__(func, interval, Method.left())

    @property
    def points(self) -> list[Point]:
        """The same as super, but add an endpoint"""
        x = self.interval.end
        y = self.func(x)
        return super().points + [Point(x,y)]

    def calc(self) -> float:
        total: float = 0
        for partition in self.interval:
            h = partition.length
            a = self.func(partition.start)
            b = self.func(partition.end)
            total += (a+b)/2*h
        return total

    def graph(self) -> matplotlib.axes.Axes:
        raise NotImplementedError("It's on the TODO list")
