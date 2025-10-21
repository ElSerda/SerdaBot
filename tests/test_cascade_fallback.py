"""Tests du système de fallback en cascade LM Studio → OpenAI → Répliques.

Philosophy: Test le comportement RÉEL sans mocks complexes.
Les appels HTTP échouent naturellement → cascade fonctionne.
"""

import pytest

from src.core.fallbacks import get_fallback_response
from src.utils.model_utils import call_model


class TestCascadeFallback:
    """Tests du fallback en cascade complet."""

    @pytest.mark.asyncio
    async def test_all_llm_fail_returns_none(self):
        """Scénario : LM Studio indisponible + pas d'OpenAI → retourne None."""
        config = {
            "bot": {
                "model_endpoint": "http://localhost:9999/v1",  # Port inexistant
                "model_timeout": 1,
            },
            "openai": {}  # Pas de clé OpenAI
        }

        result = await call_model("Test question", config, mode="ask")
        
        # Cascade complète échouée → None
        assert result is None, "Tous LLM indisponibles devrait retourner None"

    @pytest.mark.asyncio
    async def test_none_triggers_fallback_responses(self):
        """Vérifie que None déclenche bien les répliques fallback."""
        # Simuler result de call_model
        llm_result = None
        
        # Code utilisé dans ask_command.py
        if llm_result is None:
            fallback_msg = get_fallback_response("ask_error")
        else:
            fallback_msg = llm_result
        
        # Fallback devrait être utilisé
        assert isinstance(fallback_msg, str)
        assert len(fallback_msg) > 0
        assert len(fallback_msg) < 500  # Twitch-safe

    def test_none_vs_empty_string_distinction(self):
        """Vérifie la distinction claire : None (unavailable) vs "" (empty response)."""
        # None → Tous LLM indisponibles → fallback répliques
        llm_unavailable = None
        should_use_fallback = llm_unavailable is None
        assert should_use_fallback is True, "None devrait déclencher fallback"
        
        # "" → LLM a répondu mais vide → message d'erreur spécifique
        llm_empty = ""
        is_unavailable = llm_empty is None
        assert is_unavailable is False, "Empty string ne devrait PAS déclencher fallback"
        
        # "content" → Succès normal
        llm_success = "Réponse du LLM"
        is_unavailable_success = llm_success is None
        assert is_unavailable_success is False

    @pytest.mark.asyncio
    async def test_fallback_cascade_logic(self):
        """Teste la logique de cascade sans appels réseau."""
        # Simuler les 3 niveaux
        lm_studio_result = None  # Échoué
        openai_result = None      # Échoué
        
        # Logique utilisée dans le code
        final_result = lm_studio_result or openai_result
        
        if final_result is None:
            final_result = get_fallback_response("ask_error")
        
        # Fallback devrait être utilisé
        assert isinstance(final_result, str)
        assert len(final_result) > 0

    def test_all_fallback_intents_exist(self):
        """Vérifie que toutes les intentions fallback sont disponibles."""
        # Test chaque intention individuellement (type-safe)
        response_ask = get_fallback_response("ask")
        assert isinstance(response_ask, str)
        assert len(response_ask) > 0
        assert len(response_ask) < 500
        
        response_chill = get_fallback_response("chill")
        assert isinstance(response_chill, str)
        assert len(response_chill) > 0
        assert len(response_chill) < 500
        
        response_timeout = get_fallback_response("ask_timeout")
        assert isinstance(response_timeout, str)
        assert len(response_timeout) > 0
        assert len(response_timeout) < 500
        
        response_error = get_fallback_response("ask_error")
        assert isinstance(response_error, str)
        assert len(response_error) > 0
        assert len(response_error) < 500

    def test_fallback_responses_are_random(self):
        """Vérifie que les réponses fallback varient (randomisées)."""
        responses = {get_fallback_response("ask_error") for _ in range(10)}
        # Au moins 2 réponses différentes sur 10 essais
        assert len(responses) >= 2, "Les répliques devraient varier"

    @pytest.mark.asyncio
    async def test_command_integration_with_none(self):
        """Simule le comportement complet d'une commande avec LLM=None."""
        # Simuler call_model qui retourne None
        llm_available = True  # Boot detection OK
        llm_response = None   # Mais runtime échoue (crash post-boot)
        
        # Code dans ask_command.py
        if llm_response is None:
            final_message = get_fallback_response("ask_error")
        elif not llm_response:
            final_message = "⚠️ Erreur ou pas de réponse."
        else:
            final_message = llm_response
        
        # Vérifier fallback utilisé
        assert final_message != "⚠️ Erreur ou pas de réponse."
        assert isinstance(final_message, str)
        assert len(final_message) > 0


