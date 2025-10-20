#!/usr/bin/env python3
"""
Script de découverte automatique : trouve le nombre max d'users concurrents
que le modèle peut gérer sans dépasser 3s de latence.

Démarre avec 5 users, incrémente de 5 jusqu'à ce qu'un message dépasse 3s.
Sauvegarde le résultat optimal dans un fichier de config.

Ce script permet de tester le nombre maximum d'utilisateurs concurrents supportés par le modèle.

Instructions :
1. Exécutez le script pour générer les résultats des tests dans `model_limits.json`.
2. Ouvrez le fichier `model_limits.json` pour consulter les résultats.
3. Mettez à jour manuellement les valeurs `max_concurrent_users_brut` et `max_concurrent_users_modere` dans le fichier `config.yaml`.
   - Cela permet d'éviter les modifications automatiques non désirées.

Modes disponibles :
- brut : Pas de cooldown, stats brutes.
- modéré : Cooldown configuré, stats propres.

"""

import sys
import asyncio
import httpx
import time
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


from config.config import load_config
from prompts.prompt_loader import load_system_prompt

async def test_concurrent_users(num_users: int, config: dict, mode: str = "modere") -> dict:
    """
    Teste un nombre donné d'users concurrents.
    mode = "brut"  : pas de cooldown, spam seuil, stats brutes
    mode = "modere": cooldown config, pas de spam, stats propres
    """
    api_url = config["bot"].get("model_endpoint", "http://127.0.0.1:1234/v1/chat/completions")
    model_name = config["bot"].get("model_name", "qwen2.5-3b-instruct")
    test_cooldown = config["bot"].get("test_cooldown", 5.0)
    system_prompt = load_system_prompt(mode="chill")
    enabled_commands = ["ask", "gameinfo"]  # Commandes spécifiques demandées

    print(f"\n🧪 Test avec {num_users} users concurrents... (mode: {mode})")

    results = {
        "num_users": num_users,
        "messages_sent": 0,
        "messages_success": 0,
        "max_latency": 0.0,
        "avg_latency": 0.0,
        "failed": False,
        "latencies": [],
        "timeouts": 0
    }

    async def send_message(user_id: int):
        messages = [
            f"Salut, je suis user {user_id}",
            f"!{enabled_commands[user_id % len(enabled_commands)]}",  # Commande utilisateur
            "Merci pour ta réponse !"
        ]
        history = []
        async with httpx.AsyncClient(timeout=30.0) as client:
            for msg in messages:
                results["messages_sent"] += 1
                api_messages = [{"role": "system", "content": system_prompt}]
                api_messages.extend(history[-4:])
                api_messages.append({"role": "user", "content": msg})
                try:
                    start = time.time()
                    response = await client.post(
                        api_url,
                        json={
                            "model": model_name,
                            "messages": api_messages,
                            "temperature": 0.7,
                            "max_tokens": 150
                        }
                    )
                    latency = time.time() - start
                    if response.status_code == 200:
                        data = response.json()
                        assistant_msg = data["choices"][0]["message"]["content"]
                        history.append({"role": "user", "content": msg})
                        history.append({"role": "assistant", "content": assistant_msg})
                        results["messages_success"] += 1
                        results["latencies"].append(latency)
                        results["max_latency"] = max(results["max_latency"], latency)
                        if latency > 3.0:
                            results["failed"] = True
                            results["timeouts"] += 1
                            if mode == "brut":
                                print(f"🛑 SEUIL DÉPASSÉ: User {user_id} = {latency:.2f}s (limite: 3.0s)")
                        # Cooldown seulement en mode modéré
                        if mode == "modere":
                            await asyncio.sleep(test_cooldown)
                    else:
                        results["failed"] = True
                except Exception:
                    results["failed"] = True

    tasks = [send_message(i) for i in range(num_users)]
    await asyncio.gather(*tasks)
    if results["latencies"]:
        results["avg_latency"] = sum(results["latencies"]) / len(results["latencies"])
    return results


async def find_max_concurrent():
    """Trouve le nombre max d'users concurrents via dichotomie."""
    
    print("=" * 100)
    print("🔍 RECHERCHE DU NOMBRE MAX D'USERS CONCURRENTS")
    print("=" * 100)
    print("Objectif : Trouver le max d'users sans dépasser 3s de latence\n")
    
    config = load_config()
    model_name = config["bot"].get("model_name", "qwen2.5-3b-instruct")
    print(f"📡 Model: {model_name}\n")
    
    # Dichotomie : commence entre 1 et 50
    min_users = 1
    max_users = 50
    optimal_users = 1
    all_results = []
    

    print("\n==================== TEST 1 : MODE BRUT (sans cooldown, spam seuil) ====================")
    min_users = 1
    max_users = 50
    optimal_users_brut = 1
    all_results_brut = []
    while min_users <= max_users:
        test_users = (min_users + max_users) // 2
        result = await test_concurrent_users(test_users, config, mode="brut")
        all_results_brut.append(result)
        print(f"  ✅ {result['messages_success']}/{result['messages_sent']} messages réussis")
        print(f"  ⏱️  Latence max: {result['max_latency']:.2f}s | Moyenne: {result['avg_latency']:.2f}s")
        if result["failed"] or result["max_latency"] > 3.0:
            print(f"  ❌ {test_users} users : TROP (latence max {result['max_latency']:.2f}s)\n")
            max_users = test_users - 1
        else:
            print(f"  ✅ {test_users} users : OK\n")
            optimal_users_brut = test_users
            min_users = test_users + 1

    print("\n==================== TEST 2 : MODE MODÉRÉ (cooldown config, pas de spam) ====================")
    min_users = 1
    max_users = 50
    optimal_users_modere = 1
    all_results_modere = []
    while min_users <= max_users:
        test_users = (min_users + max_users) // 2
        result = await test_concurrent_users(test_users, config, mode="modere")
        all_results_modere.append(result)
        print(f"  ✅ {result['messages_success']}/{result['messages_sent']} messages réussis")
        print(f"  ⏱️  Latence max: {result['max_latency']:.2f}s | Moyenne: {result['avg_latency']:.2f}s")
        if result["failed"] or result["max_latency"] > 3.0:
            print(f"  ❌ {test_users} users : TROP (latence max {result['max_latency']:.2f}s)\n")
            max_users = test_users - 1
        else:
            print(f"  ✅ {test_users} users : OK\n")
            optimal_users_modere = test_users
            min_users = test_users + 1

    print("\n==================== RÉCAPITULATIF ====================")
    print(f"\nMODE BRUT : MAX_CONCURRENT_USERS = {optimal_users_brut}")
    print(f"MODE MODÉRÉ : MAX_CONCURRENT_USERS = {optimal_users_modere}")
    print("\n🧪 Historique des tests BRUT:")
    for r in sorted(all_results_brut, key=lambda x: x["num_users"]):
        status = "✅" if not r["failed"] and r["max_latency"] <= 3.0 else "❌"
        print(f"  {status} {r['num_users']:2d} users → Max: {r['max_latency']:.2f}s | Moy: {r['avg_latency']:.2f}s | Timeouts: {r['timeouts']}")
    print("\n🧪 Historique des tests MODÉRÉ:")
    for r in sorted(all_results_modere, key=lambda x: x["num_users"]):
        status = "✅" if not r["failed"] and r["max_latency"] <= 3.0 else "❌"
        print(f"  {status} {r['num_users']:2d} users → Max: {r['max_latency']:.2f}s | Moy: {r['avg_latency']:.2f}s | Timeouts: {r['timeouts']}")

    # Sauvegarde dans un fichier JSON
    output_file = Path(__file__).parent.parent / "config" / "model_limits.json"
    output_file.parent.mkdir(exist_ok=True)
    config_data = {
        "model_name": model_name,
        "max_concurrent_users_brut": optimal_users_brut,
        "max_concurrent_users_modere": optimal_users_modere,
        "max_history_messages": 4,
        "user_rate_limit": 0.5,
        "response_timeout": 3.0,
        "tested_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        "test_results_brut": [
            {
                "num_users": r["num_users"],
                "max_latency": r["max_latency"],
                "avg_latency": r["avg_latency"],
                "success_rate": r["messages_success"] / r["messages_sent"] if r["messages_sent"] > 0 else 0,
                "timeouts": r["timeouts"]
            }
            for r in sorted(all_results_brut, key=lambda x: x["num_users"])
        ],
        "test_results_modere": [
            {
                "num_users": r["num_users"],
                "max_latency": r["max_latency"],
                "avg_latency": r["avg_latency"],
                "success_rate": r["messages_success"] / r["messages_sent"] if r["messages_sent"] > 0 else 0,
                "timeouts": r["timeouts"]
            }
            for r in sorted(all_results_modere, key=lambda x: x["num_users"])
        ]
    }
    with open(output_file, "w") as f:
        json.dump(config_data, f, indent=2)
    print(f"\n💾 Config sauvegardée dans: {output_file}")
    print("\n==================== FIN ====================")
    return optimal_users_modere


if __name__ == "__main__":
    asyncio.run(find_max_concurrent())
