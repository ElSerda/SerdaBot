#!/usr/bin/env python3
"""
🔬 Test Comparatif Massif: Qwen 2.5-1.5B vs GPT-4o-mini
Compare performances, vitesse, qualité sur 50+ cas réels Twitch
"""

import asyncio
import time
import httpx
from openai import AsyncOpenAI
import os
import sys
from typing import Dict, List, Any
import statistics

# Config
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    print("❌ OPENAI_API_KEY manquant")
    sys.exit(1)

LM_STUDIO_URL = "http://127.0.0.1:1234/v1/chat/completions"
QWEN_MODEL = "Qwen2.5-1.5B-Instruct-Q4_K_M"
GPT_MODEL = "gpt-4o-mini"

# Prompts optimaux SerdaBot (production)
SYSTEM_ASK = """Tu es serda_bot. Réponds de façon concise et claire.
Maximum 200 caractères par réponse.

Exemples:
"python" → "Langage populaire pour scripts et IA."
"blockchain" → "Technologie de registre décentralisé sécurisé."
"Elden Ring" → "Jeu action-RPG difficile de FromSoftware."
"""

SYSTEM_CHILL = """Tu es serda_bot, bot Twitch cool mais flemme de trop parler.
Réponds toujours en 1-5 mots maximum. Style décontracté.

Exemples:
"Salut !" → "Yo."
"lol" → "Marrant."
"gg" → "Stylé."
"merci" → "De rien !"
"bravo" → "Incroyable."
"comment ça va ?" → "Nickel."
"t'es qui toi ?" → "Le bot du stream."
"tu fais quoi ?" → "Je commente."
"pourquoi ?" → "Pour le fun."
"t'es où ?" → "Juste ici."
"""

# === BATCH DE TEST MASSIF (60 cas) ===

# ASK: Questions techniques/gaming (30 cas)
TEST_ASK = [
    # Tech/Programming (10)
    "C'est quoi Python ?",
    "C'est quoi JavaScript ?",
    "C'est quoi React ?",
    "C'est quoi Docker ?",
    "C'est quoi Git ?",
    "C'est quoi une API ?",
    "C'est quoi le cloud computing ?",
    "C'est quoi TypeScript ?",
    "C'est quoi Node.js ?",
    "C'est quoi Kubernetes ?",
    
    # Gaming (10)
    "C'est quoi Elden Ring ?",
    "C'est quoi Valorant ?",
    "C'est quoi Minecraft ?",
    "C'est quoi League of Legends ?",
    "C'est quoi Dark Souls ?",
    "C'est quoi Fortnite ?",
    "C'est quoi Baldur's Gate 3 ?",
    "C'est quoi Zelda Breath of the Wild ?",
    "C'est quoi Cyberpunk 2077 ?",
    "C'est quoi Among Us ?",
    
    # Concepts/Culture (10)
    "C'est quoi blockchain ?",
    "C'est quoi machine learning ?",
    "C'est quoi un NFT ?",
    "C'est quoi Twitch ?",
    "C'est quoi Discord ?",
    "C'est quoi un speedrun ?",
    "C'est quoi le cosplay ?",
    "C'est quoi un emote ?",
    "C'est quoi un raid Twitch ?",
    "C'est quoi un sub Twitch ?",
]

# CHILL: Interactions sociales variées (30 cas)
TEST_CHILL = [
    # Salutations (5)
    "Salut !",
    "Bonjour",
    "Hey",
    "Coucou",
    "Yo",
    
    # Réactions positives (8)
    "lol",
    "mdr",
    "gg",
    "bravo",
    "nice",
    "stylé",
    "bien joué",
    "excellent",
    
    # Remerciements (3)
    "merci",
    "thx",
    "thanks",
    
    # Questions identité (5)
    "t'es qui toi ?",
    "qui es-tu ?",
    "tu fais quoi ?",
    "t'es un bot ?",
    "tu t'appelles comment ?",
    
    # Questions état (4)
    "comment ça va ?",
    "ça va ?",
    "tu vas bien ?",
    "quoi de neuf ?",
    
    # Interjections (5)
    "pourquoi ?",
    "ah bon",
    "sérieux ?",
    "vraiment ?",
    "ok",
]


async def test_qwen(system: str, user_prompt: str, mode: str) -> Dict[str, Any]:
    """Test Qwen via LM Studio"""
    try:
        # Few-shot enrichi pour CHILL
        if mode == "chill":
            messages = [
                {"role": "system", "content": system},
                {"role": "user", "content": "lol"},
                {"role": "assistant", "content": "Marrant."},
                {"role": "user", "content": "t'es qui toi ?"},
                {"role": "assistant", "content": "Le bot du stream."},
                {"role": "user", "content": user_prompt},
            ]
        else:
            messages = [
                {"role": "system", "content": system},
                {"role": "user", "content": user_prompt}
            ]
        
        # Config optimale production
        temp = 0.4 if mode == "ask" else 0.5
        max_tokens = 80 if mode == "ask" else 20
        stop = ["\n\n"] if mode == "ask" else None
        repeat_penalty = 1.1 if mode == "ask" else 1.0
        
        payload = {
            "model": "local-model",
            "messages": messages,
            "temperature": temp,
            "max_tokens": max_tokens,
            "top_p": 0.9,
            "repeat_penalty": repeat_penalty,
            "stream": False
        }
        
        if stop:
            payload["stop"] = stop
        
        start = time.time()
        
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(LM_STUDIO_URL, json=payload)
            
            if response.status_code == 200:
                data = response.json()
                result = data["choices"][0]["message"]["content"].strip()
                duration = time.time() - start
                
                return {
                    "success": True,
                    "response": result,
                    "duration": duration,
                    "chars": len(result),
                    "words": len(result.split()),
                    "error": None
                }
    
    except Exception as e:
        return {
            "success": False,
            "response": None,
            "duration": 0,
            "chars": 0,
            "words": 0,
            "error": str(e)
        }


async def test_gpt(system: str, user_prompt: str, mode: str) -> Dict[str, Any]:
    """Test GPT-4o-mini via OpenAI"""
    try:
        client = AsyncOpenAI(api_key=OPENAI_API_KEY)
        
        # Config optimale production (même que Qwen)
        temp = 0.4 if mode == "ask" else 0.5
        max_tokens = 80 if mode == "ask" else 20
        
        start = time.time()
        
        response = await client.chat.completions.create(
            model=GPT_MODEL,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user_prompt}
            ],
            max_tokens=max_tokens,
            temperature=temp
        )
        
        duration = time.time() - start
        content = response.choices[0].message.content
        result = content.strip() if content else ""
        
        return {
            "success": True,
            "response": result,
            "duration": duration,
            "chars": len(result),
            "words": len(result.split()),
            "error": None
        }
    
    except Exception as e:
        return {
            "success": False,
            "response": None,
            "duration": 0,
            "chars": 0,
            "words": 0,
            "error": str(e)
        }


def validate_response(result: Dict[str, Any], mode: str) -> bool:
    """Valide si la réponse respecte les contraintes"""
    if not result["success"]:
        return False
    
    if mode == "ask":
        return result["chars"] <= 250
    else:
        return result["words"] <= 5


async def compare_models():
    """Comparaison massive Qwen vs GPT"""
    
    print("=" * 80)
    print("🔬 COMPARAISON MASSIVE: Qwen 2.5-1.5B vs GPT-4o-mini")
    print("=" * 80)
    print(f"📊 Cas de test: {len(TEST_ASK)} ASK + {len(TEST_CHILL)} CHILL = {len(TEST_ASK) + len(TEST_CHILL)} total")
    print(f"🤖 Modèles: {QWEN_MODEL} (local) vs {GPT_MODEL} (OpenAI)")
    print("=" * 80)
    
    # Vérifier LM Studio disponible
    try:
        async with httpx.AsyncClient(timeout=3.0) as client:
            await client.get("http://127.0.0.1:1234/v1/models")
        print("✅ LM Studio actif")
    except:
        print("❌ LM Studio indisponible - Impossible de tester Qwen")
        return
    
    print("\n🚀 Début des tests...\n")
    
    results = {
        "qwen": {"ask": [], "chill": []},
        "gpt": {"ask": [], "chill": []}
    }
    
    # === TEST ASK MODE ===
    print("=" * 80)
    print("📚 MODE ASK (Questions techniques/gaming)")
    print("=" * 80)
    
    for i, prompt in enumerate(TEST_ASK, 1):
        print(f"\n[{i}/{len(TEST_ASK)}] Test: {prompt}")
        
        # Test Qwen
        qwen_result = await test_qwen(SYSTEM_ASK, prompt, "ask")
        results["qwen"]["ask"].append(qwen_result)
        
        qwen_ok = validate_response(qwen_result, "ask")
        qwen_status = "✅" if qwen_ok else "❌"
        
        if qwen_result["success"]:
            print(f"  Qwen:  {qwen_status} {qwen_result['chars']:3d} chars | {qwen_result['duration']:.2f}s | {qwen_result['response'][:60]}...")
        else:
            print(f"  Qwen:  ❌ ERREUR: {qwen_result['error']}")
        
        # Test GPT
        gpt_result = await test_gpt(SYSTEM_ASK, prompt, "ask")
        results["gpt"]["ask"].append(gpt_result)
        
        gpt_ok = validate_response(gpt_result, "ask")
        gpt_status = "✅" if gpt_ok else "❌"
        
        if gpt_result["success"]:
            print(f"  GPT:   {gpt_status} {gpt_result['chars']:3d} chars | {gpt_result['duration']:.2f}s | {gpt_result['response'][:60]}...")
        else:
            print(f"  GPT:   ❌ ERREUR: {gpt_result['error']}")
        
        await asyncio.sleep(0.2)  # Rate limit
    
    # === TEST CHILL MODE ===
    print("\n" + "=" * 80)
    print("💬 MODE CHILL (Interactions sociales)")
    print("=" * 80)
    
    for i, prompt in enumerate(TEST_CHILL, 1):
        print(f"\n[{i}/{len(TEST_CHILL)}] Test: {prompt}")
        
        # Test Qwen
        qwen_result = await test_qwen(SYSTEM_CHILL, prompt, "chill")
        results["qwen"]["chill"].append(qwen_result)
        
        qwen_ok = validate_response(qwen_result, "chill")
        qwen_status = "✅" if qwen_ok else "❌"
        
        if qwen_result["success"]:
            print(f"  Qwen:  {qwen_status} {qwen_result['words']:2d} mots | {qwen_result['duration']:.2f}s | {qwen_result['response']}")
        else:
            print(f"  Qwen:  ❌ ERREUR: {qwen_result['error']}")
        
        # Test GPT
        gpt_result = await test_gpt(SYSTEM_CHILL, prompt, "chill")
        results["gpt"]["chill"].append(gpt_result)
        
        gpt_ok = validate_response(gpt_result, "chill")
        gpt_status = "✅" if gpt_ok else "❌"
        
        if gpt_result["success"]:
            print(f"  GPT:   {gpt_status} {gpt_result['words']:2d} mots | {gpt_result['duration']:.2f}s | {gpt_result['response']}")
        else:
            print(f"  GPT:   ❌ ERREUR: {gpt_result['error']}")
        
        await asyncio.sleep(0.2)
    
    # === STATISTIQUES FINALES ===
    print("\n\n" + "=" * 80)
    print("📊 STATISTIQUES COMPARATIVES")
    print("=" * 80)
    
    # Calculer stats par modèle/mode
    stats = {}
    
    for model in ["qwen", "gpt"]:
        stats[model] = {}
        
        for mode in ["ask", "chill"]:
            data = results[model][mode]
            successful = [r for r in data if r["success"]]
            valid = [r for r in successful if validate_response(r, mode)]
            
            if successful:
                success_rate = len(valid) / len(data) * 100
                avg_duration = statistics.mean([r["duration"] for r in successful])
                
                if mode == "ask":
                    avg_chars = statistics.mean([r["chars"] for r in successful])
                    max_chars = max([r["chars"] for r in successful])
                    stats[model][mode] = {
                        "success_rate": success_rate,
                        "avg_duration": avg_duration,
                        "avg_chars": avg_chars,
                        "max_chars": max_chars,
                        "total": len(data),
                        "valid": len(valid)
                    }
                else:
                    avg_words = statistics.mean([r["words"] for r in successful])
                    max_words = max([r["words"] for r in successful])
                    stats[model][mode] = {
                        "success_rate": success_rate,
                        "avg_duration": avg_duration,
                        "avg_words": avg_words,
                        "max_words": max_words,
                        "total": len(data),
                        "valid": len(valid)
                    }
            else:
                stats[model][mode] = {
                    "success_rate": 0,
                    "avg_duration": 0,
                    "total": len(data),
                    "valid": 0
                }
    
    # Affichage comparatif ASK
    print("\n🎯 MODE ASK (30 cas)")
    print("-" * 80)
    print(f"{'Métrique':<25} {'Qwen 1.5B':>20} {'GPT-4o-mini':>20} {'Gagnant':>10}")
    print("-" * 80)
    
    qwen_ask = stats["qwen"]["ask"]
    gpt_ask = stats["gpt"]["ask"]
    
    print(f"{'Taux succès':<25} {qwen_ask['success_rate']:>19.1f}% {gpt_ask['success_rate']:>19.1f}% {'':>10}")
    print(f"{'Cas valides':<25} {qwen_ask['valid']:>15}/{qwen_ask['total']:>2} {gpt_ask['valid']:>15}/{gpt_ask['total']:>2} {'':>10}")
    print(f"{'Latence moyenne':<25} {qwen_ask['avg_duration']:>18.2f}s {gpt_ask['avg_duration']:>18.2f}s {'':>10}")
    print(f"{'Chars moyenne':<25} {qwen_ask['avg_chars']:>18.1f}  {gpt_ask['avg_chars']:>18.1f}  {'':>10}")
    print(f"{'Chars max':<25} {qwen_ask['max_chars']:>20}  {gpt_ask['max_chars']:>18}  {'':>10}")
    
    # Affichage comparatif CHILL
    print("\n💬 MODE CHILL (30 cas)")
    print("-" * 80)
    print(f"{'Métrique':<25} {'Qwen 1.5B':>20} {'GPT-4o-mini':>20} {'Gagnant':>10}")
    print("-" * 80)
    
    qwen_chill = stats["qwen"]["chill"]
    gpt_chill = stats["gpt"]["chill"]
    
    print(f"{'Taux succès':<25} {qwen_chill['success_rate']:>19.1f}% {gpt_chill['success_rate']:>19.1f}% {'':>10}")
    print(f"{'Cas valides':<25} {qwen_chill['valid']:>15}/{qwen_chill['total']:>2} {gpt_chill['valid']:>15}/{gpt_chill['total']:>2} {'':>10}")
    print(f"{'Latence moyenne':<25} {qwen_chill['avg_duration']:>18.2f}s {gpt_chill['avg_duration']:>18.2f}s {'':>10}")
    print(f"{'Mots moyenne':<25} {qwen_chill['avg_words']:>18.1f}  {gpt_chill['avg_words']:>18.1f}  {'':>10}")
    print(f"{'Mots max':<25} {qwen_chill['max_words']:>20}  {gpt_chill['max_words']:>18}  {'':>10}")
    
    # Stats globales
    print("\n📈 GLOBAL (60 cas)")
    print("-" * 80)
    
    qwen_global_success = (qwen_ask['valid'] + qwen_chill['valid']) / 60 * 100
    gpt_global_success = (gpt_ask['valid'] + gpt_chill['valid']) / 60 * 100
    
    qwen_global_latency = (qwen_ask['avg_duration'] + qwen_chill['avg_duration']) / 2
    gpt_global_latency = (gpt_ask['avg_duration'] + gpt_chill['avg_duration']) / 2
    
    print(f"{'Taux succès global':<25} {qwen_global_success:>19.1f}% {gpt_global_success:>19.1f}%")
    print(f"{'Latence moyenne globale':<25} {qwen_global_latency:>18.2f}s {gpt_global_latency:>18.2f}s")
    
    # === VERDICT FINAL ===
    print("\n\n" + "=" * 80)
    print("🏆 VERDICT FINAL")
    print("=" * 80)
    
    print("\n✨ SUCCÈS (objectif: 80%)")
    if qwen_global_success > gpt_global_success:
        print(f"  🥇 Qwen 1.5B:    {qwen_global_success:.1f}% (GAGNANT)")
        print(f"  🥈 GPT-4o-mini:  {gpt_global_success:.1f}%")
    elif gpt_global_success > qwen_global_success:
        print(f"  🥇 GPT-4o-mini:  {gpt_global_success:.1f}% (GAGNANT)")
        print(f"  🥈 Qwen 1.5B:    {qwen_global_success:.1f}%")
    else:
        print(f"  🤝 ÉGALITÉ:      {qwen_global_success:.1f}%")
    
    print("\n⚡ VITESSE")
    if qwen_global_latency < gpt_global_latency:
        speedup = (gpt_global_latency / qwen_global_latency - 1) * 100
        print(f"  🥇 Qwen 1.5B:    {qwen_global_latency:.2f}s (GAGNANT, +{speedup:.0f}% plus rapide)")
        print(f"  🥈 GPT-4o-mini:  {gpt_global_latency:.2f}s")
    else:
        speedup = (qwen_global_latency / gpt_global_latency - 1) * 100
        print(f"  🥇 GPT-4o-mini:  {gpt_global_latency:.2f}s (GAGNANT, +{speedup:.0f}% plus rapide)")
        print(f"  🥈 Qwen 1.5B:    {qwen_global_latency:.2f}s")
    
    print("\n💰 COÛT")
    print("  🥇 Qwen 1.5B:    GRATUIT (local)")
    print("  🥈 GPT-4o-mini:  ~$0.01 pour ce test (60 requêtes)")
    
    print("\n🎯 RECOMMANDATION SERDABOT")
    print("-" * 80)
    
    if qwen_global_success >= 80 and qwen_global_latency < 0.5:
        print("  ✅ QWEN 1.5B PRIORITAIRE:")
        print(f"     - {qwen_global_success:.1f}% succès (objectif 80% atteint)")
        print(f"     - {qwen_global_latency:.2f}s latence (excellent pour live)")
        print("     - GRATUIT (local)")
        print(f"     - GPT-4o-mini en fallback ({gpt_global_success:.1f}% succès)")
    elif gpt_global_success >= 80:
        print("  ⚠️  GPT-4o-mini MEILLEUR:")
        print(f"     - {gpt_global_success:.1f}% succès vs {qwen_global_success:.1f}% Qwen")
        print(f"     - Qwen sous objectif 80% (config à améliorer)")
        print("     - Garder Qwen prioritaire (gratuit) mais accepter plus de fallback GPT")
    else:
        print("  ⚠️  AUCUN ATTEINT 80%:")
        print(f"     - Qwen: {qwen_global_success:.1f}%")
        print(f"     - GPT:  {gpt_global_success:.1f}%")
        print("     - Réviser prompts ou upgrade modèle (Qwen 7B)")
    
    print("\n" + "=" * 80)


if __name__ == "__main__":
    asyncio.run(compare_models())
