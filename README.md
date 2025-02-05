# latex-recipes
Generate PDFs of recipes using LaTeX


## Set up
The Python code that generates LaTeX from the YAML files relies on the following non-standard Python modules:
 - [PyYAML](https://pypi.org/project/PyYAML/)
 - [Jinja2](https://pypi.org/project/Jinja2/)
 - [PyEnchant](https://pyenchant.github.io/pyenchant/)
 - [language_tool_python](https://pypi.org/project/language-tool-python/)

The PDF generation is handled by [latexmk](https://www.cantab.net/users/johncollins/latexmk/index.html) - if you have a standard [LaTeX](https://www.latex-project.org/get/) distribution you probably already have it.


## Generating the recipe PDFs
The project uses [GNU Make](https://www.gnu.org/software/make/) to generate the PDFs from YAML files. An example of such a file can be found in the `yaml` directory.

To generate PDFs for all of the YAML files in the `yaml` directory, simply run
```bash
make -j
```

By default this uses `rcp-phone.sty`, producing PDFs designed to be displayed on smaller devices. To select a different style, override `STY_FILE`, eg
```bash
make -j STY_FILE=rcp-parallel.sty
```
Available style files can be found in `src/styles`.


## Spelling/grammar checking
By default the YAML files are checked using [LanguageTool](https://dev.languagetool.org/http-server), which highlights potential spelling and grammar errors. Whilst it is very detailed, LanguageTool is very slow. Other options can be enabled by overriding `CHECKER` with one of `language_tool`, `enchant`, or `none`, eg
```bash
make -j CHECKER=enchant
```
