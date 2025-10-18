"""
Tests unitaires pour les Quick Wins (v1.1+)
- MAX_TOKENS_ASK = 120
- Cache atomique (os.replace)
- Fallback traduction robuste
- Normalisation regex améliorée
"""
import pytest

from src.utils.cache_manager import CACHE_FILE, normalize_key, save_cache
from src.utils.model_utils import MAX_TOKENS_ASK, MAX_TOKENS_CHILL


class TestMaxTokensConfig:
    """Vérifie que MAX_TOKENS_ASK est à 120 (Quick Win #1)"""
    
    def test_max_tokens_ask_is_120(self):
        """MAX_TOKENS_ASK doit être 120 pour éviter les cuts à 230 chars"""
        assert MAX_TOKENS_ASK == 120, f"MAX_TOKENS_ASK devrait être 120, trouvé {MAX_TOKENS_ASK}"
    
    def test_max_tokens_chill_is_60(self):
        """Vérifie que MAX_TOKENS_CHILL est 60 (commit c9e9a70)"""
        from utils.model_utils import MAX_TOKENS_CHILL

        assert MAX_TOKENS_CHILL == 60, f"MAX_TOKENS_CHILL devrait être 60, trouvé {MAX_TOKENS_CHILL}"


class TestAtomicCacheWrite:
    """Vérifie que save_cache utilise os.replace (Quick Win #2)"""
    
    def test_save_cache_uses_os_replace(self):
        """save_cache doit utiliser os.replace pour écriture atomique"""
        import inspect
        source = inspect.getsource(save_cache)
        assert 'os.replace' in source, "save_cache devrait utiliser os.replace pour écriture atomique"
    
    def test_save_cache_creates_tmp_file(self):
        """save_cache doit créer un fichier .tmp avant replace"""
        import inspect
        source = inspect.getsource(save_cache)
        assert '.tmp' in source, "save_cache devrait utiliser un fichier temporaire .tmp"


class TestNormalizationRegex:
    """Vérifie que la normalisation regex fonctionne correctement (Quick Win #4)"""
    
    @pytest.mark.parametrize("input_query,expected", [
        # "Parle moi de/du" doit être nettoyé
        ("Parle moi du panda roux", "panda roux"),
        ("Parle moi de la photosynthèse", "photosynthèse"),
        ("Parle de Python", "python"),  # Sans pronom
        
        # "Explique moi" doit être nettoyé
        ("Explique moi Docker", "docker"),
        ("Explique moi le fonctionnement du processeur", "fonctionnement du processeur"),
        ("Explique React", "react"),  # Sans pronom
        
        # "Tu connais" doit être nettoyé
        ("Tu connais l'Intel Core i9-14900K ?", "intel core i9-14900k"),
        ("Tu connais le panda roux", "panda roux"),
        
        # "C'est quoi" doit être nettoyé
        ("C'est quoi la théorie de la relativité", "théorie de la relativité"),
        ("C'est quoi le Ryzen 9 7950X3D", "ryzen 9 7950x3d"),
        
        # Articles doivent être enlevés
        ("le processeur Intel", "processeur intel"),
        ("la photosynthèse", "photosynthèse"),
        ("les pandas", "pandas"),
    ])
    def test_normalize_key(self, input_query, expected):
        """Teste que normalize_key nettoie correctement les formules conversationnelles"""
        result = normalize_key(input_query)
        assert result == expected, f"normalize_key('{input_query}') devrait retourner '{expected}', trouvé '{result}'"
    
    def test_normalize_key_handles_case_insensitive(self):
        """normalize_key doit être insensible à la casse"""
        assert normalize_key("PARLE MOI DU PANDA ROUX") == "panda roux"
        assert normalize_key("Explique Moi Docker") == "docker"
    
    def test_normalize_key_strips_punctuation(self):
        """normalize_key doit enlever la ponctuation finale"""
        assert normalize_key("C'est quoi Python ?") == "python"
        assert normalize_key("Tu connais Docker !") == "docker"
        assert normalize_key("Parle moi du panda roux.") == "panda roux"


class TestPromptConfiguration:
    """Vérifie que les prompts système sont correctement configurés"""
    
    def test_system_ask_prompt(self):
        """Prompt ASK doit mentionner 1-2 phrases et 230 caractères"""
        from src.prompts.prompt_loader import SYSTEM_ASK_FINAL
        
        assert "1-2 phrases" in SYSTEM_ASK_FINAL, "Prompt ASK devrait mentionner '1-2 phrases'"
        assert "230 caractères" in SYSTEM_ASK_FINAL, "Prompt ASK devrait mentionner '230 caractères'"
    
    def test_system_chill_prompt(self):
        """Prompt CHILL doit mentionner minimum 10 caractères"""
        from src.prompts.prompt_loader import SYSTEM_CHILL_FINAL
        
        assert "2-6 mots" in SYSTEM_CHILL_FINAL, "Prompt CHILL devrait mentionner '2-6 mots'"
        assert "minimum 10 caractères" in SYSTEM_CHILL_FINAL, "Prompt CHILL devrait mentionner 'minimum 10 caractères'"


class TestCacheManagerFallback:
    """Vérifie que le fallback traduction est robuste (Quick Win #3)"""
    
    def test_get_cached_or_fetch_returns_none_on_wikipedia_fail(self):
        """get_cached_or_fetch doit retourner None si Wikipedia échoue (pas 'Je ne sais pas')"""
        import inspect
        
        from src.utils.cache_manager import get_cached_or_fetch
        
        source = inspect.getsource(get_cached_or_fetch)
        
        # Vérifie que la fonction retourne None en cas d'échec Wikipedia
        # (permet au modèle de répondre au lieu de forcer "Je ne sais pas")
        assert 'return None' in source, "get_cached_or_fetch devrait retourner None en cas d'échec Wikipedia"


class TestCacheFileStructure:
    """Vérifie que la structure du cache est correcte"""
    
    def test_cache_dir_exists(self):
        """Le dossier cache/ doit exister"""
        from src.utils.cache_manager import CACHE_DIR
        assert CACHE_DIR.exists(), f"Le dossier cache {CACHE_DIR} devrait exister"
    
    def test_cache_file_path(self):
        """Le fichier cache doit être cache/dynamic_facts.json"""
        assert str(CACHE_FILE) == "cache/dynamic_facts.json", f"CACHE_FILE devrait être 'cache/dynamic_facts.json', trouvé '{CACHE_FILE}'"


class TestWikipediaRedirects:
    """Vérifie que les redirections Wikipedia importantes sont présentes"""
    
    def test_software_redirects_exist(self):
        """Les redirections pour langages de programmation doivent exister"""
        from src.utils.cache_manager import _WIKI_REDIRECTS
        
        assert "python" in _WIKI_REDIRECTS, "Redirection pour 'python' manquante"
        assert "docker" in _WIKI_REDIRECTS, "Redirection pour 'docker' manquante"
        assert "react" in _WIKI_REDIRECTS, "Redirection pour 'react' manquante"
    
    def test_hardware_redirects_exist(self):
        """Les redirections pour hardware doivent exister"""
        from src.utils.cache_manager import _WIKI_REDIRECTS
        
        # CPU
        assert any("ryzen" in k for k in _WIKI_REDIRECTS), "Redirection pour Ryzen manquante"
        
        # GPU
        assert any("rtx" in k for k in _WIKI_REDIRECTS), "Redirection pour RTX manquante"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
