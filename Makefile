# which style file to use (located in STY_DIR)
STY_FILE=rcp-phone.sty

# where the YAML recipes are defined
YAML_DIR=./yaml


# TeX and PDF generation tools
YAML_TO_TEX=python3 ./src/yaml_to_tex.py
LATEXMK=latexmk -pdf -ps- -dvi- -xdv- -interaction=nonstopmode -halt-on-error

# where style files are kept
STY_DIR=./src/styles

# where any TeX-related files (including logs) go
TEX_DIR=./tex

# where the generated PDF files go
PDF_DIR=./pdf

# the hand-written YAML files
YAML=$(wildcard $(YAML_DIR)/*.yaml)

# the generated TeX files
TEX=$(addprefix $(TEX_DIR)/, $(notdir $(YAML:.yaml=.tex)))

# the generated .pdf files
PDF=$(addprefix $(PDF_DIR)/, $(notdir $(YAML:.yaml=.pdf)))



# generate new and changed PDFs from scratch
.PHONY: all
all: $(PDF)

# generate new and changed TeX files from scratch
.PHONY: latex
latex: $(TEX)

# force generate all PDFs from scratch
.PHONY: force
force: clean $(PDF)

# remove TeX, PDF, and log files
.PHONY: clean
clean:
	@printf "`tput bold``tput setaf 1`Cleaning`tput sgr0`\n"
	rm -rf $(TEX_DIR) $(PDF_DIR)

# prevent removal of intermediate TeX files
.PRECIOUS: $(TEX_DIR)/%.tex

# generate a PDF from a TeX file
$(PDF_DIR)/%.pdf: $(TEX_DIR)/%.tex | $(PDF_DIR)
	@printf "`tput bold``tput setaf 2`Compiling %s`tput sgr0`\n" $@
	$(LATEXMK) -e "ensure_path('TEXINPUTS','$(STY_DIR)')" -outdir=$(PDF_DIR) -auxdir=$(TEX_DIR) $< > $(TEX_DIR)/$*.out

# convert YAML recipe definition into a TeX file
$(TEX_DIR)/%.tex: $(YAML_DIR)/%.yaml $(STY_DIR)/$(STY_FILE) | $(TEX_DIR)
	@printf "`tput bold``tput setaf 6`Generating %s`tput sgr0`\n" $@
	$(YAML_TO_TEX) $< $@ --style $(STY_FILE)

# create output directory for PDFs
$(PDF_DIR):
	mkdir -p $(PDF_DIR)

# create intermediate directory for TeX-related files
$(TEX_DIR):
	mkdir -p $(TEX_DIR)
# 	cp $(STY_DIR)/$(STY_FILE) $(TEX_DIR)/$(STY_FILE)
