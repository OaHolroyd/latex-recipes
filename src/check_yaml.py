"""
Runs a spelling and grammar checker over a YAML file
"""
from sys import stderr
import argparse
from pathlib import Path

import yaml
from enchant.checker import SpellChecker
from enchant import DictWithPWL


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


def check_yaml(input_file: str, output_file: str, word_file: str | None = None):
    """
    Loads a recipe from a YAML file and runs a spell/grammar checker over it.
    """
    # load the recipe from the YAML file
    text = Path(input_file).read_text()

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
            warn(f"[{input_file}] WARNING potential spelling errors")
        warn(f"  {err.word}")

    with open(output_file, "w") as f:
        f.write(text)


if __name__ == '__main__':
    # set up the arg parser
    parser = argparse.ArgumentParser(description="Spell/grammar checks YAML definitions")

    # required args: the input and output files
    parser.add_argument('input_file', type=str, help='input YAML file')
    parser.add_argument('output_file', type=str, help='output YAML file')

    # optionally override default additional-word list
    parser.add_argument('--words', type=str, default="src/words.txt", help='additional word list')

    # get the arguments
    args = parser.parse_args()
    input_file = args.input_file
    output_file = args.output_file
    word_file = args.words

    # generate the TeX file
    check_yaml(input_file, output_file, word_file=word_file)
