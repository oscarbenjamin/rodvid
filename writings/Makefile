#
# Makefile to build reports and convert figures
#
all: rod_pivot.pdf

rod_pivot.pdf: rod_pivot.tex rod_geometry.pdf rod_free_body.pdf liftoff.pdf rod_slip.pdf
	xelatex $<
	xelatex $<
	make clean

# Convert SVG figures to PDF
%.pdf: %.svg
	inkscape $< --export-pdf=$@

# Generate figures from Python scripts
%.pdf: %.py
	./$< $@

# Clear up random LaTeX crap...
clean:
	rm *.aux *.log
