"""
Config Loader - Utilitaire pour charger config.yaml
"""

import yaml
from pathlib import Path


def load_config() -> dict:
    """Charge la configuration depuis config.yaml"""
    config_path = Path(__file__).parent / "config.yaml"
    
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        raise FileNotFoundError(f"Configuration non trouvée: {config_path}")
    except yaml.YAMLError as e:
        raise ValueError(f"Erreur dans config.yaml: {e}")
