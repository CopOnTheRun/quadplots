import argparse
from pathlib import Path
from typing import Callable

from matplotlib import pyplot as plt
from sympy.parsing import parse_expr
from sympy.parsing.latex import parse_latex
from sympy import Expr
from sympy.printing import latex

from quadplots.Interval import Interval, Method, AnnotatedFunction
from quadplots.Quadrature import Riemann, Trapezoid, Simpson
from quadplots.GraphQuad import Graph, AnimatedGraph

METHODS = {"mid": Method.mid,
         "left": Method.left,
         "right": Method.right,
         "max": Method.max,
         "min": Method.min,
         "rand": Method.random,}

QUADS = {"riemann": Riemann,
         "trapezoid": Trapezoid,
         "simpson": Simpson,}


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("func",
                        help = "The function to graph",
                        type = str,)

    parser.add_argument("start",
                        help = "The interval start",
                        type = int,)

    parser.add_argument("end",
                        help = "The interval end",
                        type = int,)

    parser.add_argument("--animate",
                        help = "Turns the output into a .gif based on the frames specified",
                        nargs = "+",
                        type = int,
                        metavar = "FRAME",
                        )

    parser.add_argument("--partitions",
                        help = "Number partitions in the interval",
                        type = int,
                        default = 10)

    parser.add_argument("--quad_type",
                        help = "The quadrature type",
                        choices = QUADS.keys(),
                        default = "riemann",
                        )

    parser.add_argument("--method",
                        help = "The method type, only works with riemann sums",
                        choices = METHODS.keys(),
                        default = "midpoint",
                        )

    parser.add_argument("--latex",
                        help = "Pass if the func str in latex",
                        action = "store_true",
                        )

    parser.add_argument("--out",
                        help = "The file to save to",
                        type = Path,
                        default = Path("quadrature.svg"),
                        )

    return parser.parse_args()

def sympy_to_func(expr: Expr) -> Callable[[float], float]:
    syms = expr.free_symbols
    sym = syms.pop()
    return lambda x: float(expr.subs(sym, x).evalf())

def main():
    args = get_args()
    plt.style.use("ggplot")
    sympy_func = parse_latex(args.func) if args.latex else parse_expr(args.func)
    f = sympy_to_func(sympy_func)
    F = sympy_to_func(sympy_func.integrate())
    func = AnnotatedFunction(f, latex(sympy_func), F)

    interval = Interval(args.start, args.end,) // args.partitions

    method = METHODS[args.method]()

    quad = QUADS[args.quad_type](func, interval, method)
    if frames := args.animate:
        anim = AnimatedGraph(frames, [quad], (1,1), error=False)
        stem = args.out.stem
        anim.write(stem + ".gif", dpi = 300)
    else:
        g = Graph([quad],(1,1),error=False)
        g.write(args.out)

if __name__ == "__main__":
    main()
