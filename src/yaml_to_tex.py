"""
Takes a YAML definition and generates a LaTeX file
"""
from sys import stderr
import argparse
from pathlib import Path

import yaml
from jinja2 import Environment, FileSystemLoader
from enchant.checker import SpellChecker
from enchant import DictWithPWL


TEMPLATE_FILE="src/recipe.j2"


class ansicolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def stderr_print(*args, **kwargs):
    print(*args, **kwargs, file=stderr)


def warn(text: str, *args, **kwargs):
    stderr_print(ansicolors.WARNING + text + ansicolors.ENDC, *args, **kwargs)


def make_checker(words: list[str]) -> SpellChecker:
    """
    Constructs a SpellChecker, adding extra words to its permitted list
    """
    d = DictWithPWL("en_GB")
    for w in words:
        d.add(w)
    return SpellChecker(d)


# define non-LaTeX friendly characters and their replacements
BAD_CHARS = {
    "é": "\\'{e}",
    "%": "\\%",
    "˚": "\\degree{}",
    "½": "\\sfrac{1}{2}",
    "⅓": "\\sfrac{1}{3}",
    "⅔": "\\sfrac{2}{3}",
    "¼": "\\sfrac{1}{4}",
    "¾": "\\sfrac{3}{4}",
}


def yaml_to_tex(
    yaml_file: str,
    tex_file: str,
    sty_file: str,
    nocheck: bool = False,
    word_file: str | None = None,
):
    """
    Generate a YAML file `yaml_file` from a TeX file `tex_file`

    Args:
        yaml_file: relative path to the source YAML file
        tex_file: relative path to the output TeX file
        tex_file: relative path to the recipe style file
        nocheck: whether to disable spell-checking
        word_file: relative path to file containing additional permitted words
            for the spell-checker
    """
    # load the recipe from the yaml file
    text = Path(yaml_file).read_text()

    if not nocheck:
        # read extra words from the file if supplied
        words = []
        if word_file is not None:
            with open(word_file, "r") as f:
                words = [line.rstrip('\n') for line in f]

        # set up dictionary
        checker = make_checker(words)

        # check spelling
        checker.set_text(text.lower())
        errflag = False
        for err in checker:
            if not errflag:
                errflag = True
                warn(f"[{yaml_file}] WARNING potential spelling errors")
            warn(f"  {err.word}")

    # get content from the YAML
    content = yaml.safe_load(text)
    content["style"] = sty_file[:-4]

    # extract the primary ingredient list
    main_key = list(content["ingredients"].keys())[0]
    content["main_ingredients"] = {main_key: content["ingredients"][main_key]}
    content["ingredients"].pop(main_key, None)

    # fill in the recipe template
    env = Environment(loader=FileSystemLoader(searchpath="./"))
    template = env.get_template(TEMPLATE_FILE)
    latex = template.render(**content) + '\n'


    # clean up the recipe, removing bad chars etc.
    for ch, rep in BAD_CHARS.items():
        latex = latex.replace(ch, rep)

    # save to file
    with open(tex_file, "w") as f:
        f.write(latex)


if __name__ == '__main__':
    # set up the arg parser
    parser = argparse.ArgumentParser(description="Generates TeX files from YAML definitions")

    # required args: the input and output files
    parser.add_argument('yaml_file', type=str, help='input YAML file')
    parser.add_argument('tex_file', type=str, help='output TeX file')

    # optionally check spelling etc.
    parser.add_argument('--nocheck', action='store_true', help='disable spell checker')

    # optionally override default additional-word list
    parser.add_argument('--words', type=str, default="src/words.txt", help='additional word list')

    # optionally override the style file
    parser.add_argument('--style', type=str, default="rcpphone.sty", help='additional word list')

    # get the arguments
    args = parser.parse_args()
    yaml_file = args.yaml_file
    tex_file = args.tex_file
    nocheck = args.nocheck
    word_file = args.words
    sty_file = args.style

    # generate the TeX file
    yaml_to_tex(yaml_file, tex_file, sty_file, nocheck=nocheck, word_file=word_file)
