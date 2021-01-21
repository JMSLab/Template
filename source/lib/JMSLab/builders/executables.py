from pathlib import Path
from shutil import which

import yaml
import os

EXE_FILE = Path(__file__).resolve().parents[0] / 'executables.yml'


def get_executables(efile = EXE_FILE, languages = []):
    with open(efile, 'r') as e:
        executables = yaml.safe_load(e)
        for lang in list(executables.keys()) + languages:
            ENV = f'JMSLAB_EXE_{lang.replace(" ", "_")}'.upper()
            if ENV in os.environ:
                program = os.environ[ENV]
                if which(program):
                    executables[lang] = which(program)
                else:
                    executables[lang] = str(Path(program).expanduser().resolve())

    return {lang: quote_str(exe) for lang, exe in executables.items()}


def quote_str(x, quotechar = '"', contains = None):
    not_quoted = not (x.startswith(quotechar) or x.endswith(quotechar))
    x_contains = True if contains is None else x.find(contains) >= 0
    return quotechar + x + quotechar if not_quoted and x_contains else x
