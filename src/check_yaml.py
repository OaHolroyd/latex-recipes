"""
Runs a spelling and grammar checker over a YAML file
"""
from sys import stderr
import argparse
from pathlib import Path

import yaml
import language_tool_python
from enchant.checker import SpellChecker
from enchant import DictWithPWL


class DummyMatch(object):
    def __init__(self, msg):
        self.message = msg


def match_str(match):
    s = 'Error: {}\n'.format(match.message)
    try:
        s += '{}\n{}\n'.format(
            match.context, ' ' * match.offsetInContext + '^' * match.errorLength
        )
    except:
        pass
    return s


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


def flatten_content(content: dict) -> list[str]:
    """
    Takes the content of a YAML file and turns it into a list of text suitable
    for spell/grammar checking
    """
    content_list = []
    if isinstance(content.get("title", None), str):
        content_list.append(content["title"])
    if isinstance(content.get("servings", None), str):
        content_list.append(content["servings"])
    if isinstance(content.get("number", None), str):
        content_list.append(content["number"])
    if isinstance(content.get("prepTime", None), str):
        content_list.append(content["prepTime"])
    if isinstance(content.get("cookTime", None), str):
        content_list.append(content["cookTime"])
    if isinstance(content.get("freezable", None), str):
        content_list.append(content["freezable"])
    if isinstance(content.get("notes", None), str):
        content_list.append(content["notes"])
    for key, val in content.get("ingredients", {}).items():
        for item in val:
            content_list.append("Item:" + str(item))
    for step in content.get("method", []):
        content_list.append(step)
    return content_list


def get_errors_language_tool(content: list[str], words: list[str]) -> list:
    """
    Use a local LanguageTool server to find spelling and grammar errors in the
    content.
    """
    errors = []
    with language_tool_python.LanguageTool('en-GB') as tool:
        for item in content:
            # run LanguageTool on text
            text = str(item)
            matches = tool.check(text)

            # custom permitted spellings
            for i in range(len(matches)):
                match = matches[i]

                # ignore matches that are spelling 'mistakes' that are in the words list
                if match.ruleId == "MORFOLOGIK_RULE_EN_GB":
                    bad_word = text[match.offsetInContext:match.offsetInContext+match.errorLength]
                    if bad_word in words:
                        continue

                errors.append(match)
    return errors


def get_errors_enchant(content: list[str], words: list[str]) -> list:
    """
    Use a Enchant to find spelling errors in the content.
    """
    # set up the spell checker
    d = DictWithPWL("en_GB")
    for w in words:
        d.add(w)
    tool = SpellChecker(d)

    # Merge content into a single string
    text = " ".join(content)

    # check spelling
    tool.set_text(text)
    errors = []
    for err in tool:
        errors.append(DummyMatch(f'{err.word} spelled incorrectly'))

    return errors


def check_yaml(
        input_file: str,
        output_file: str,
        word_file: str | None = None,
        mode: str = "language_tool"
    ):
    """
    Loads a recipe from a YAML file and runs a spell/grammar checker over it.
    """
    # read extra words from the file if supplied
    words = []
    if word_file is not None:
        with open(word_file, "r") as f:
            words = [line.rstrip('\n') for line in f]

    # load the recipe from the YAML file
    text = Path(input_file).read_text()

    # get content from the YAML
    content = flatten_content(yaml.safe_load(text))

    # check spelling and grammar
    if mode == "language_tool":
        errors = get_errors_language_tool(content, words)
    elif mode == "enchant":
        errors = get_errors_enchant(content, words)
    elif mode == "none":
        errors = []
    else:
        raise ValueError(f"mode '{mode}' not recognised")

    # report errors
    if len(errors) > 0:
        warn(f"[{input_file}] Possible errors detected:");

        for error in errors:
            warn(f"{match_str(error)}");

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

    # optionally override default checker
    parser.add_argument('--mode', type=str, default="language_tool", help='Checking engine')

    # get the arguments
    args = parser.parse_args()
    input_file = args.input_file
    output_file = args.output_file
    word_file = args.words
    mode = args.mode

    # generate the TeX file
    check_yaml(input_file, output_file, word_file=word_file, mode=mode)
