# latex-recipes
Generate PDFs of recipes using LaTeX

## Set up
The Python code that generates LaTeX from the YAML files relies on the following non-standard Python modules:
 - [PyYAML](https://pypi.org/project/PyYAML/)
 - [Jinja2](https://pypi.org/project/Jinja2/)
 - [PyEnchant](https://pyenchant.github.io/pyenchant/)

The PDF generation is handled by [latexmk](https://www.cantab.net/users/johncollins/latexmk/index.html) - if you have a standard [LaTeX](https://www.latex-project.org/get/) distribution you probably already have it.

## Generating the recipe PDFs
The project uses [GNU Make](https://www.gnu.org/software/make/) to generate the PDFs from YAML files. An example of such a file can be found in the `yaml` directory.

To generate PDFs for all of the YAML files in the `yaml` directory, simply run
```bash
make -j
```
