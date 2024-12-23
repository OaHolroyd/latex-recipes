"""
Takes a YAML definition and generates a LaTeX file
"""
from sys import stderr
import argparse
from pathlib import Path

import yaml
from jinja2 import Environment, FileSystemLoader


TEMPLATE_FILE="src/recipe.j2"


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
    "–": "---",
}


def yaml_to_tex(
    yaml_file: str,
    tex_file: str,
    sty_file: str,
):
    """
    Generate a YAML file `yaml_file` from a TeX file `tex_file`

    Args:
        yaml_file: relative path to the source YAML file
        tex_file: relative path to the output TeX file
        sty_file: relative path to the recipe style file
    """
    # load the recipe from the YAML file
    text = Path(yaml_file).read_text()

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

    # optionally override the style file
    parser.add_argument('--style', type=str, default="rcpphone.sty", help='additional word list')

    # get the arguments
    args = parser.parse_args()
    yaml_file = args.yaml_file
    tex_file = args.tex_file
    sty_file = args.style

    # generate the TeX file
    yaml_to_tex(yaml_file, tex_file, sty_file)
