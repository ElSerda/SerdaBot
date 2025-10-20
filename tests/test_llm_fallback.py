"""Tests pour le système de fallback LLM."""

import pytest
from src.core.fallbacks import get_fallback_response, get_all_fallback_intents, add_custom_fallback
from src.utils.llm_detector import is_llm_available, get_llm_mode


class TestLLMDetector:
    """Tests de détection de disponibilité du LLM."""
    
    def test_is_llm_available_returns_bool(self):
        """is_llm_available() doit retourner un booléen."""
        result = is_llm_available()
        assert isinstance(result, bool), "is_llm_available() doit retourner True ou False"
    
    def test_get_llm_mode_default_auto(self):
        """get_llm_mode() par défaut doit retourner 'auto'."""
        config = {"bot": {}}
        mode = get_llm_mode(config)
        assert mode in ["auto", "enabled", "disabled"], "Mode LLM doit être valide"


class TestFallbackResponses:
    """Tests du système de réponses fallback."""
    
    def test_get_fallback_response_ask(self):
        """get_fallback_response('ask') doit retourner une réponse valide."""
        response = get_fallback_response("ask")
        assert isinstance(response, str), "Doit retourner une string"
        assert len(response) > 5, "Réponse ne doit pas être vide"
        # Doit être une réponse liée au contexte LLM indisponible
        assert len(response) < 200, "Réponse doit être concise"
    
    def test_get_fallback_response_chill(self):
        """get_fallback_response('chill') doit retourner une salutation."""
        response = get_fallback_response("chill")
        assert isinstance(response, str), "Doit retourner une string"
        assert len(response) > 0, "Réponse ne doit pas être vide"
        # Doit être court et amical
        assert len(response) < 100, "Réponse chill doit être courte"
    
    def test_get_fallback_response_ask_timeout(self):
        """get_fallback_response('ask_timeout') doit gérer les timeouts."""
        response = get_fallback_response("ask_timeout")
        assert isinstance(response, str), "Doit retourner une string"
        assert len(response) > 0, "Réponse ne doit pas être vide"
    
    def test_get_fallback_response_ask_error(self):
        """get_fallback_response('ask_error') doit gérer les erreurs."""
        response = get_fallback_response("ask_error")
        assert isinstance(response, str), "Doit retourner une string"
        assert len(response) > 0, "Réponse ne doit pas être vide"
    
    def test_get_fallback_response_mode_silent(self):
        """Mode 'silent' doit retourner un message neutre."""
        response = get_fallback_response("ask", mode="silent")
        assert response == "Commande temporairement indisponible."
    
    def test_get_fallback_response_mode_minimal(self):
        """Mode 'minimal' doit retourner juste un emoji."""
        response = get_fallback_response("ask", mode="minimal")
        assert response == "🤖"
    
    def test_get_all_fallback_intents(self):
        """get_all_fallback_intents() doit retourner toutes les intentions."""
        intents = get_all_fallback_intents()
        assert isinstance(intents, list), "Doit retourner une liste"
        assert "ask" in intents, "Doit contenir 'ask'"
        assert "chill" in intents, "Doit contenir 'chill'"
        assert len(intents) >= 4, "Doit avoir au moins 4 intentions"
    
    def test_add_custom_fallback(self):
        """add_custom_fallback() doit permettre d'ajouter des réponses custom."""
        custom_intent = "test_custom"
        custom_responses = ["Test 1", "Test 2"]
        
        add_custom_fallback(custom_intent, custom_responses)
        
        response = get_fallback_response(custom_intent)  # type: ignore
        assert response in custom_responses, "Doit retourner une des réponses custom"
    
    def test_fallback_responses_are_random(self):
        """Les réponses fallback doivent varier (aléatoires)."""
        responses = set()
        
        # Générer 20 réponses pour "chill"
        for _ in range(20):
            response = get_fallback_response("chill")
            responses.add(response)
        
        # On devrait avoir au moins 2 réponses différentes
        assert len(responses) >= 2, "Les réponses doivent être aléatoires (variées)"
    
    def test_fallback_responses_are_twitch_safe(self):
        """Les réponses fallback ne doivent pas dépasser 500 chars."""
        for intent in ["ask", "chill", "ask_timeout", "ask_error"]:
            response = get_fallback_response(intent)  # type: ignore
            assert len(response) <= 500, f"Réponse {intent} trop longue pour Twitch: {len(response)} chars"
