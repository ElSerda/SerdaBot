"""
Configuration pytest pour KissBot
"""

import pytest
import sys
import os

# Ajouter le répertoire parent au path pour les imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


@pytest.fixture
def mock_config():
    """Configuration mock pour les tests."""
    # Charger la vraie config pour avoir la clé RAWG
    import yaml
    import os
    
    config_path = os.path.join(os.path.dirname(__file__), '..', 'config.yaml')
    
    try:
        with open(config_path, 'r') as f:
            real_config = yaml.safe_load(f)
    except:
        real_config = {}
    
    # Utiliser la vraie clé RAWG si disponible, sinon mock
    return {
        'twitch': {
            'token': 'test_token',
            'prefix': '!',
            'channels': ['test_channel']
        },
        'cache': {
            'ttl_seconds': 3600,
            'max_size': 1000
        },
        'llm': {
            'local': {
                'enabled': True,
                'url': 'http://localhost:1234/v1/chat/completions'
            },
            'openai': {
                'enabled': False
            }
        },
        'apis': real_config.get('apis', {
            'rawg': {
                'api_key': 'test_rawg_key'
            },
            'steam': {
                'enabled': True
            }
        })
    }


@pytest.fixture
def mock_bot(mock_config):
    """Bot mock pour les tests."""
    # TODO: Créer un mock du bot complet
    pass
