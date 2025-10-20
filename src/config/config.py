import os
from pathlib import Path

import yaml


def load_config(path: str | None = None) -> dict:
    """
    Charge le fichier de configuration YAML central du projet.
    
    Ordre de priorité :
    1. Variable d'environnement SERDABOT_CONFIG (si définie)
    2. Paramètre `path` (si fourni)
    3. Config locale : ../SerdaBot-local/config/config.yaml
    4. Config repo : src/config/config.yaml
    5. Fallback : src/config/config.sample.yaml
    
    Cette logique permet de :
    - Utiliser une config locale hors Git (SerdaBot-local/)
    - Avoir un fallback fonctionnel pour les forks/CI
    - Override via variable d'environnement si besoin
    """
    # 1. Priorité à la variable d'environnement
    env_config = os.getenv('SERDABOT_CONFIG')
    if env_config:
        config_path = Path(env_config)
        if config_path.exists():
            with open(config_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
    
    # 2. Sinon, utiliser le paramètre fourni
    if path:
        config_path = Path(path)
        if config_path.exists():
            with open(config_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
    
    # 3. Tenter la config locale (SerdaBot-local/)
    local_config = Path('../SerdaBot-local/config/config.yaml')
    if local_config.exists():
        with open(local_config, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    
    # 4. Tenter la config dans le repo
    repo_config = Path('src/config/config.yaml')
    if repo_config.exists():
        with open(repo_config, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    
    # 5. Fallback vers config.sample.yaml
    sample_config = Path('src/config/config.sample.yaml')
    if sample_config.exists():
        with open(sample_config, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    
    raise FileNotFoundError(
        "❌ Aucune config trouvée ! Vérifie que tu as bien :\n"
        "  1. Créé ../SerdaBot-local/config/config.yaml OU\n"
        "  2. Copié src/config/config.example.yaml → src/config/config.yaml\n"
        "  Voir README.md pour les instructions de setup."
    )
