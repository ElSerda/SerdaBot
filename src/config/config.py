from pathlib import Path

import yaml


def load_config(path: str = 'src/config/config.yaml') -> dict:
    """
    Charge le fichier de configuration YAML central du projet.
    Utilise config.sample.yaml en fallback si config.yaml n'existe pas (CI/tests).
    """
    config_path = Path(path)
    
    # Fallback vers config.sample.yaml si config.yaml n'existe pas
    if not config_path.exists():
        sample_path = config_path.parent / 'config.sample.yaml'
        if sample_path.exists():
            config_path = sample_path
    
    with open(config_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)
