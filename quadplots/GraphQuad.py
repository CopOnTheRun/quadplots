from typing import Sequence, Iterable

import matplotlib
from matplotlib import pyplot
from matplotlib.animation import FuncAnimation
import numpy as np

from quadplots.Quadrature import Quadrature

class Graph:
    """Class to visualize a sequence of Quadrature Objects"""
    def __init__(self, quads: Sequence[Quadrature], layout: tuple[int,int],
            error: bool = True, **kwargs):
        self.quads = quads
        self.layout = layout
        self.fig, self.quad_axes, self.error_axes = self.create_subplots(error,**kwargs)
        self.colors = pyplot.rcParams['axes.prop_cycle'].by_key()['color']
        self.curve = self.get_curve()
        self.error = self.get_error() if error else None
        self.points = self.get_points()
        self.shapes = self.get_shapes()
        self.title = self.get_title()
        self.fig.tight_layout()

    def create_subplots(self, error: bool, **kwargs):
        """Return and possibly write to a file, a graphic representation of the Riemann sum"""
        #setting up matplotlib
        #matplotlib.rcParams['text.usetex'] = True

        num_quads = len(self.quads)
        spots = self.layout[0] * self.layout[1]

        #int cast unecessary because bool is a subclass of int, but clarity
        if num_quads + int(error) > spots:
            raise ValueError("Not enough room for all the subplots.")
        fig = pyplot.figure(**kwargs)

        quad_axes = []

        #each quadrature subplot
        for i in range(1,num_quads+1):
            quad_axes.append(fig.add_subplot(*self.layout,i))

        error_axes = None
        if error:
            error_spots = (num_quads + 1, spots)
            error_axes = fig.add_subplot(*self.layout, error_spots)

        return fig, quad_axes, error_axes

    def get_curve(self):
        """Returns the lines objects for matplotlib"""
        #this makes it so that the function curve goes past the bounds of the interval. Purely asthetics.
        quad = self.quads[0]
        overshoot = .025*abs(quad.interval.length)
        start = quad.interval.start - overshoot
        end = quad.interval.end + overshoot

        #creating function curve
        xs = np.linspace(start, end, 200)
        ys = [quad.func.func(x) for x in xs]
        label = f"$y = {quad.func.string}$" if quad.func.string else "$y=f(x)$"
        lines = []
        for ax in self.quad_axes:
            line, = ax.plot(xs,ys,color="black")
            line.set_label(label)
            lines.append(line)
        return lines

    def legend(self, axes_legend = True):
        if axes_legend:
            for ax in self.quad_axes:
                ax.legend()

        if not axes_legend:
            handles, labels = self.quad_axes[0].get_legend_handles_labels()
            self.fig.legend(handles, labels)

    def get_title(self):
        """Creates a title for the graph"""
        title_str = f"Quadrature approximation of ${self.quads[0].func.string}$"
        return self.fig.suptitle(title_str)

    def get_error(self):
        """The error lines for the difference of the actual value and the calculated value"""
        er_ax = self.error_axes
        er_ax.axhline(color="black",lw=.5)
        colors = iter(self.colors)
        lines = []
        for quad in self.quads:
            error = quad.error()
            x = len(quad.interval.partitions)
            line, = er_ax.plot(x,error,'o',color=next(colors))
            lines.append(line)

        return lines

    def get_points(self):
        """Points used for the quadrature"""
        points = []
        for quad,ax in zip(self.quads,self.quad_axes):
            point, = ax.plot(quad.points.x,quad.points.y,".",color="black")
            points.append(point)
        return points

    def get_shapes(self):
        """Return the artist shapes"""
        colors = iter(self.colors)
        artists = []
        for quad, ax in zip(self.quads, self.quad_axes):
            artists.append(quad.graph(ax,next(colors)))
        return artists

    def write(self, filename: str):
        """Write graph to a file"""
        self.fig.tight_layout()
        self.fig.savefig(filename)

class AnimatedGraph(Graph):
    def __init__(self, frames: Iterable[int], *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.frames = frames
        self.animation = self.animate()

    def anim_init(self):
        if self.error:
            x_start = min(self.frames) - 1
            x_end = max(self.frames) + 1
            min_y = self.calc_min_error()
            self.error_axes.clear()
            self.error_axes.set_xlim(x_start,x_end)
            self.error_axes.set_yscale('symlog', linthresh=min_y)

    def calc_min_error(self) -> int:
        min_y = abs(self.quads[0].error())
        max_interval = max(self.frames)
        for quad in self.quads:
            quad.interval //= max_interval
            abs_error = abs(quad.error())
            if abs_error < min_y:
                min_y = abs_error
        return min_y

    def anim_func(self, size:int):
        for ax in self.quad_axes:
            ax.clear()
        for quad in self.quads:
            quad.interval //= size

        if self.error:
            self.error = self.get_error()
        self.curve = self.get_curve()
        self.points = self.get_points()
        self.shapes = self.get_shapes()

        return *self.points, *self.shapes

    def animate(self):
        return FuncAnimation(self.fig, self.anim_func, self.frames, self.anim_init, interval=1000)

    def write(self, filename: str, *args, **kwargs):
        self.animation.save(filename,*args, **kwargs)
