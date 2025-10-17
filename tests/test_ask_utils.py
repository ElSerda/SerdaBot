"""Tests for ask_utils module."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from utils.ask_utils import build_ask_prompt, estimate_tokens, get_max_length


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


class TestBuildAskPrompt:
    """Tests for ask prompt building."""

    def test_basic_prompt(self):
        """Test basic prompt building."""
        user = "test_user"
        question = "What is Python?"
        prompt = build_ask_prompt(user, question)

        assert question.strip() in prompt
        assert len(prompt) > 0

    def test_prompt_with_long_question(self):
        """Test prompt with long question."""
        user = "test_user"
        question = "This is a very long question " * 20
        prompt = build_ask_prompt(user, question)

        assert len(prompt) > 0
        assert "?" in prompt or question.strip()[:50] in prompt

    def test_prompt_strips_whitespace(self):
        """Test that prompt strips whitespace from question."""
        user = "test_user"
        question = "   What is Python?   "
        prompt = build_ask_prompt(user, question)

        assert "What is Python?" in prompt
        assert "   " not in prompt or prompt.count("   ") < 2


class TestGetMaxLength:
    """Tests for max length calculation."""

    def test_basic_max_length(self):
        """Test basic max length calculation."""
        prefix = "Start: "
        suffix = " :End"
        limit = 100
        max_len = get_max_length(prefix, suffix, limit)

        # Should be limit - len(prefix) - len(suffix)
        expected = 100 - len(prefix) - len(suffix)
        assert max_len == expected

    def test_max_length_with_long_prefix_suffix(self):
        """Test max length when prefix+suffix exceed limit."""
        prefix = "A" * 60
        suffix = "B" * 60
        limit = 100
        max_len = get_max_length(prefix, suffix, limit)

        # Should return 0 when prefix+suffix > limit
        assert max_len == 0

    def test_max_length_zero_limit(self):
        """Test max length with zero limit."""
        max_len = get_max_length("prefix", "suffix", 0)
        assert max_len == 0
