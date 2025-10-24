#!/usr/bin/env python3
"""
SerdaBot V1 - Point d'entrée principal
Architecture KISS modulaire
"""

import asyncio
import logging
import yaml
from pathlib import Path

from bot import KissBot


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


def setup_logging(config: dict):
    """Configure le logging global"""
    log_level = config.get('logging', {}).get('level', 'INFO')
    log_file = config.get('logging', {}).get('file', 'serdabot.log')
    
    logging.basicConfig(
        level=getattr(logging, log_level),
        format='%(asctime)s [%(levelname)s] %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )


def main():
    """Point d'entrée principal pour TwitchIO 2.x"""
    try:
        # Charger config et setup logging
        config = load_config()
        setup_logging(config)
        
        logging.info("🚀 Démarrage KissBot V1 TwitchIO 2.x avec toutes les fonctionnalités")
        
        # Créer et lancer le bot
        bot = KissBot(config)
        bot.run()  # TwitchIO 2.x gère l'event loop automatiquement
        
    except Exception as e:
        logging.error(f"❌ Erreur critique: {e}")
        raise


if __name__ == "__main__":
    print("🚀 LANCEMENT DU VRAI BOT avec TwitchIO 2.x et TOUTES les fonctionnalités !")
    main()