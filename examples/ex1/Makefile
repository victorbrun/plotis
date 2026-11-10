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

clean:
	rm -rf $(FIG) figures main.aux main.log main.out main.pdf

.PHONY: all clean
