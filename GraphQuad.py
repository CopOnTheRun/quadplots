import matplotlib
from matplotlib import pyplot
import numpy as np
from typing import Sequence, Optional, Iterable

from Quadrature import Quadrature

class Graph:
    def __init__(self, quads: Sequence[Quadrature],
            layout: tuple[int,int], style: str = "seaborn"):
        self.quads = quads
        self.style = style
        self.layout = layout
        self.fig, self.axes = self.background()
        self.colors = pyplot.rcParams['axes.prop_cycle'].by_key()['color']

    def background(self):
        """Return and possibly write to a file, a graphic representation of the Riemann sum"""
        #setting up matplotlib
        pyplot.style.use(self.style)
        #matplotlib.rcParams['text.usetex'] = True

        #creating the figure
        fig = pyplot.figure()
        num_quads = len(self.quads)
        for i in range(1,num_quads+1):
            fig.add_subplot(*self.layout,i)

        return fig, fig.axes

    def curve(self):
        #this makes it so that the function curve goes past the bounds of the interval. Purely asthetics.
        quad = self.quads[0]
        overshoot = .025*abs(quad.interval.length)
        start = quad.interval.start - overshoot
        end = quad.interval.end + overshoot

        #creating function curve
        x = np.linspace(start, end, 200)
        y = quad.func.func(x)
        label = f"$y = {quad.func.string}$" if quad.func.string else "$y=f(x)$"
        for ax in self.axes:
            line, = ax.plot(x,y,color="black")
            line.set_label(label)
            ax.legend()

    def error(self):
        if len(self.quads) >= self.layout[0]*self.layout[1]:
            raise ValueError("Need a place to put the error graph.")
        er_ax = self.fig.add_subplot(*self.layout,len(self.axes)+1)
        er_ax.axhline(color="black",lw=.5)
        colors = iter(self.colors)
        for i, quad in enumerate(self.quads):
            y = quad.error()
            er_ax.bar(i,y,width=1,color=next(colors))

    def points(self):
        #plotting the points used for quadrature
        for quad,ax in zip(self.quads,self.axes):
            ax.plot(quad.points.x,quad.points.y,".",color="black")

    def quadrature(self, colors: Optional[Iterable[str]] = None):
        if colors:
            self.colors = colors
        colors = iter(self.colors)
        for quad, ax in zip(self.quads, self.axes):
            quad.graph(ax,next(colors))

    def write(self, filename: str):
        self.fig.tight_layout()
        self.fig.savefig(filename)

def graph(quad: Quadrature, color = None, filename: str = None):
    graph = Graph(quad)
    graph.curve()
    graph.points()
    graph.quadrature(color)

    if filename:
        graph.write(filename)

    return graph.fig
