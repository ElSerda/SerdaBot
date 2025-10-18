#!/usr/bin/env python3
"""
Script de comparaison Qwen2.5-1.5B vs Qwen2.5-3B
Teste le même prompt sur les deux modèles côte à côte
"""
import sys
import os
import httpx
import asyncio
import time

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.prompts.prompt_loader import build_messages


# Configuration des modèles (même endpoint, modèles différents)
MODELS = {
    "1.5B": {
        "endpoint": "http://localhost:1234/v1/chat/completions",
        "model_name": "qwen2.5-1.5b-instruct",
        "max_tokens": 120  # MAX_TOKENS_ASK actuel
    },
    "3B": {
        "endpoint": "http://localhost:1234/v1/chat/completions",
        "model_name": "qwen2.5-3b-instruct",
        "max_tokens": 120  # Même limite pour comparaison
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
    
    start = time.time()
    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.post(
                model_config["endpoint"],
                json=payload,
                headers={"Content-Type": "application/json"}
            )
            response.raise_for_status()
            data = response.json()
            result = data["choices"][0]["message"]["content"].strip()
            tokens = data.get("usage", {}).get("completion_tokens", 0)
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return None
    
    elapsed = time.time() - start
    
    if result:
        print(f"📤 Question: {question}")
        print(f"💬 Réponse ({len(result)} chars, {tokens} tokens, {elapsed:.2f}s):")
        print(f"   {result}")
        
        # Check si phrase complète
        complete = result.rstrip().endswith(('.', '!', '?'))
        status = "✅ PHRASE COMPLÈTE" if complete else "❌ COUPÉ"
        tok_per_sec = tokens / elapsed if elapsed > 0 else 0
        print(f"Status: {status} | Vitesse: {tok_per_sec:.1f} tok/s")
        
        return {"text": result, "tokens": tokens, "time": elapsed, "complete": complete}
    else:
        print(f"❌ Échec du modèle")
        return None


async def compare_models():
    """Compare les deux modèles sur toutes les questions"""
    print("\n" + "="*100)
    print("🔬 COMPARAISON QWEN 1.5B vs 3B - Sweet Spot Test")
    print("="*100)
    print(f"Prompt: Réponds de façon concise et précise en 1-2 phrases. Maximum 230 caractères.")
    print(f"max_tokens: 120 (identique pour les deux)")
    print(f"Mode: ASK (questions factuelles)")
    print("="*100)
    
    stats_1_5b = {"complete": 0, "total": 0, "total_time": 0, "total_tokens": 0}
    stats_3b = {"complete": 0, "total": 0, "total_time": 0, "total_tokens": 0}
    
    for i, question in enumerate(TEST_QUESTIONS, 1):
        print(f"\n\n{'#'*100}")
        print(f"# TEST {i}/{len(TEST_QUESTIONS)}: {question}")
        print(f"{'#'*100}")
        
        # Test 1.5B
        result_1_5b = await test_model("1.5B", question)
        if result_1_5b:
            stats_1_5b["total"] += 1
            stats_1_5b["complete"] += 1 if result_1_5b["complete"] else 0
            stats_1_5b["total_time"] += result_1_5b["time"]
            stats_1_5b["total_tokens"] += result_1_5b["tokens"]
        
        # Test 3B
        result_3b = await test_model("3B", question)
        if result_3b:
            stats_3b["total"] += 1
            stats_3b["complete"] += 1 if result_3b["complete"] else 0
            stats_3b["total_time"] += result_3b["time"]
            stats_3b["total_tokens"] += result_3b["tokens"]
        
        # Comparaison
        print(f"\n{'─'*100}")
        print("📊 COMPARAISON:")
        print(f"{'─'*100}")
        if result_1_5b and result_3b:
            print(f"1.5B: {len(result_1_5b['text'])} chars, {result_1_5b['time']:.2f}s, {result_1_5b['tokens']/result_1_5b['time']:.1f} tok/s")
            print(f"3B:   {len(result_3b['text'])} chars, {result_3b['time']:.2f}s, {result_3b['tokens']/result_3b['time']:.1f} tok/s")
        print(f"{'─'*100}")
    
    print("\n\n" + "="*100)
    print("🏁 STATISTIQUES FINALES")
    print("="*100)
    
    if stats_1_5b["total"] > 0:
        avg_speed_1_5b = stats_1_5b["total_tokens"] / stats_1_5b["total_time"]
        complete_pct_1_5b = (stats_1_5b["complete"] / stats_1_5b["total"]) * 100
        print(f"\n1.5B: {stats_1_5b['complete']}/{stats_1_5b['total']} phrases complètes ({complete_pct_1_5b:.1f}%)")
        print(f"      Vitesse moyenne: {avg_speed_1_5b:.1f} tok/s")
    
    if stats_3b["total"] > 0:
        avg_speed_3b = stats_3b["total_tokens"] / stats_3b["total_time"]
        complete_pct_3b = (stats_3b["complete"] / stats_3b["total"]) * 100
        print(f"\n3B:   {stats_3b['complete']}/{stats_3b['total']} phrases complètes ({complete_pct_3b:.1f}%)")
        print(f"      Vitesse moyenne: {avg_speed_3b:.1f} tok/s")
    
    print("\n" + "="*100)


if __name__ == "__main__":
    asyncio.run(compare_models())
