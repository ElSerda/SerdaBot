#!/usr/bin/env python3
"""
Test de températures pour 1.5B vs 7B
Compare la créativité vs précision à différentes températures
"""
import sys
import os
import httpx
import asyncio

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.prompts.prompt_loader import build_messages


# Configuration
ENDPOINT = "http://localhost:1234/v1/chat/completions"
MODELS = ["qwen2.5-1.5b-instruct", "qwen2.5-7b-instruct"]
TEMPERATURES = [0.0, 0.2, 0.4, 0.6, 0.8, 1.0]
MAX_TOKENS = 80

# Questions de test (variées : animaux, tech, science, histoire, gaming)
TEST_QUESTIONS = [
    # Animaux
    "parle moi des pandas roux",
    "c'est quoi un axolotl",
    "les dauphins",
    # Tech/Programmation
    "c'est quoi python",
    "blockchain",
    "intelligence artificielle",
    "react",
    # Science
    "trou noir",
    "adn",
    "photosynthèse",
    # Histoire/Culture
    "empire romain",
    "révolution française",
    # Gaming
    "minecraft",
    "valorant",
    # Divers
    "comment fonctionne internet",
]


async def test_temperature(model_name: str, question: str, temperature: float):
    """Teste un modèle avec une température donnée"""
    
    # Build messages
    built = build_messages(mode="ask", content=question)
    
    # Override temperature
    payload = {
        "model": model_name,
        "messages": built["messages"],
        "temperature": temperature,
        "max_tokens": MAX_TOKENS,
        "stream": False
    }
    
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(
                ENDPOINT,
                json=payload,
                headers={"Content-Type": "application/json"}
            )
            response.raise_for_status()
            data = response.json()
            result = data["choices"][0]["message"]["content"].strip()
            finish_reason = data["choices"][0].get("finish_reason", "unknown")
            return result, finish_reason
    except Exception as e:
        return f"❌ Erreur: {e}", "error"


async def analyze_temperature_impact():
    """Analyse l'impact de la température sur les deux modèles"""
    
    print("\n" + "="*100)
    print("🌡️ ANALYSE TEMPÉRATURE - Impact sur 1.5B vs 7B")
    print("="*100)
    print(f"Températures testées: {TEMPERATURES}")
    print(f"max_tokens: {MAX_TOKENS}")
    print(f"Questions: {len(TEST_QUESTIONS)}")
    print("="*100)
    
    # Statistiques globales
    global_stats = {
        "1.5B": {"lengths": [], "complete": [], "temps": []},
        "7B": {"lengths": [], "complete": [], "temps": []}
    }
    
    for question in TEST_QUESTIONS:
        print(f"\n\n{'#'*100}")
        print(f"# QUESTION: {question}")
        print(f"{'#'*100}")
        
        for model_name in MODELS:
            model_short = "1.5B" if "1.5b" in model_name else "7B"
            print(f"\n{'='*100}")
            print(f"🤖 {model_short} - Tests températures")
            print(f"{'='*100}")
            
            results = []
            
            for temp in TEMPERATURES:
                result, finish = await test_temperature(model_name, question, temp)
                complete = result.rstrip().endswith(('.', '!', '?'))
                status = "✅" if complete else "❌"
                
                print(f"\n🌡️  T={temp:.1f} | {status} | {len(result)} chars | finish={finish}")
                print(f"   {result[:100]}{'...' if len(result) > 100 else ''}")
                
                results.append({
                    "temp": temp,
                    "result": result,
                    "length": len(result),
                    "complete": complete
                })
                
                # Collecte stats globales
                global_stats[model_short]["lengths"].append(len(result))
                global_stats[model_short]["complete"].append(complete)
                global_stats[model_short]["temps"].append(temp)
            
            # Analyse statistique par question
            print(f"\n{'─'*100}")
            print(f"📊 STATISTIQUES {model_short}:")
            avg_length = sum(r["length"] for r in results) / len(results)
            complete_rate = sum(1 for r in results if r["complete"]) / len(results) * 100
            print(f"   Longueur moyenne: {avg_length:.0f} chars")
            print(f"   Taux phrases complètes: {complete_rate:.0f}%")
            print(f"   Range longueur: {min(r['length'] for r in results)}-{max(r['length'] for r in results)} chars")
            print(f"{'─'*100}")
    
    # RÉSUMÉ GLOBAL
    print("\n\n" + "="*100)
    print("📊 RÉSUMÉ GLOBAL - TOUTES QUESTIONS")
    print("="*100)
    
    for model_short in ["1.5B", "7B"]:
        stats = global_stats[model_short]
        total_tests = len(stats["lengths"])
        avg_length = sum(stats["lengths"]) / total_tests
        min_length = min(stats["lengths"])
        max_length = max(stats["lengths"])
        complete_rate = sum(1 for c in stats["complete"] if c) / total_tests * 100
        
        print(f"\n🤖 {model_short}:")
        print(f"   Tests total: {total_tests}")
        print(f"   Longueur moyenne: {avg_length:.1f} chars")
        print(f"   Range: {min_length}-{max_length} chars")
        print(f"   Taux phrases complètes: {complete_rate:.1f}%")
        
        # Par température
        temp_stats = {}
        for i, temp in enumerate(stats["temps"]):
            if temp not in temp_stats:
                temp_stats[temp] = {"lengths": [], "complete": []}
            temp_stats[temp]["lengths"].append(stats["lengths"][i])
            temp_stats[temp]["complete"].append(stats["complete"][i])
        
        print(f"\n   Par température:")
        for temp in TEMPERATURES:
            if temp in temp_stats:
                avg_len = sum(temp_stats[temp]["lengths"]) / len(temp_stats[temp]["lengths"])
                complete = sum(1 for c in temp_stats[temp]["complete"] if c) / len(temp_stats[temp]["complete"]) * 100
                print(f"      T={temp:.1f}: avg={avg_len:.0f} chars, complete={complete:.0f}%")
    
    print("\n" + "="*100)
    print("🏁 FIN DES TESTS")
    print("="*100)
    print("\n💡 ANALYSE:")
    print("- Température basse (0.0-0.4) → Plus déterministe, moins de variation")
    print("- Température moyenne (0.4-0.6) → Équilibre créativité/précision")
    print("- Température haute (0.6-1.0) → Plus créatif, risque glitchs (7B chinois)")
    print("="*100)


if __name__ == "__main__":
    asyncio.run(analyze_temperature_impact())
