"""Tests for translator module."""

import pytest
from utils.translator import Translator
import tempfile
import json
from pathlib import Path


@pytest.fixture
def temp_translator():
    """Create a translator with temporary files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        devs_file = Path(tmpdir) / "devs.json"
        blocked_file = Path(tmpdir) / "blocked_sites.json"
        whitelist_file = Path(tmpdir) / "bot_whitelist.json"
        blacklist_file = Path(tmpdir) / "bot_blacklist.json"
        
        translator = Translator(
            devs_file=str(devs_file),
            blocked_file=str(blocked_file),
            bot_whitelist_file=str(whitelist_file),
            bot_blacklist_file=str(blacklist_file)
        )
        yield translator


class TestDevManagement:
    """Tests for dev whitelist management."""
    
    def test_add_dev(self, temp_translator):
        """Test adding a dev to whitelist."""
        temp_translator.add_dev("testuser")
        assert temp_translator.is_dev("testuser")
    
    def test_remove_dev(self, temp_translator):
        """Test removing a dev from whitelist."""
        temp_translator.add_dev("testuser")
        assert temp_translator.remove_dev("testuser")
        assert not temp_translator.is_dev("testuser")
    
    def test_remove_nonexistent_dev(self, temp_translator):
        """Test removing a dev that doesn't exist."""
        assert not temp_translator.remove_dev("nonexistent")
    
    def test_get_devs(self, temp_translator):
        """Test getting list of devs."""
        temp_translator.add_dev("user1")
        temp_translator.add_dev("user2")
        devs = temp_translator.get_devs()
        assert "user1" in devs
        assert "user2" in devs
        assert len(devs) == 2


class TestBlockedSites:
    """Tests for blocked sites management."""
    
    def test_add_blocked_site(self, temp_translator):
        """Test adding a blocked site."""
        temp_translator.add_blocked_site("spam.com")
        assert "spam.com" in temp_translator.blocked_sites
    
    def test_remove_blocked_site(self, temp_translator):
        """Test removing a blocked site."""
        temp_translator.add_blocked_site("spam.com")
        assert temp_translator.remove_blocked_site("spam.com")
        assert "spam.com" not in temp_translator.blocked_sites
    
    def test_spam_bot_detection(self, temp_translator):
        """Test spam bot detection."""
        temp_translator.add_blocked_site("fakeviews")
        
        # Should detect spam
        assert temp_translator.is_spam_bot("fakeviews_bot", "check this out")
        
        # Should not detect (no blocked word)
        assert not temp_translator.is_spam_bot("normal_user", "hello world")
    
    def test_spam_bot_excludes_owner(self, temp_translator):
        """Test that channel owner is excluded from spam detection."""
        temp_translator.add_blocked_site("test")
        
        # Should not detect spam for channel owner
        assert not temp_translator.is_spam_bot("test_channel", "test message", "test_channel")


class TestBotWhitelistBlacklist:
    """Tests for bot whitelist/blacklist management."""
    
    def test_add_to_whitelist(self, temp_translator):
        """Test adding bot to whitelist."""
        temp_translator.add_bot_to_whitelist("nightbot")
        assert temp_translator.is_bot_whitelisted("nightbot")
    
    def test_add_to_blacklist(self, temp_translator):
        """Test adding bot to blacklist."""
        temp_translator.add_bot_to_blacklist("spambot")
        assert temp_translator.is_bot_blacklisted("spambot")
    
    def test_should_ignore_whitelisted(self, temp_translator):
        """Test that whitelisted bots are ignored."""
        temp_translator.add_bot_to_whitelist("nightbot")
        assert temp_translator.should_ignore_bot("nightbot")
    
    def test_should_ignore_blacklisted(self, temp_translator):
        """Test that blacklisted bots are ignored."""
        temp_translator.add_bot_to_blacklist("spambot")
        assert temp_translator.should_ignore_bot("spambot")
    
    def test_remove_from_whitelist(self, temp_translator):
        """Test removing bot from whitelist."""
        temp_translator.add_bot_to_whitelist("nightbot")
        assert temp_translator.remove_bot_from_whitelist("nightbot")
        assert not temp_translator.is_bot_whitelisted("nightbot")
    
    def test_get_whitelisted_bots(self, temp_translator):
        """Test getting list of whitelisted bots."""
        temp_translator.add_bot_to_whitelist("bot1")
        temp_translator.add_bot_to_whitelist("bot2")
        bots = temp_translator.get_whitelisted_bots()
        assert "bot1" in bots
        assert "bot2" in bots


class TestTranslationChecks:
    """Tests for translation helper methods."""
    
    def test_should_translate_for_dev(self, temp_translator):
        """Test translation check for dev."""
        temp_translator.add_dev("testdev")
        
        # Should translate (dev, not a command, long enough)
        assert temp_translator.should_translate("testdev", "Hello this is a test message")
        
        # Should not translate (command)
        assert not temp_translator.should_translate("testdev", "!ask something")
        
        # Should not translate (too short)
        assert not temp_translator.should_translate("testdev", "hi")
    
    def test_should_not_translate_for_non_dev(self, temp_translator):
        """Test that non-devs are not translated."""
        assert not temp_translator.should_translate("random_user", "Hello this is a message")
