from pathlib import Path

import yaml


def load_config(path: str = 'src/config/config.yaml') -> dict:
    """
    Charge le fichier de configuration YAML central du projet.
    """
    with open(Path(path), 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)
