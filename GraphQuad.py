import matplotlib
from matplotlib import pyplot
import numpy as np

from Quadrature import Quadrature

class Graph:
    def __init__(self, quad: Quadrature):
        self.quad = quad
        self.fig, self.ax = self.background()

    def background(self):
        """Return and possibly write to a file, a graphic representation of the Riemann sum"""
        #setting up matplotlib
        matplotlib.use("svg")
        pyplot.style.use("seaborn")
        #matplotlib.rcParams['text.usetex'] = True

        #creating the figure
        fig = pyplot.figure()
        ax = fig.add_subplot(1,1,1)
        fig.tight_layout()
        return fig, ax

    def curve(self):
        #this makes it so that the function curve goes past the bounds of the interval. Purely asthetics.
        overshoot = .025*abs(self.quad.interval.length)
        start = self.quad.interval.start - overshoot
        end = self.quad.interval.end + overshoot

        #creating function curve
        x = np.linspace(start, end, 200)
        y = self.quad.func.func(x)
        line, =  self.ax.plot(x, y, color="black")

        #legend and line label
        label = f"$y = {self.quad.func.string}$" if self.quad.func.string else "$y=f(x)$"
        line.set_label(label)
        self.ax.legend()
        return line

    def points(self):
        #plotting the points used for quadrature
        return self.ax.plot(self.quad.points.x,self.quad.points.y,".",color="black")

    def quadrature(self):
        return self.quad.graph(self.fig.axes[0])

    def write(self, filename: str):
        self.fig.savefig(filename)

def graph(quad: Quadrature, filename: str = None):
    graph = Graph(quad)
    graph.curve()
    graph.points()
    graph.quadrature()

    if filename:
        graph.write(filename)

    return graph.fig
