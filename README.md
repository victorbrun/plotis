# `plotis`
`plotis` is a plot isolation tool for python. It saves the data and python code needed to independently reproduce plots using a pythonic interface.

This project was initiated to address the issue of repository size ballooning in documentation projects where images are frequently updated. Since the most common image formats are not plain text, Git cannot version control them effectively, resulting in the storage of every version of every image. Instead of converting images to a plain text format or pruning the Git history, I chose to overengineer this solution. This solution uses Python context managers to extract the necessary code and data, enabling the independent reproduction of plots.

# Installation
```bash
pip install plotis
```

# Usage
## Simple example
`plotis` relies on the context manager `PlotIs`. By placing the plotting logic inside the `PlotIs` context and providing the data used for plotting, as shown below, a folder will be created in the working directory. This folder contains the data (`<figfoldername>/data.csv`) and code (`<figfoldername>/run.py`) needed to reproduce the plot independently.
```python
# Import base dependencies
import pandas as pd 
import matplotlib.pyplot as plt

# Imports PlotIs context manager from plotis package
from plotis import PlotIs 

# Generates sample data
x = np.linspace(0, 4*math.pi)
y = np.sin(x)
sample_data = pd.DataFrame(data={"x": x, "y": y})

# Specify the name of the folder which will contain 
# code and data needed to independently reproduce the plot.
figure_folder = "fig1"

# Creates plot inside PlotIs context
with PlotIs(figure_folder, sample_data):
	# Plots data 
	sample_data.plot(x="x", y="y")
	plt.title("Sin function")
	plt.xlabel("x")
	plt.ylabel("sin(x)")

	# Shows plot 
	plt.show()
```

## LaTeX project example
As this package was motivate by large documentation projects, this example will showcase how to "highjack" the compilation process of a LaTeX document to insert the figure produced by above example.

Consider a LaTeX document containing the following content:
```latex
\documentclass[12pt]{article}
\usepackage{graphicx}
\usepackage{hyperref}

\title{PlotIs example one}
\author{Victor Brun\\ \href{https://victorbrun.com}{victorbrun.com}}
\date{\today}

\begin{document}

\maketitle

\section{The sinus function}
The sinus function is a trigonometric function which we denote by $\sin{x}$. In figure \ref{fig:sin} we can see that it looks like a wave.

\begin{figure}[h]
	\centering
	\includegraphics[width=8cm]{figures/sinus_curve.png}
	\caption{The sinus function plotted on the interval $[0, 4\pi]$.}
	\label{fig:sin}
\end{figure}

\end{document}
```

Since you want to version control the figures in this huge LaTeX project, `figures/sinus_curve.png` does not exist in the repository (as it is a non-plain text image format). Fortunately, you have already written the logic using `plotis` (the code in the above example) needed to produce the figure `sinus_curve.png`. The result produced by running the `plotis` code, `fig1/data.csv`, and `fig1/run.py`, is sufficient to recreate the figure. You can create a Makefile to run the plotting script `fig1/run.py` and subsequently move the produced image to the appropriate folder in your LaTeX project. The Makefile is as follows:
```make
all: | plotgen move pdflatex
	# Executes below targets in the following order
	# 1. plotget
	# 2. move
	# 3. pdflatex

plotgen: sinus_curve/run.py sinus_curve/data.csv
	# Runs the automatically generated pyhton
	# script to create the plot
	python3 fig1/run.py 

move: sinus_curve/figure.png 
	@echo "\nCreating folder figures if it does not exist"
	mkdir -p figures 

	@echo "\nCopying produced fiure to figures/"
	cp fig1/figure.png figures/sinus_curve.png

pdflatex: main.tex
	# Runs pdflatex twice to make sure
	# references are created correctly
	pdflatex main.tex
	pdflatex main.tex
```

This can be found as a working example in `examples/ex1`.
