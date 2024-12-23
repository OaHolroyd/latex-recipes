# default style file to use (located in STY_DIR)
STY_FILE?=rcp-phone.sty

# where the YAML recipes are defined
YAML_DIR=./yaml



# executables
CHECK_YAML=python3 ./src/check_yaml.py
YAML_TO_TEX=python3 ./src/yaml_to_tex.py
LATEXMK=latexmk -pdf -ps- -dvi- -xdv- -interaction=nonstopmode -halt-on-error

# where style files are kept
STY_DIR=./src/styles

# where any intermediate files
TMP_DIR=./tmp

# where the generated PDF files go
PDF_DIR=./pdf

# the hand-written YAML files
YAML=$(wildcard $(YAML_DIR)/*.yaml)

# the checked YAML files
CHECKED=$(addprefix $(TMP_DIR)/, $(notdir $(YAML:.yaml=.checked.yaml)))

# the generated TeX files
TEX=$(addprefix $(TMP_DIR)/, $(notdir $(YAML:.yaml=.tex)))

# the generated .pdf files
PDF=$(addprefix $(PDF_DIR)/, $(notdir $(YAML:.yaml=.pdf)))



# generate new and changed PDFs from scratch
.PHONY: all
all: $(PDF)

# generate new and changed TeX files from scratch
.PHONY: latex
latex: $(TEX)

# spell/grammar check the YAML files
.PHONY: check
check: $(CHECKED)

# force generate all PDFs from scratch
.PHONY: force
force: clean $(PDF)

# remove TeX, PDF, and log files
.PHONY: clean
clean:
	@printf "`tput bold``tput setaf 15`Cleaning`tput sgr0`\n"
	rm -rf $(TMP_DIR) $(PDF_DIR)

# prevent removal of intermediate
.PRECIOUS: $(TMP_DIR)/%.tex
.PRECIOUS: $(TMP_DIR)/%.checked.yaml

# generate a PDF from a TeX file
$(PDF_DIR)/%.pdf: $(TMP_DIR)/%.tex | $(PDF_DIR)
	@printf "`tput bold``tput setaf 15`Compiling %s`tput sgr0`\n" $@
	$(LATEXMK) -e "ensure_path('TEXINPUTS','$(STY_DIR)')" -outdir=$(PDF_DIR) -auxdir=$(TMP_DIR) $< > $(TMP_DIR)/$*.out

# convert YAML recipe definition into a TeX file
$(TMP_DIR)/%.tex: $(TMP_DIR)/%.checked.yaml $(STY_DIR)/$(STY_FILE) | $(TMP_DIR)
	@printf "`tput bold``tput setaf 15`Generating %s`tput sgr0`\n" $@
	$(YAML_TO_TEX) $< $@ --style $(STY_FILE)

# spell and grammar check a YAML recipe definition
$(TMP_DIR)/%.checked.yaml: $(YAML_DIR)/%.yaml | $(TMP_DIR)
	@printf "`tput bold``tput setaf 15`Checking %s`tput sgr0`\n" $<
	$(CHECK_YAML) $< $@

# create output directory for PDFs
$(PDF_DIR):
	mkdir -p $(PDF_DIR)

# create intermediate directory for TeX-related files
$(TMP_DIR):
	mkdir -p $(TMP_DIR)
