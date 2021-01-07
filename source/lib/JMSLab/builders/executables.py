from pathlib import Path
import yaml
import os


EXE_FILE = Path(__file__).resolve().parents[0] / 'executables.yml'


def get_executables(efile = EXE_FILE, languages = []):
    with open(efile, 'r') as e:
        executables = yaml.safe_load(e)
        for lang in list(executables.keys()) + languages:
            ENV = f'JMSLAB_EXE_{lang}'.upper()
            if ENV in os.environ:
                executables[lang] = os.environ[ENV]

    return executables
