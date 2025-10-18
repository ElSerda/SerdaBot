"""
Fact Cache Manager - Wikipedia Integration
Gère le cache des faits encyclopédiques pour réduire les hallucinations
"""
import asyncio
import json
import os
import time
from pathlib import Path
from typing import Dict, Optional

import httpx

from src.utils.translator import Translator

# Chemin du cache persistant
CACHE_DIR = Path("cache")
CACHE_FILE = CACHE_DIR / "dynamic_facts.json"
CACHE_DIR.mkdir(exist_ok=True)

# Variables globales
_fact_cache: Dict[str, str] = {}
_last_wiki_call = 0
_WIKI_RATE_LIMIT = 1.0  # 1 requête/sec
_translator = None  # Initialisé à la demande


def _get_translator():
    """Récupère l'instance du traducteur (lazy loading)."""
    global _translator
    if _translator is None:
        _translator = Translator()
    return _translator

# Redirections pour termes ambigus (Wikipedia)
_WIKI_REDIRECTS = {
    "python": "Python_(langage)",
    "react": "React_(JavaScript)",
    "java": "Java_(langage)",
    "rust": "Rust_(langage)",
    "swift": "Swift_(langage_d'Apple)",
    "docker": "Docker_(logiciel)",
    
    # Hardware - Processeurs AMD (Ryzen)
    "ryzen 9 9950x3d": "AMD_Ryzen",
    "ryzen 9950x3d": "AMD_Ryzen",
    "9950x3d": "AMD_Ryzen",
    "ryzen 9 7950x3d": "AMD_Ryzen",
    "ryzen 7950x3d": "AMD_Ryzen",
    "7950x3d": "AMD_Ryzen",
    "ryzen": "AMD_Ryzen",
    
    # Hardware - Processeurs Intel
    "i9-14900k": "Intel_Core",
    "i9 14900k": "Intel_Core",
    "14900k": "Intel_Core",
    "intel core": "Intel_Core",
    
    # Hardware - GPU NVIDIA
    "rtx 4090": "GeForce_40",
    "rtx 4080": "GeForce_40",
    "rtx 4070": "GeForce_40",
    "geforce": "GeForce",
    
    # Hardware - GPU AMD
    "rx 7900 xtx": "Radeon_RX_7000",
    "rx 7900xtx": "Radeon_RX_7000",
    "rx 7900": "Radeon_RX_7000",
    "radeon": "Radeon",
}


def load_cache(reset: bool = False):
    """Charge le cache depuis le fichier JSON au démarrage.
    
    Args:
        reset: Si True, vide le cache existant (mode expérimental)
    """
    global _fact_cache
    
    if reset:
        _fact_cache = {}
        if CACHE_FILE.exists():
            CACHE_FILE.unlink()
        print("[CACHE] 🔄 Cache réinitialisé (mode expérimental)")
        return
    
    if CACHE_FILE.exists():
        try:
            with open(CACHE_FILE, "r", encoding="utf-8") as f:
                _fact_cache = json.load(f)
            print(f"[CACHE] ✅ {len(_fact_cache)} faits chargés depuis {CACHE_FILE}")
        except Exception as e:
            print(f"[CACHE] ⚠️ Erreur chargement: {e}")
            _fact_cache = {}
    else:
        _fact_cache = {}
        print("[CACHE] 📦 Nouveau cache initialisé")


def save_cache():
    """Sauvegarde le cache sur disque (écriture atomique)."""
    try:
        # Sauvegarde atomique pour éviter corruption (write .tmp puis replace)
        temp_file = CACHE_FILE.with_suffix(".tmp")
        with open(temp_file, "w", encoding="utf-8") as f:
            json.dump(_fact_cache, f, ensure_ascii=False, indent=2)
        # os.replace() est atomique sur POSIX et Windows
        os.replace(str(temp_file), str(CACHE_FILE))
    except Exception as e:
        print(f"[CACHE] ❌ Erreur sauvegarde: {e}")


def normalize_key(query: str) -> str:
    """Normalise la question pour la recherche (minuscule, sans directives)."""
    import re
    
    key = query.strip().lower()
    key = key.rstrip("?!. ").strip()
    
    # Enlever les préfixes courants avec regex pour gérer "moi", "nous", etc.
    # Pattern: "explique (moi|nous|leur) X" → "X"
    conversational_patterns = [
        r"^c'est quoi\s+",
        r"^c quoi\s+",
        r"^c'est qui\s+",
        r"^c qui\s+",
        r"^tu connais\s+(le|la|les|l')?\s*",  # "tu connais le/la/les X"
        r"^connais tu\s+(le|la|les|l')?\s*",
        r"^connais-tu\s+(le|la|les|l')?\s*",
        r"^explique\s+(moi|nous|leur|lui)\s+",  # "explique moi X" (obligatoire)
        r"^explique\s+",  # "explique X" (sans pronom)
        r"^parle\s+(moi|nous)\s+(de|des|du)\s+",  # "parle moi de X" (obligatoire)
        r"^parle\s+(de|des|du)\s+",  # "parle de X" (sans pronom)
        r"^qu'est-ce que\s+(le|la|les|l')?\s*",
        r"^quest-ce que\s+(le|la|les|l')?\s*",
        r"^qu'est ce que\s+(le|la|les|l')?\s*",
        r"^qui est\s+",
        r"^qui sont\s+",
        r"^défini\s+",
        r"^définis\s+",
    ]
    
    for pattern in conversational_patterns:
        key = re.sub(pattern, "", key, flags=re.IGNORECASE).strip()
    
    # Enlever articles ("le", "la", "les", "un", "une", "des") au début
    articles = ["le ", "la ", "les ", "un ", "une ", "des ", "l'"]
    for article in articles:
        if key.startswith(article):
            key = key[len(article):].strip()
            break  # Un seul article max
    
    return key or query.strip().lower()


def is_factual_question(query: str) -> bool:
    """Détecte si la question mérite une recherche encyclopédique."""
    q = query.lower().strip()
    
    # Patterns sociaux à exclure (CHILL mode)
    social_patterns = ["salut", "hello", "hi", "yo", "gg", "lol", "mdr", "xd", "comment ça va", "comment vas"]
    if any(pattern in q for pattern in social_patterns):
        return False
    
    # Patterns factuels à inclure
    factual_patterns = [
        "quoi", "qu'est", "quest", "explique", "parle", "défini", "signifie", 
        "c'est", "c est", "comment", "pourquoi",
        "définition", "origine", "qui est", "qui sont"
    ]
    
    # Si au moins un pattern factuel ET plus de 1 mot → factuel
    has_factual = any(pattern in q for pattern in factual_patterns)
    has_length = len(q.split()) >= 1  # Au moins 1 mot après normalisation
    
    return has_factual or has_length  # Ou juste un mot (ex: "python", "axolotl")


async def search_wikipedia(query: str, lang: str = "fr") -> Optional[str]:
    """Cherche le bon titre d'article via l'API de recherche Wikipedia."""
    global _last_wiki_call
    
    # Respecter le rate limit
    now = time.time()
    if now - _last_wiki_call < _WIKI_RATE_LIMIT:
        await asyncio.sleep(_WIKI_RATE_LIMIT - (now - _last_wiki_call))
    
    try:
        search_url = f"https://{lang}.wikipedia.org/w/api.php"
        params = {
            "action": "opensearch",
            "search": query,
            "limit": 1,
            "namespace": 0,
            "format": "json"
        }
        
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.get(search_url, params=params)
            _last_wiki_call = time.time()
            
            if resp.status_code == 200:
                data = resp.json()
                # Format: [query, [titles], [descriptions], [urls]]
                if len(data) >= 2 and len(data[1]) > 0:
                    best_title = data[1][0]  # Premier résultat
                    print(f"[WIKI] 🔍 Trouvé: {query} → {best_title}")
                    return best_title
                    
    except Exception as e:
        print(f"[WIKI] ⚠️ Erreur recherche pour '{query}': {e}")
    
    return None


async def fetch_wiki_summary(topic: str, lang: str = "fr") -> Optional[str]:
    """Récupère un résumé Wikipedia court et propre (async)."""
    global _last_wiki_call
    
    if not topic.strip():
        return None
    
    # 1. Appliquer redirections manuelles si nécessaire (ex: python→Python_(langage))
    clean_topic = _WIKI_REDIRECTS.get(topic.lower(), topic)
    if clean_topic != topic:
        print(f"[WIKI] 🔀 Redirection manuelle: {topic} → {clean_topic}")
    else:
        # 2. Si pas de redirection manuelle, utiliser la recherche Wikipedia
        searched_title = await search_wikipedia(topic, lang)
        if searched_title:
            clean_topic = searched_title
    
    # 3. Respecter le rate limit
    now = time.time()
    if now - _last_wiki_call < _WIKI_RATE_LIMIT:
        await asyncio.sleep(_WIKI_RATE_LIMIT - (now - _last_wiki_call))
    
    try:
        clean_topic = clean_topic.strip().replace(" ", "_")
        url = f"https://{lang}.wikipedia.org/api/rest_v1/page/summary/{clean_topic}"
        
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.get(url)
            _last_wiki_call = time.time()
            
            if resp.status_code == 200:
                data = resp.json()
                extract = data.get("extract", "")
                
                if extract and len(extract) > 20:  # Éviter les stubs
                    # Nettoyer et tronquer à 230 caractères max
                    clean = " ".join(extract.replace("\n", " ").split())
                    
                    if len(clean) > 230:
                        # Couper à la dernière ponctuation avant 230
                        end = max(clean.rfind(p, 0, 230) for p in ".!?;")
                        clean = clean[:end + 1] if end != -1 else clean[:227] + "…"
                    
                    return clean
                    
    except Exception as e:
        print(f"[WIKI] ⚠️ Erreur pour '{topic}': {e}")
    
    return None


async def get_cached_or_fetch(query: str) -> Optional[str]:
    """Point d'entrée principal: cherche dans le cache ou Wikipedia."""
    normalized = normalize_key(query)
    
    # 1. Chercher dans le cache
    if normalized in _fact_cache:
        print(f"[CACHE] 💡 Hit: {normalized}")
        return _fact_cache[normalized]
    
    # 2. Vérifier si c'est une question factuelle (sinon → CHILL mode au modèle)
    if not is_factual_question(normalized):
        return None  # Question sociale, pas de cache
    
    # 3. Chercher sur Wikipedia FR
    print(f"[WIKI] 🔍 Recherche: {normalized}")
    wiki_answer = await fetch_wiki_summary(normalized, lang="fr")
    wiki_lang = "fr"
    
    # 4. Fallback Wikipedia EN si FR échoue (pour hardware, tech, etc.)
    if not wiki_answer:
        print("[WIKI] 🔄 Fallback EN...")
        wiki_answer = await fetch_wiki_summary(normalized, lang="en")
        wiki_lang = "en"
    
    # 5. Si trouvé en anglais, traduire en français
    if wiki_answer and wiki_lang == "en":
        translator = _get_translator()
        print("[WIKI] 🌐 Traduction EN→FR...")
        try:
            translated = translator.translate(wiki_answer, source='en', target='fr')
            if translated and not translated.startswith("⚠️"):
                wiki_answer = translated
                print(f"[WIKI] ✅ Traduit: {wiki_answer[:80]}...")
            else:
                print("[WIKI] ⚠️ Traduction échouée, fallback EN brut")
                # Garde le texte EN plutôt que de retourner None
        except Exception as e:
            print(f"[WIKI] ⚠️ Erreur traduction: {e}, fallback EN brut")
            # Garde le texte EN même en cas d'exception
    
    # 6. Sauvegarder dans le cache
    if wiki_answer:
        _fact_cache[normalized] = wiki_answer
        save_cache()
        print(f"[WIKI] ✅ Ajouté au cache: {normalized}")
        return wiki_answer
    
    # 7. Si Wikipedia échoue, ne rien retourner (permet au modèle de tenter une réponse)
    # Le "Je ne sais pas" sera géré par le prompt système du modèle
    print(f"[WIKI] ⚠️ Wikipedia n'a rien trouvé pour: {normalized} - fallback modèle")
    return None  # Permet au modèle de répondre depuis ses connaissances


def add_to_cache(query: str, answer: str):
    """Ajoute manuellement une paire question/réponse au cache (commande admin)."""
    key = normalize_key(query)
    
    # Validation minimale
    if len(answer) > 30 and "Je ne sais pas" not in answer:
        _fact_cache[key] = answer
        save_cache()
        print(f"[CACHE] ➕ Ajout manuel: {key}")
        return True
    return False


def get_cache_stats() -> Dict[str, str | int | bool]:
    """Retourne les statistiques du cache."""
    return {
        "total_entries": len(_fact_cache),
        "cache_file": str(CACHE_FILE),
        "file_exists": CACHE_FILE.exists()
    }


def clear_cache():
    """Vide le cache (commande admin)."""
    global _fact_cache
    _fact_cache = {}
    save_cache()
    print("[CACHE] 🗑️ Cache vidé")


# Charger le cache au démarrage du module
load_cache()
