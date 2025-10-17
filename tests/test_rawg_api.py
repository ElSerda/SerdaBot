"""Tests for RAWG API module."""

import pytest
from unittest.mock import patch, MagicMock
from core.rawg_api import query_rawg_game


class TestRawgApi:
    """Tests for RAWG API integration."""
    
    @patch('core.rawg_api.requests.get')
    def test_query_rawg_game_success(self, mock_get):
        """Test successful RAWG game query."""
        # Mock successful response
        mock_response = MagicMock()
        mock_response.json.return_value = {
            'results': [{
                'name': 'Test Game',
                'slug': 'test-game',
                'description_raw': 'A great test game',
                'released': '2024-01-01',
                'platforms': [
                    {'platform': {'name': 'PC'}},
                    {'platform': {'name': 'PlayStation 5'}}
                ]
            }]
        }
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response
        
        config = {'rawg': {'api_key': 'test_key'}}
        result = query_rawg_game('Test Game', config)
        
        assert result is not None
        assert result['name'] == 'Test Game'
        assert 'test game' in result['summary'].lower()
    
    @patch('core.rawg_api.requests.get')
    def test_query_rawg_game_no_api_key(self, mock_get):
        """Test RAWG query without API key."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            'results': [{
                'name': 'Test Game',
                'slug': 'test-game',
                'description_raw': 'A test game'
            }]
        }
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response
        
        config = {}
        result = query_rawg_game('Test Game', config)
        
        # Should still work without API key (limited rate)
        assert result is not None
    
    @patch('core.rawg_api.requests.get')
    def test_query_rawg_game_no_results(self, mock_get):
        """Test RAWG query with no results."""
        mock_response = MagicMock()
        mock_response.json.return_value = {'results': []}
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response
        
        config = {}
        
        with pytest.raises(Exception) as excinfo:
            query_rawg_game('Nonexistent Game', config)
        
        assert 'Aucun résultat' in str(excinfo.value)
    
    @patch('core.rawg_api.requests.get')
    def test_query_rawg_game_with_platforms(self, mock_get):
        """Test RAWG query result includes platforms."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            'results': [{
                'name': 'Multi-Platform Game',
                'slug': 'multi-game',
                'description_raw': 'Available everywhere',
                'platforms': [
                    {'platform': {'name': 'PC'}},
                    {'platform': {'name': 'Xbox Series X|S'}},
                    {'platform': {'name': 'PlayStation 5'}}
                ]
            }]
        }
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response
        
        config = {}
        result = query_rawg_game('Multi-Platform Game', config)
        
        assert 'PC' in result['platforms']
        assert 'Xbox' in result['platforms'] or 'Series X' in result['platforms']
