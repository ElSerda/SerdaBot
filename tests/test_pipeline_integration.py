"""
Tests d'intégration du pipeline complet
Teste le flux réel : User input → Cache → Wikipedia → Modèle → Output
"""
import pytest

from src.config.config import load_config
from src.utils.cache_manager import clear_cache, get_cached_or_fetch, load_cache
from src.utils.model_utils import call_model


class TestPipelineIntegration:
    """Tests du pipeline complet (comme dans ask_command.py)"""
    
    @pytest.fixture(autouse=True)
    def setup_teardown(self):
        """Setup : charge config et nettoie cache avant chaque test"""
        self.config = load_config()
        clear_cache()
        yield
        # Teardown : rien pour l'instant
    
    @pytest.mark.asyncio
    async def test_pipeline_cache_miss_wikipedia_hit(self):
        """Test : Cache MISS → Wikipedia HIT → Cache sauvegardé"""
        question = "C'est quoi Python ?"
        
        # 1er appel : Cache MISS, Wikipedia devrait trouver
        answer1 = await get_cached_or_fetch(question)
        
        assert answer1 is not None, "Wikipedia devrait trouver Python"
        assert len(answer1) > 50, "Réponse Wikipedia devrait être substantielle"
        assert "langage" in answer1.lower() or "programmation" in answer1.lower(), \
            "Réponse devrait mentionner 'langage' ou 'programmation'"
        
        # 2e appel : Cache HIT (même réponse, instantané)
        answer2 = await get_cached_or_fetch(question)
        
        assert answer2 == answer1, "Cache devrait retourner la même réponse"
    
    @pytest.mark.llm
    @pytest.mark.asyncio
    async def test_pipeline_wikipedia_fail_fallback_model(self):
        """Test : Wikipedia FAIL → Fallback modèle (nécessite LLM local)"""
        # Question très spécifique que Wikipedia ne trouvera pas
        question = "C'est quoi un truc imaginaire complètement inventé par moi ?"
        
        # get_cached_or_fetch devrait retourner None (Wikipedia fail)
        cached_answer = await get_cached_or_fetch(question)
        
        # Si Wikipedia fail, on devrait avoir None (pas de cache)
        if cached_answer is None:
            # Fallback modèle (comme dans ask_command.py)
            model_answer = await call_model(question, self.config, mode='ask')
            
            assert model_answer is not None, "Le modèle devrait toujours retourner une réponse"
            assert len(model_answer) > 0, "Réponse modèle ne devrait pas être vide"
        else:
            # Si Wikipedia a trouvé quelque chose (rare), c'est OK aussi
            assert len(cached_answer) > 0
    
    @pytest.mark.asyncio
    async def test_pipeline_normalization_works(self):
        """Test : Normalisation permet de trouver dans cache/Wikipedia"""
        # Variations de la même question
        questions = [
            "C'est quoi Docker ?",
            "Parle moi de Docker",
            "Explique moi Docker",
            "Tu connais Docker ?"
        ]
        
        answers = []
        for q in questions:
            answer = await get_cached_or_fetch(q)
            if answer:  # Si Wikipedia trouve
                answers.append(answer)
        
        # Au moins une devrait trouver grâce à la normalisation
        assert len(answers) > 0, "Au moins une variation devrait trouver Docker"
        
        # Si plusieurs trouvent, devraient être identiques (même clé normalisée)
        if len(answers) > 1:
            assert all(a == answers[0] for a in answers), \
                        "Toutes les variations devraient retourner la même réponse (même clé normalisée)"
    
    @pytest.mark.llm
    @pytest.mark.asyncio
    async def test_pipeline_mode_ask_vs_chill(self):
        """Test : Mode ASK (cache) vs CHILL (direct modèle) - Nécessite LLM local"""        # Mode ASK : utilise le cache/Wikipedia
        ask_question = "C'est quoi la photosynthèse ?"
        ask_answer = await get_cached_or_fetch(ask_question)
        
        # Mode CHILL : direct modèle (pas de cache)
        chill_input = "Salut !"
        chill_answer = await call_model(chill_input, self.config, mode='chill')
        
        # Validations
        if ask_answer:  # Si Wikipedia trouve
            assert len(ask_answer) > 80, "Réponse ASK devrait être substantielle"
        
        assert chill_answer is not None, "Mode CHILL devrait toujours répondre"
        assert len(chill_answer) > 0, "Réponse CHILL ne devrait pas être vide"
    
    @pytest.mark.asyncio
    async def test_pipeline_cache_persistence(self):
        """Test : Cache persiste entre load_cache() et save_cache()"""
        question = "C'est quoi React ?"
        
        # 1er appel
        answer1 = await get_cached_or_fetch(question)
        
        if answer1:  # Si Wikipedia trouve
            # Recharger le cache depuis le fichier
            load_cache()
            
            # 2e appel après reload
            answer2 = await get_cached_or_fetch(question)
            
            assert answer2 == answer1, "Cache devrait persister après reload"
    
    @pytest.mark.asyncio
    async def test_pipeline_handles_hardware_queries(self):
        """Test : Pipeline gère correctement les questions hardware"""
        hardware_questions = [
            "C'est quoi le Ryzen 9 7950X3D ?",
            "Tu connais la RTX 4090 ?",
        ]
        
        for question in hardware_questions:
            answer = await get_cached_or_fetch(question)
            
            # Devrait trouver via Wikipedia (redirections hardware)
            if answer:
                assert len(answer) > 30, f"Réponse hardware pour '{question}' devrait être substantielle"
                # Vérifier mots-clés attendus
                assert any(word in answer.lower() for word in ['amd', 'processeur', 'nvidia', 'graphique', 'gpu', 'carte']), \
                    "Réponse devrait contenir des mots-clés hardware pertinents"
    
    @pytest.mark.llm
    @pytest.mark.asyncio
    async def test_pipeline_max_tokens_respected(self):
        """Test : MAX_TOKENS_ASK=120 permet réponses complètes - Nécessite LLM local"""
        # Question nécessitant une réponse détaillée
        question = "C'est quoi un trou noir ?"
        
        answer = await get_cached_or_fetch(question)
        
        if not answer:  # Si Wikipedia fail, tester avec modèle
            answer = await call_model(question, self.config, mode='ask')
        
        # Avec MAX_TOKENS_ASK=120, on devrait avoir des réponses >100 chars
        assert answer is not None
        assert len(answer) > 0, "Réponse ne devrait pas être vide"
        
        # Vérifier qu'on n'a pas de troncature brutale (devrait finir par ponctuation)
        if len(answer) > 50:  # Si réponse substantielle
            last_char = answer.rstrip()[-1] if answer.rstrip() else ''
            assert last_char in '.!?…', \
                f"Réponse longue devrait finir par ponctuation, trouvé '{last_char}'"


class TestPipelineEdgeCases:
    """Tests des cas limites du pipeline"""
    
    @pytest.fixture(autouse=True)
    def setup_config(self):
        """Setup : charge config"""
        self.config = load_config()
        yield
    
    @pytest.mark.asyncio
    async def test_empty_query(self):
        """Test : Query vide ne devrait pas crasher"""
        answer = await get_cached_or_fetch("")
        # Devrait retourner None ou réponse vide sans crash
        assert answer is None or len(answer) == 0
    
    @pytest.mark.asyncio
    async def test_very_long_query(self):
        """Test : Query très longue ne devrait pas crasher"""
        long_query = "C'est quoi " + "le truc " * 100 + "?"
        
        try:
            _answer = await get_cached_or_fetch(long_query)
            # Si ça ne crash pas, c'est OK
            assert True
        except Exception as e:
            pytest.fail(f"Pipeline ne devrait pas crasher sur query longue: {e}")
    
    @pytest.mark.asyncio
    async def test_special_characters_in_query(self):
        """Test : Caractères spéciaux ne devraient pas crasher"""
        special_queries = [
            "C'est quoi l'ADN ???",
            "Python >>> Java",
            "C++ vs C#",
            "Qu'est-ce que <HTML> ?",
        ]
        
        for query in special_queries:
            try:
                _answer = await get_cached_or_fetch(query)
                # Si ça ne crash pas, c'est OK
                assert True
            except Exception as e:
                pytest.fail(f"Pipeline crashe sur '{query}': {e}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
