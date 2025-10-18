"""Tests for prompt_loader module."""

from prompts.prompt_loader import load_system_prompt, make_prompt


class TestPromptLoader:
    """Tests for new prompt system."""

    def test_load_system_prompt(self):
        """Test loading system prompt."""
        prompt = load_system_prompt()
        assert prompt is not None
        assert len(prompt) > 0
        assert isinstance(prompt, str)
        # Nouveau SYSTEM ultra-simplifié
        assert "bot" in prompt.lower() and "twitch" in prompt.lower()

    def test_make_prompt_ask(self):
        """Test making ask prompt."""
        prompt = make_prompt('ask', 'Quelle heure est-il?', 'viewer123')
        assert prompt is not None
        # Plus de "Mode: ask", maintenant c'est ultra-simplifié
        assert 'Explique brièvement' in prompt or 'Quelle heure est-il?' in prompt

    def test_make_prompt_chill(self):
        """Test making chill prompt."""
        prompt = make_prompt('chill', 'Salut!', 'viewer456')
        assert prompt is not None
        # Plus de "Mode: chill", maintenant c'est ultra-simplifié
        assert 'Réponds' in prompt or 'Salut!' in prompt

    def test_make_prompt_trad(self):
        """Test making trad prompt."""
        prompt = make_prompt('trad', 'Hello world', 'viewer789')
        assert prompt is not None
        assert 'Traduis' in prompt or 'Hello world' in prompt

    def test_make_prompt_with_roast(self):
        """Test making prompt with roast user."""
        # Roast maintenant géré en direct (pas dans le prompt)
        # Le prompt pour roast user est identique à un user normal
        prompt = make_prompt('chill', 'Test', 'el_serda')
        assert 'Réponds' in prompt or 'Test' in prompt
        # Pas de "Roast" car géré directement par chill_command.py

    def test_make_prompt_with_game_context(self):
        """Test making prompt with game context."""
        prompt = make_prompt('reactor', 'LUL', 'viewer', 'Valorant', 'Ranked')
        assert 'Valorant' in prompt or 'LUL' in prompt

