"""Tests for game_utils module."""

import pytest
from utils.game_utils import (
    normalize_platforms,
    compress_platforms,
    clean_summary,
    sanitize_slug
)


class TestNormalizePlatforms:
    """Tests for platform normalization."""
    
    def test_list_of_dicts(self):
        """Test normalizing list of platform dictionaries."""
        platforms = [{"name": "PC"}, {"name": "PlayStation 5"}]
        result = normalize_platforms(platforms)
        assert result == ["PC", "PlayStation 5"]
    
    def test_comma_separated_string(self):
        """Test normalizing comma-separated string."""
        platforms = "PC, Xbox, PlayStation"
        result = normalize_platforms(platforms)
        assert "PC" in result
        assert "Xbox" in result
        assert "PlayStation" in result
    
    def test_list_of_strings(self):
        """Test normalizing list of strings."""
        platforms = ["PC", "Xbox"]
        result = normalize_platforms(platforms)
        assert result == platforms


class TestCompressPlatforms:
    """Tests for platform name compression."""
    
    def test_compress_playstation(self):
        """Test PlayStation compression."""
        platforms = ["PlayStation 5", "PlayStation 4"]
        result = compress_platforms(platforms)
        assert "PS5" in result
        assert "PS4" in result
    
    def test_compress_xbox(self):
        """Test Xbox compression."""
        platforms = ["Xbox Series X|S", "Xbox One"]
        result = compress_platforms(platforms)
        assert "Xbox" in result
        # Should deduplicate
        assert result.count("Xbox") == 1
    
    def test_compress_pc(self):
        """Test PC compression."""
        platforms = ["PC (Microsoft Windows)"]
        result = compress_platforms(platforms)
        assert "PC" in result
    
    def test_preserve_unknown_platforms(self):
        """Test that unknown platforms are preserved."""
        platforms = ["Custom Platform"]
        result = compress_platforms(platforms)
        assert "Custom Platform" in result


class TestCleanSummary:
    """Tests for summary cleaning."""
    
    def test_remove_game_name(self):
        """Test that game name is removed from summary."""
        summary = "Elden Ring is an amazing game. Elden Ring features..."
        cleaned = clean_summary(summary, "Elden Ring")
        # Game name should be removed at least once
        assert cleaned != summary
    
    def test_take_first_paragraph(self):
        """Test that only first paragraph is kept."""
        summary = "First paragraph here.\n\nSecond paragraph should be removed."
        cleaned = clean_summary(summary, "TestGame")
        assert "Second paragraph" not in cleaned
        assert "First paragraph" in cleaned
    
    def test_strip_leading_punctuation(self):
        """Test stripping of leading punctuation."""
        summary = ": This is a summary"
        cleaned = clean_summary(summary, "TestGame")
        assert not cleaned.startswith(":")


class TestSanitizeSlug:
    """Tests for slug sanitization."""
    
    def test_basic_slug(self):
        """Test basic slug creation."""
        slug = sanitize_slug("Elden Ring")
        # Slug keeps hyphens for spaces
        assert slug == "elden-ring"
    
    def test_special_characters(self):
        """Test removal of special characters."""
        slug = sanitize_slug("God of War: Ragnarök")
        assert ":" not in slug
        assert slug.replace("-", "").isalnum()
    
    def test_lowercase(self):
        """Test that slug is lowercase."""
        slug = sanitize_slug("TEST GAME")
        assert slug.islower()
    
    def test_accents_removed(self):
        """Test that accents are removed."""
        slug = sanitize_slug("Pokémon")
        assert "é" not in slug
