PYTHON ?= python3

all: figures main.pdf

# Runs the plotting script: writes figures/*/{data.csv,run.py,house.mplstyle,figure.pdf}
figures: plot_script.py house.mplstyle
	$(PYTHON) plot_script.py

main.pdf: main.tex figures
	pdflatex main.tex
	pdflatex main.tex

# Shows that run.py is self-contained and relocatable: the figure folders are
# moved, and each figure is regenerated from run.py + data.csv, run from /
reproduce: figures
	rm -rf moved && mkdir moved && cp -R figures/waves figures/bars moved/
	rm moved/*/figure.pdf
	cd / && for d in "$(CURDIR)"/moved/*; do $(PYTHON) "$$d/run.py"; done
	ls moved/*/figure.pdf

clean:
	rm -rf figures moved main.aux main.log main.out main.pdf

.PHONY: all figures reproduce clean
