"""Tests for model_utils module."""

from utils.model_utils import estimate_tokens


class TestEstimateTokens:
    """Tests for token estimation function."""

    def test_empty_string(self):
        """Test token estimation with empty string."""
        assert estimate_tokens("") == 0

    def test_short_text(self):
        """Test token estimation with short text."""
        text = "Hello"
        estimated = estimate_tokens(text)
        assert estimated == len(text) // 4

    def test_long_text(self):
        """Test token estimation with longer text."""
        text = "This is a longer text to test token estimation"
        estimated = estimate_tokens(text)
        assert estimated == len(text) // 4

    def test_french_text(self):
        """Test token estimation with French text."""
        text = "Bonjour, comment allez-vous aujourd'hui ?"
        estimated = estimate_tokens(text)
        assert estimated == len(text) // 4
        assert estimated > 0

