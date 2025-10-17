"""Tests for prompt_loader module."""

import pytest
from pathlib import Path
from prompts.prompt_loader import load_prompt_template


class TestLoadPromptTemplate:
    """Tests for prompt template loading."""
    
    def test_load_ask_prompt_fr(self):
        """Test loading French ask prompt."""
        prompt = load_prompt_template('ask', 'fr')
        assert prompt is not None
        assert len(prompt) > 0
        assert isinstance(prompt, str)
    
    def test_load_ask_prompt_en(self):
        """Test loading English ask prompt."""
        prompt = load_prompt_template('ask', 'en')
        assert prompt is not None
        assert len(prompt) > 0
        assert isinstance(prompt, str)
    
    def test_load_chill_prompt_fr(self):
        """Test loading French chill prompt."""
        prompt = load_prompt_template('chill', 'fr')
        assert prompt is not None
        assert len(prompt) > 0
    
    def test_load_game_prompt_fr(self):
        """Test loading French game prompt."""
        prompt = load_prompt_template('game', 'fr')
        assert prompt is not None
        assert len(prompt) > 0
    
    def test_fallback_to_fr_when_lang_not_exists(self):
        """Test fallback to French when language doesn't exist."""
        # 'es' (Spanish) doesn't exist, should fallback to 'fr'
        prompt = load_prompt_template('ask', 'es')
        assert prompt is not None
        assert len(prompt) > 0
    
    def test_invalid_prompt_type_raises_error(self):
        """Test that invalid prompt type raises an error."""
        with pytest.raises((FileNotFoundError, RuntimeError)):
            load_prompt_template('nonexistent_type', 'fr')
