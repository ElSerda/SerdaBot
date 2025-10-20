"""Tests for config module."""

from pathlib import Path

import yaml


class TestConfigLoading:
    """Tests for configuration loading."""

    def test_config_sample_exists(self):
        """Test that config.example.yaml exists and is valid."""
        sample_path = Path('src/config/config.example.yaml')
        assert sample_path.exists(), "config.example.yaml should exist"

        with open(sample_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)

        assert config is not None
        assert isinstance(config, dict)

    def test_config_sample_has_required_sections(self):
        """Test that config.example.yaml has all required sections."""
        sample_path = Path('src/config/config.example.yaml')

        with open(sample_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)

        # Check required sections
        assert 'twitch' in config
        assert 'bot' in config
        assert 'igdb' in config

    def test_config_sample_twitch_section(self):
        """Test Twitch section structure."""
        sample_path = Path('src/config/config.example.yaml')

        with open(sample_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)

        twitch = config['twitch']
        assert 'client_id' in twitch
        assert 'client_secret' in twitch
        assert 'bot_id' in twitch

    def test_config_sample_bot_section(self):
        """Test bot section structure."""
        sample_path = Path('src/config/config.example.yaml')

        with open(sample_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)

        bot = config['bot']
        assert 'name' in bot
        assert 'channel' in bot
        assert 'enabled_commands' in bot
        assert isinstance(bot['enabled_commands'], list)
