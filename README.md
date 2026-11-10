# `plotis`
`plotis` is a plot isolation tool for Python. It saves the data and Python code needed to reproduce a plot independently, using a pythonic interface.

This project started as a fix for repositories that balloon in size in documentation projects where images are updated often. The most common image formats are not plain text, so Git cannot version them efficiently and stores every version of every image. Instead of converting images to a plain-text format or pruning the Git history, I chose to overengineer this solution: a Python context manager extracts the code and data needed to reproduce each plot.

# Installation
```bash
pip install plotis
```

# Usage
## Simple example
`plotis` relies on the context manager `PlotIs`. Put the plotting logic inside a `PlotIs` context and pass it the data used for plotting, as shown below. On exit, `PlotIs` creates a folder containing the data (`<figfoldername>/data.csv`) and code (`<figfoldername>/run.py`) needed to reproduce the plot independently.
```python
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from plotis import PlotIs

# Generates sample data
x = np.linspace(0, 4 * np.pi)
sample_data = pd.DataFrame({"x": x, "y": np.sin(x)})

# Creates the plot inside a PlotIs context. The folder fig1 will contain
# the code and data needed to reproduce the plot independently.
with PlotIs("fig1", sample_data):
    sample_data.plot(x="x", y="y")
    plt.title("Sine function")
    plt.xlabel("x")
    plt.ylabel("sin(x)")

    # Shows the plot here; replaced by `pass` in run.py
    plt.show()
```

Running `python fig1/run.py`, from any directory, writes `fig1/figure.png`.

## Options
```python
with PlotIs(
    "figures/sine",           # folder for data.csv, run.py (and the figure)
    sample_data,              # must be a plain variable name
    format="pdf",             # any format plt.savefig understands (default "png")
    savefig_kwargs={"bbox_inches": "tight"},  # literals only
    style="house.mplstyle",   # applied in the context, copied next to run.py
    render=True,              # also write figures/sine/figure.pdf on exit
):
    fig, ax = plt.subplots()
    for name, group in sample_data.groupby("series"):  # nested blocks are fine
        ax.plot(group["x"], group["y"], label=name)
    ax.legend()
```

- `run.py` resolves `data.csv`, the style file and the output figure relative to its own location, so the folder can be moved and the script run from any working directory.
- The `with` statement is parsed with `ast`: it may span several lines, use keyword arguments in any order, or put the body on the same line.
- The data is captured when the context is entered, so changes the body makes to the data frame are not saved (and are not applied twice by `run.py`).
- `data.csv` is written without the index column.
- Nothing is written if the context raises an exception.
- `savefig()`/`show()` statements in the context are replaced by `pass` in `run.py`.

`examples/ex2` uses every option above. Run `make` there to build the figures and a LaTeX document, and `make reproduce` to regenerate the figures from the moved `run.py` files alone.

## Limitations
`run.py` contains only the body of the `with` block, preceded by `import pandas as pd`, `import matplotlib.pyplot as plt` and the data variable loaded from `data.csv`. So the body:

- may only use `pd`, `plt`, the data variable and names it defines or imports itself. Other names from the surrounding script, such as `np`, helper functions or other variables, do not exist in `run.py`.
- must produce a single figure, with at most one `savefig()` and one `show()` call.
- cannot contain another `PlotIs` context.

With `render=True`, a `plt.show()` in the body can close the figure on interactive backends, which leaves the rendered file empty. Use `render=True` without `show()`, or use a non-interactive backend such as `Agg`.

`PlotIs` must be used in a source file (not an interactive prompt or notebook cell), since it reads the `with` block from the calling file.

## Errors
| Exception | Raised when |
|---|---|
| `PlotIsError` | `PlotIs` is not used as a `with` statement, `data` is not a plain variable name, the body nests `PlotIs` or has more than one `savefig()`/`show()` call, `savefig_kwargs` holds non-literal values, or the calling source file cannot be read. |
| `TypeError` | `data` is not a `pandas.DataFrame`. |
| `FileNotFoundError` | The `style` file does not exist. |

## Migrating from 0.1
- Catch `PlotIsError` instead of `Exception`.
- Pass `data` as a plain variable name (`PlotIs(path, df)`, not `PlotIs(path, df.copy())`).
- `data.csv` has no index column. Read it with `pd.read_csv(path)`, without `index_col=0`.
- `run.py` now saves `figure.<format>` next to itself instead of relative to the working directory.

See [CHANGELOG.md](CHANGELOG.md) for the full list of changes.

## LaTeX project example
Since this package was motivated by large documentation projects, this example shows how to hook into the compilation of a LaTeX document to insert the figure produced by the example above.

Consider a LaTeX document with the following content:
```latex
\documentclass[12pt]{article}
\usepackage{graphicx}
\usepackage{hyperref}

\title{PlotIs example one}
\author{Victor Brun\\ \href{https://victorbrun.com}{victorbrun.com}}
\date{\today}

\begin{document}

\maketitle

\section{The sine function}
The sine function is a trigonometric function which we denote by $\sin{x}$. In figure \ref{fig:sin} we can see that it looks like a wave.

\begin{figure}[h]
	\centering
	\includegraphics[width=8cm]{figures/sinus_curve.png}
	\caption{The sine function plotted on the interval $[0, 4\pi]$.}
	\label{fig:sin}
\end{figure}

\end{document}
```

To keep the repository small, `figures/sinus_curve.png` is not committed, since it is not a plain-text format. The plotting script (`plot_script.py`, using `PlotIs` as above) writes `sinus_curve/data.csv` and `sinus_curve/run.py`, which are enough to recreate the figure. A Makefile then runs `run.py`, copies the image to where the LaTeX document expects it and compiles the document:
```make
PYTHON ?= python3
FIG := sinus_curve

all: main.pdf

# Runs the plotting script, which writes the isolated data and code
$(FIG)/run.py $(FIG)/data.csv: plot_script.py
	$(PYTHON) plot_script.py

# Runs the automatically generated python script to create the plot
$(FIG)/figure.png: $(FIG)/run.py $(FIG)/data.csv
	$(PYTHON) $(FIG)/run.py

# Copies the produced figure to where main.tex expects it
figures/$(FIG).png: $(FIG)/figure.png
	mkdir -p figures
	cp $< $@

# Runs pdflatex twice so that references are resolved
main.pdf: main.tex figures/$(FIG).png
	pdflatex main.tex
	pdflatex main.tex
```

In a real project you would commit `sinus_curve/` and run only the last three rules. The working example is in `examples/ex1`.

# Development
```bash
pip install -e ".[dev]"
pytest
```
