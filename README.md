# quadplots

The `quadplots` program is an educational utility to create visualizations of basic quadrature methods. The current methods supported are Riemann sum (left, right, mid, max, min), Trapezoid rule, and Simpson's rule.

## Usage

Basic usage of quadplots only requires an expression you want to graph (must be valid python), and the start and end points.

```
quadplots "x**2 - 3*x + 1" -2 3 
```

![](https://github.com/CopOnTheRun/quadplots/raw/main/images/basic_example.svg)

By default quadplots will graph a riemann sum with n=10 and use the midpoint method, but you can easily change these options.

```
quadplots "x**2 - 3*x + 1" -2 3 --method min --partitions 5
```


![](https://github.com/CopOnTheRun/quadplots/raw/main/images/min_example.svg)

You can also change the type of quadrature method used

```
quadplots "x**3 - 8*x + 7" -2 3 --method min --partitions 4 --quad-type simpson 
```
![](https://github.com/CopOnTheRun/quadplots/raw/main/images/simpson_example.svg)

If you want, instead of python functions, you can write latex by adding the `--latex` flag to the command.

```
quadplots "\exp{-x^{2}}" -2 4 --partitions 4 --quad_type simpson --latex
```
![](https://github.com/CopOnTheRun/quadplots/raw/main/images/latex_example.svg)

Finally, if you wish to animate the plot, you can pass `--animate` with a list of partitions you would like to see at each frame.

```
quadplots "\exp{-x^{2}}" -2 4 --partitions 4 --quad_type simpson --latex --animate 2 4 6 10 100
```
![](https://github.com/CopOnTheRun/quadplots/raw/main/images/animation_example.gif)
