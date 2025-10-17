"""Tests for clean module."""

from utils.clean import clean_response


class TestCleanResponse:
    """Tests for response cleaning function."""

    def test_clean_basic_response(self):
        """Test cleaning a basic response."""
        response = "This is a clean response."
        cleaned = clean_response(response)
        assert cleaned == response

    def test_remove_chatml_tags(self):
        """Test removal of ChatML tags."""
        response = "Hello world<|im_end|>"
        cleaned = clean_response(response)
        assert "<|im_start|>" not in cleaned
        assert "<|im_end|>" not in cleaned
        assert "Hello world" in cleaned

    def test_remove_assistant_prefix(self):
        """Test removal of assistant: prefix."""
        response = "assistant: This is the response"
        cleaned = clean_response(response)
        assert "assistant:" not in cleaned.lower()
        assert "This is the response" in cleaned

    def test_strip_whitespace(self):
        """Test stripping of leading/trailing whitespace."""
        response = "  \n  Response with spaces  \n  "
        cleaned = clean_response(response)
        assert cleaned == "Response with spaces"

    def test_truncate_long_response(self):
        """Test truncation of very long responses."""
        long_response = "A" * 1000
        cleaned = clean_response(long_response, max_length=100)
        assert len(cleaned) <= 100
        assert len(cleaned) < len(long_response)

    def test_preserve_short_response(self):
        """Test that short responses are not truncated."""
        short_response = "Short"
        cleaned = clean_response(short_response, max_length=100)
        assert cleaned == short_response
        assert not cleaned.endswith("...")

    def test_remove_multiple_tags(self):
        """Test removal of multiple types of tags."""
        response = "<|im_start|>user\nTest<|im_end|>Final"
        cleaned = clean_response(response)
        assert "Final" in cleaned
        assert "<|" not in cleaned

    def test_remove_markdown_bold(self):
        """Test removal of Markdown bold syntax."""
        response = "This is **bold** text"
        cleaned = clean_response(response)
        assert "**" not in cleaned
        assert "bold" in cleaned

    def test_remove_markdown_code(self):
        """Test removal of Markdown inline code."""
        response = "This is `code` text"
        cleaned = clean_response(response)
        assert "`" not in cleaned
        assert "code" in cleaned

    def test_empty_response(self):
        """Test cleaning an empty response."""
        cleaned = clean_response("")
        assert cleaned == ""

    def test_response_with_newlines(self):
        """Test response with multiple newlines."""
        response = "Line1\n\n\nLine2"
        cleaned = clean_response(response)
        # Should preserve newlines but strip outer whitespace
        assert "Line1" in cleaned
        assert "Line2" in cleaned
