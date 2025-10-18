#!/usr/bin/env python3
"""
Script de comparaison Qwen2.5-1.5B vs Qwen2.5-7B
Teste le même prompt sur les deux modèles côte à côte
"""
import sys
import os
import httpx
import asyncio

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.prompts.prompt_loader import build_messages


# Configuration des modèles (même endpoint, modèles différents)
MODELS = {
    "1.5B": {
        "endpoint": "http://localhost:1234/v1/chat/completions",
        "model_name": "qwen2.5-1.5b-instruct",
        "max_tokens": 80  # Augmenté pour comparaison équitable
    },
    "7B": {
        "endpoint": "http://localhost:1234/v1/chat/completions",
        "model_name": "qwen2.5-7b-instruct",
        "max_tokens": 80  # Même limite pour comparaison
    }
}


# Questions de test
TEST_QUESTIONS = [
    "parle moi des pandas roux",
    "c'est quoi python",
    "blockchain",
    "comment fonctionne un ssd",
    "explique moi l'ia",
]


async def test_model(model_key: str, question: str, mode: str = "ask"):
    """Teste un modèle avec une question"""
    model_config = MODELS[model_key]
    
    print(f"\n{'='*100}")
    print(f"🤖 {model_key} - {model_config['model_name']}")
    print(f"{'='*100}")
    
    # Build messages avec le prompt loader
    built = build_messages(mode=mode, content=question)
    
    # Préparer le payload pour LM Studio
    payload = {
        "model": model_config["model_name"],
        "messages": built["messages"],
        "temperature": built["temperature"],
        "max_tokens": model_config["max_tokens"],
        "stream": False
    }
    
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(
                model_config["endpoint"],
                json=payload,
                headers={"Content-Type": "application/json"}
            )
            response.raise_for_status()
            data = response.json()
            result = data["choices"][0]["message"]["content"].strip()
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return None
    
    if result:
        print(f"📤 Question: {question}")
        print(f"💬 Réponse ({len(result)} chars):")
        print(f"   {result}")
        
        # Check si phrase complète
        complete = result.rstrip().endswith(('.', '!', '?'))
        status = "✅ PHRASE COMPLÈTE" if complete else "❌ COUPÉ"
        print(f"Status: {status}")
    else:
        print(f"❌ Échec du modèle")
    
    return result


async def compare_models():
    """Compare les deux modèles sur toutes les questions"""
    print("\n" + "="*100)
    print("🔬 COMPARAISON QWEN 1.5B vs 7B - Prompt Qwen3 + Exemples Vrais")
    print("="*100)
    print(f"Prompt: Réponds en une phrase. Maximum 230 caractères.")
    print(f"max_tokens: 80 (identique pour les deux)")
    print(f"Exemples: panda roux (vrai), python, ssd")
    print("="*100)
    
    for i, question in enumerate(TEST_QUESTIONS, 1):
        print(f"\n\n{'#'*100}")
        print(f"# TEST {i}/{len(TEST_QUESTIONS)}: {question}")
        print(f"{'#'*100}")
        
        # Test 1.5B
        result_1_5b = await test_model("1.5B", question)
        
        # Test 7B
        result_7b = await test_model("7B", question)
        
        # Comparaison
        print(f"\n{'─'*100}")
        print("📊 COMPARAISON:")
        print(f"{'─'*100}")
        if result_1_5b and result_7b:
            print(f"1.5B: {len(result_1_5b)} chars | 7B: {len(result_7b)} chars")
            print(f"Ratio longueur: {len(result_7b)/len(result_1_5b):.2f}x")
        print(f"{'─'*100}")
    
    print("\n\n" + "="*100)
    print("🏁 FIN DES TESTS")
    print("="*100)


if __name__ == "__main__":
    asyncio.run(compare_models())
