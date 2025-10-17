"""Pytest configuration and fixtures for SerdaBot tests."""

import sys
from pathlib import Path

import pytest

# Add src to path for imports
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))


@pytest.fixture
def sample_config():
    """Sample configuration for testing."""
    return {
        "twitch": {
            "token": "oauth:test_token",
            "client_id": "test_client_id",
            "client_secret": "test_client_secret",
            "bot_id": "123456789"
        },
        "bot": {
            "name": "test_bot",
            "channel": "test_channel",
            "cooldown": 60,
            "debug": False,
            "enabled_commands": ["ask", "game", "chill", "trad"],
            "model_endpoint": "http://127.0.0.1:1234/v1/chat/completions",
            "model_type": "openai",
            "openai_model": "gpt-3.5-turbo",
            "kofi_url": "https://ko-fi.com/test_user",
            "donation_message": "☕ Test donation message: {kofi_url}",
            "user_agent": "TestBot/1.0",
            "auto_translate": True
        },
        "igdb": {
            "client_id": "test_igdb_client_id",
            "client_secret": "test_igdb_client_secret"
        },
        "openai": {
            "api_key": "sk-test_openai_key"
        }
    }


@pytest.fixture
def mock_message():
    """Mock TwitchIO message object."""
    class MockAuthor:
        def __init__(self):
            self.name = "test_user"
            self.is_mod = False

    class MockChannel:
        def __init__(self):
            self.name = "test_channel"

        async def send(self, message):
            """Mock send method."""
            return message

    class MockMessage:
        def __init__(self):
            self.author = MockAuthor()
            self.channel = MockChannel()
            self.content = "test message"
            self.echo = False

    return MockMessage()
