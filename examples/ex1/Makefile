all: | plotgen move pdflatex
	# Executes below targets in the following order
	# 1. plotget
	# 2. move
	# 3. pdflatex

plotgen: sinus_curve/run.py sinus_curve/data.csv
	# Runs the automatically generated pyhton
	# script to create the plot
	python3 sinus_curve/run.py 

move: sinus_curve/figure.png 
	@echo "\nCreating folder figures if it does not exist"
	mkdir -p figures 

	@echo "\nCopying produced fiure to figures/"
	cp sinus_curve/figure.png figures/sinus_curve.png

pdflatex: main.tex
	# Runs pdflatex twice to make sure
	# references are created correctly
	pdflatex main.tex
	pdflatex main.tex
