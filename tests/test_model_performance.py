"""
Test de performance et validation du modèle V3
==============================================
Vérifie que le modèle génère des réponses cohérentes, concises et complètes
Inclut un warmup pour des métriques stables
"""
import time

import pytest

from src.config.config import load_config
from src.prompts.prompt_loader import make_prompt
from src.utils.model_utils import call_model

# Questions de test variées
TEST_QUESTIONS = [
    "Salut !",
    "C'est quoi Python ?",
    "Parle-moi de Django",
    "tu connais Minecraft ?",
    "Explique les tests unitaires",
    "Comment faire une API REST ?",
    "C'est quoi Git ?",
    "Pourquoi utiliser TypeScript ?",
]


@pytest.fixture(scope="module")
def config():
    """Load config once for all tests."""
    return load_config()


@pytest.mark.llm
@pytest.mark.asyncio
async def test_model_warmup(config):
    """Warmup du modèle avec 2 requêtes simples."""
    print("\n🔥 Warmup du modèle...")
    
    for i in range(2):
        unique_user = f"warmup_{i}"
        prompt = make_prompt(mode="chill", content="test", user=unique_user)
        response = await call_model(prompt, config, user=unique_user, mode="chill")
        assert response is not None, f"Warmup {i+1}/2 failed"
        print(f"   ✅ Warmup {i+1}/2: {len(response)} chars")
    
    print("   🔥 Modèle prêt !\n")


@pytest.mark.llm
@pytest.mark.asyncio
async def test_model_coherence(config):
    """
    Test que le modèle génère des réponses cohérentes et pertinentes.
    
    Vérifie:
    - Phrases complètes (finissent par . ! ? ou ```)
    - Longueur raisonnable (< 300 chars pour Twitch)
    - Cohérence basique (pas de mots absurdes)
    """
    print("\n🧪 Test de cohérence sur 8 questions")
    print("=" * 70)
    
    results = []
    coherent_count = 0
    complete_count = 0
    
    for i, question in enumerate(TEST_QUESTIONS, 1):
        print(f"\n❓ Q{i}: {question}")
        
        unique_user = f"test_coherence_{i}"
        prompt = make_prompt(mode="chill", content=question, user=unique_user)
        response = await call_model(prompt, config, user=unique_user, mode="chill")
        
        assert response is not None, f"Question {i} returned None"
        
        # Analyse de la réponse
        char_count = len(response)
        is_complete = response.rstrip().endswith((".", "!", "?", "```"))
        
        # Détection de mots absurdes (heuristique simple)
        nonsense_words = ["cyborg", "étoile du", "jambes solides", "botte cyber"]
        has_nonsense = any(word in response.lower() for word in nonsense_words)
        
        is_coherent = is_complete and not has_nonsense and char_count < 300
        
        if is_complete:
            complete_count += 1
        if is_coherent:
            coherent_count += 1
        
        status = "✅" if is_coherent else "⚠️"
        print(f"{status} {char_count} chars: {response[:100]}...")
        
        results.append({
            "question": question,
            "response": response,
            "chars": char_count,
            "complete": is_complete,
            "coherent": is_coherent
        })
    
    # Assertions
    print("\n" + "=" * 70)
    print("📊 RÉSULTATS:")
    print(f"   Phrases complètes: {complete_count}/{len(TEST_QUESTIONS)} ({complete_count/len(TEST_QUESTIONS)*100:.0f}%)")
    print(f"   Réponses cohérentes: {coherent_count}/{len(TEST_QUESTIONS)} ({coherent_count/len(TEST_QUESTIONS)*100:.0f}%)")
    
    avg_chars = sum(r['chars'] for r in results) / len(results)
    print(f"   Longueur moyenne: {avg_chars:.0f} chars")
    print("=" * 70)
    
    # Au moins 80% de phrases complètes
    assert complete_count >= len(TEST_QUESTIONS) * 0.8, \
        f"Trop de phrases tronquées: {complete_count}/{len(TEST_QUESTIONS)}"
    
    # Au moins 75% de réponses cohérentes
    assert coherent_count >= len(TEST_QUESTIONS) * 0.75, \
        f"Trop de réponses incohérentes: {coherent_count}/{len(TEST_QUESTIONS)}"
    
    # Longueur moyenne raisonnable pour Twitch
    assert avg_chars < 300, f"Réponses trop longues: {avg_chars:.0f} chars (max 300)"
    
    print("\n✅ Test de cohérence réussi !")


@pytest.mark.llm
@pytest.mark.asyncio
async def test_model_response_time(config):
    """
    Test que le modèle répond dans des délais acceptables.
    
    Target: < 3s par réponse pour expérience Twitch fluide
    """
    print("\n⚡ Test de latence")
    print("=" * 70)
    
    import time
    
    durations = []
    
    # Test sur 5 questions variées
    test_questions = TEST_QUESTIONS[:5]
    
    for idx, question in enumerate(test_questions):
        unique_user = f"test_latency_{idx}"
        prompt = make_prompt(mode="chill", content=question, user=unique_user)
        
        start = time.time()
        response = await call_model(prompt, config, user=unique_user, mode="chill")
        duration = time.time() - start
        
        assert response is not None, f"Question '{question}' returned None"
        
        durations.append(duration)
        status = "✅" if duration < 3.0 else "⚠️"
        print(f"{status} {question:30s} → {duration:.2f}s")
    
    avg_duration = sum(durations) / len(durations)
    max_duration = max(durations)
    
    print("=" * 70)
    print(f"📊 Latence moyenne: {avg_duration:.2f}s")
    print(f"📊 Latence max: {max_duration:.2f}s")
    print("=" * 70)
    
    # Latence moyenne acceptable
    assert avg_duration < 3.0, f"Latence trop élevée: {avg_duration:.2f}s (max 3s)"
    
    print("\n✅ Test de latence réussi !")


@pytest.mark.llm
@pytest.mark.asyncio
async def test_model_conciseness(config):
    """
    Test que le modèle respecte la contrainte de concision.
    
    On tolère les dépassements sur questions complexes (tests unitaires, API, etc.)
    Chaque question utilise un user_id unique pour éviter l'accumulation de contexte.
    """
    print("\n📏 Test de concision")
    print("=" * 70)
    
    results = []
    latencies = []
    
    for idx, question in enumerate(TEST_QUESTIONS):
        start_time = time.time()
        # User ID unique pour chaque question = pas de contexte entre questions
        unique_user = f"test_concision_{idx}"
        prompt = make_prompt(mode="chill", content=question, user=unique_user)
        response = await call_model(prompt, config, user=unique_user, mode="chill")
        latency = time.time() - start_time
        
        assert response is not None, f"Question '{question}' returned None"
        
        char_count = len(response)
        results.append(char_count)
        latencies.append(latency)
        
        status = "✅" if char_count <= 150 else "⚠️" if char_count <= 400 else "❌"
        print(f"{status} {question:30s} → {char_count} chars, {latency:.2f}s")
    
    avg_chars = sum(results) / len(results)
    avg_latency = sum(latencies) / len(latencies)
    within_150 = sum(1 for c in results if c <= 150)
    within_400 = sum(1 for c in results if c <= 400)
    over_500 = sum(1 for c in results if c > 500)
    
    print("=" * 70)
    print(f"📊 Moyenne: {avg_chars:.0f} chars, {avg_latency:.2f}s")
    print(f"📊 ≤150 chars: {within_150}/{len(results)} ({within_150/len(results)*100:.0f}%)")
    print(f"📊 ≤400 chars: {within_400}/{len(results)} ({within_400/len(results)*100:.0f}%)")
    print("=" * 70)
    
    # Au moins 50% des réponses doivent être ≤150 chars (concises)
    assert within_150 >= len(results) * 0.5, \
        f"Pas assez de réponses concises: {within_150}/{len(results)}"
    
    # Moyenne raisonnable pour Twitch (< 200 chars)
    assert avg_chars < 200, \
        f"Moyenne trop élevée: {avg_chars:.0f} chars (max 200)"
    
    # Aucune réponse ne doit dépasser 500 chars (limite Twitch)
    assert over_500 == 0, \
        f"Réponses dépassent limite Twitch: {over_500}/{len(results)} > 500 chars"
    
    print("\n✅ Test de concision réussi !")
