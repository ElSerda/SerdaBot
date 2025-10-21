#!/usr/bin/env python3
"""
Benchmark du ConversationManager avec paramètres depuis config.yaml

Ce script teste les performances du système de contexte conversationnel
en utilisant les paramètres définis dans rate_limiting:
  - max_concurrent_users: Nombre d'utilisateurs testés
  - max_messages_per_user: Taille max de l'historique
  - max_idle_time: TTL des conversations

Usage:
  python3 scripts/benchmark_conversation_manager.py [options]

Options:
  --messages N      Nombre de messages par user (default: 20)
  --sequential      Mode séquentiel au lieu de parallèle
  --export FILE     Exporter résultats en JSON
  --quiet           Réduire l'output (summary seulement)
"""

import argparse
import asyncio
import json
import re
import sys
import time
from pathlib import Path
from typing import Any, Dict, List

import yaml

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.core.commands.chill_command import handle_chill_command
from src.utils.conversation_manager import ConversationManager


class MockAuthor:
    """Mock Twitch author."""
    def __init__(self, name: str):
        self.name = name


class MockChannel:
    """Mock Twitch channel."""
    def __init__(self):
        self.messages_sent: List[str] = []
    
    async def send(self, msg: str):
        self.messages_sent.append(msg)


class MockMessage:
    """Mock Twitch message."""
    def __init__(self, user: str, content: str):
        self.author = MockAuthor(user)
        self.content = content
        self.channel = MockChannel()


# Test messages (varied topics for realistic conversation)
TEST_MESSAGES = [
    "Salut !",
    "tu connais Python ?",
    "et les dictionnaires ?",
    "et les listes ?",
    "C'est quoi un tuple ?",
    "Parle-moi des sets",
    "Et les classes ?",
    "C'est quoi une fonction lambda ?",
    "Explique les décorateurs",
    "C'est quoi async/await ?",
    "Parle-moi de Django",
    "Tu connais FastAPI ?",
    "C'est quoi Flask ?",
    "Explique les tests unitaires",
    "C'est quoi pytest ?",
    "Parle-moi de Git",
    "C'est quoi Docker ?",
    "Tu connais Kubernetes ?",
    "Explique CI/CD",
    "C'est quoi DevOps ?",
    "Comment fonctionne REST ?",
    "Qu'est-ce que GraphQL ?",
    "Explique WebSocket",
    "C'est quoi Redis ?",
    "Parle-moi de PostgreSQL",
]


async def run_user_conversation(
    user_id: str,
    messages: List[str],
    conv_mgr: ConversationManager,
    config: dict,
    quiet: bool = False
) -> Dict[str, Any]:
    """Run a conversation for one user and collect metrics."""
    
    latencies = []
    easter_eggs = []  # Track Chinese character easter eggs
    chinese_pattern = r'([\u4e00-\u9fff]+)'
    now = time.time()
    
    for i, content in enumerate(messages, 1):
        msg = MockMessage(user_id, f"serda_bot {content}")
        
        start = time.time()
        await handle_chill_command(
            message=msg,
            config=config,
            now=now,
            conversation_manager=conv_mgr,
            llm_available=True,
            bot=None
        )
        duration = time.time() - start
        latencies.append(duration * 1000)  # Convert to ms
        
        # Check for Chinese characters in response
        if msg.channel.messages_sent:
            response = msg.channel.messages_sent[-1]
            chinese_matches = re.findall(chinese_pattern, response)
            if chinese_matches:
                easter_eggs.append({
                    "message_num": i,
                    "chinese_words": chinese_matches,
                    "response_preview": response[:80] if len(response) > 80 else response
                })
    
    # Get final history size
    state = conv_mgr.get(user_id)
    history_size = len(state.messages)
    
    return {
        "user": user_id,
        "messages_sent": len(messages),
        "history_size": history_size,
        "latencies": latencies,
        "avg_latency": sum(latencies) / len(latencies) if latencies else 0,
        "min_latency": min(latencies) if latencies else 0,
        "max_latency": max(latencies) if latencies else 0,
        "easter_eggs": easter_eggs,
    }


async def run_parallel_benchmark(
    users: List[str],
    messages_per_user: int,
    conv_mgr: ConversationManager,
    config: dict,
    quiet: bool
) -> List[Dict[str, Any]]:
    """Run benchmark with all users in parallel."""
    
    messages = TEST_MESSAGES[:messages_per_user]
    if len(messages) < messages_per_user:
        # Repeat messages if needed
        messages = (messages * ((messages_per_user // len(messages)) + 1))[:messages_per_user]
    
    tasks = [
        run_user_conversation(user, messages, conv_mgr, config, quiet)
        for user in users
    ]
    
    return await asyncio.gather(*tasks)


async def run_sequential_benchmark(
    users: List[str],
    messages_per_user: int,
    conv_mgr: ConversationManager,
    config: dict,
    quiet: bool
) -> List[Dict[str, Any]]:
    """Run benchmark with users one after another."""
    
    messages = TEST_MESSAGES[:messages_per_user]
    if len(messages) < messages_per_user:
        messages = (messages * ((messages_per_user // len(messages)) + 1))[:messages_per_user]
    
    results = []
    for user in users:
        result = await run_user_conversation(user, messages, conv_mgr, config, quiet)
        results.append(result)
    
    return results


def calculate_metrics(results: List[Dict[str, Any]], total_time: float, config_params: dict) -> Dict[str, Any]:
    """Calculate aggregate metrics from all results."""
    
    all_latencies = []
    all_easter_eggs = []
    for r in results:
        all_latencies.extend(r["latencies"])
        all_easter_eggs.extend(r.get("easter_eggs", []))
    
    all_latencies.sort()
    total_messages = sum(r["messages_sent"] for r in results)
    
    return {
        "config": config_params,
        "performance": {
            "total_time": round(total_time, 2),
            "total_messages": total_messages,
            "throughput": round(total_messages / total_time, 2) if total_time > 0 else 0,
            "avg_latency": round(sum(all_latencies) / len(all_latencies), 2),
            "min_latency": round(min(all_latencies), 2),
            "max_latency": round(max(all_latencies), 2),
            "p50_latency": round(all_latencies[len(all_latencies) // 2], 2),
            "p95_latency": round(all_latencies[int(len(all_latencies) * 0.95)], 2),
        },
        "memory": {
            "total_messages_stored": sum(r["history_size"] for r in results),
            "avg_history_size": round(sum(r["history_size"] for r in results) / len(results), 1),
            "max_history_size": max(r["history_size"] for r in results),
        },
        "easter_eggs": {
            "total_count": len(all_easter_eggs),
            "occurrence_rate": round((len(all_easter_eggs) / total_messages * 100), 2) if total_messages > 0 else 0,
            "details": all_easter_eggs,
        },
        "per_user": results,
    }


def print_report(metrics: Dict[str, Any], quiet: bool = False):
    """Print formatted benchmark report."""
    
    print("\n" + "=" * 70)
    print("🧪 BENCHMARK: ConversationManager")
    print("=" * 70)
    
    config = metrics["config"]
    perf = metrics["performance"]
    mem = metrics["memory"]
    
    print("\n📋 Configuration:")
    print(f"   Max users:          {config['max_users']}")
    print(f"   Max messages/user:  {config['max_messages']}")
    print(f"   Messages/user:      {config['messages_per_user']}")
    print(f"   TTL:                {config['ttl']}s")
    print(f"   Mode:               {config['mode']}")
    
    print("\n⏱️  Performance:")
    print(f"   Total time:         {perf['total_time']}s")
    print(f"   Total messages:     {perf['total_messages']}")
    print(f"   Throughput:         {perf['throughput']} msg/s")
    print(f"   Avg latency:        {perf['avg_latency']}ms")
    print(f"   Min latency:        {perf['min_latency']}ms")
    print(f"   Max latency:        {perf['max_latency']}ms")
    print(f"   P50 latency:        {perf['p50_latency']}ms")
    print(f"   P95 latency:        {perf['p95_latency']}ms")
    
    print("\n💾 Mémoire:")
    print(f"   Messages stockés:   {mem['total_messages_stored']}")
    print(f"   Historique moyen:   {mem['avg_history_size']} messages/user")
    print(f"   Historique max:     {mem['max_history_size']} messages")
    
    # Validation
    print("\n✅ Validation:")
    max_expected = config['max_messages']
    if mem['max_history_size'] <= max_expected:
        print(f"   • Historique limité à {mem['max_history_size']} ≤ {max_expected} ✓")
    else:
        print(f"   • ❌ Historique dépasse la limite: {mem['max_history_size']} > {max_expected}")
    
    # Easter eggs stats
    easter_eggs = metrics.get("easter_eggs", {})
    if easter_eggs.get("total_count", 0) > 0:
        print("\n🎓 Easter Eggs (Caractères Chinois):")
        print(f"   Total détectés:     {easter_eggs['total_count']}")
        print(f"   Taux d'occurrence:  {easter_eggs['occurrence_rate']}%")
        
        if not quiet and easter_eggs.get("details"):
            print("\n   🀄 Exemples d'artefacts détectés:")
            for egg in easter_eggs["details"][:3]:  # Show first 3
                chinese_words = ', '.join(egg['chinese_words'])
                print(f"      • Message #{egg['message_num']}: {chinese_words}")
                print(f"        '{egg['response_preview']}...'")
            
            if len(easter_eggs["details"]) > 3:
                print(f"      ... et {len(easter_eggs['details']) - 3} autres artefacts")
    else:
        print("\n🎓 Easter Eggs: Aucun artefact détecté dans ce test")
    
    if not quiet:
        print("\n📊 Détails par utilisateur:")
        for user_data in metrics["per_user"][:5]:  # Show first 5 users
            print(f"   • {user_data['user']}: "
                  f"{user_data['messages_sent']} msg, "
                  f"historique={user_data['history_size']}, "
                  f"latence={user_data['avg_latency']:.0f}ms")
        
        if len(metrics["per_user"]) > 5:
            print(f"   ... et {len(metrics['per_user']) - 5} autres utilisateurs")
    
    print("\n" + "=" * 70)


async def main():
    """Main benchmark function."""
    
    try:
        parser = argparse.ArgumentParser(description="Benchmark ConversationManager")
        parser.add_argument("--messages", type=int, default=20, help="Messages par user")
        parser.add_argument("--sequential", action="store_true", help="Mode séquentiel")
        parser.add_argument("--export", type=str, help="Fichier export JSON")
        parser.add_argument("--quiet", action="store_true", help="Réduire l'output")
        args = parser.parse_args()
        
        # Load config
        config_path = Path(__file__).parent.parent / "src" / "config" / "config.yaml"
        with open(config_path, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f)
        
        # Disable debug to reduce noise
        config["bot"]["debug"] = False
    except Exception as e:
        print(f"\n❌ ERREUR lors de l'initialisation: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # Get rate limiting params from config
    rate_limiting = config.get("rate_limiting", {})
    max_users = rate_limiting.get("max_concurrent_users", 4)
    max_messages = rate_limiting.get("max_messages_per_user", 12)
    ttl = rate_limiting.get("max_idle_time", 3600)
    
    # Create users
    users = [f"user{i}" for i in range(max_users)]
    
    # Initialize ConversationManager
    conv_mgr = ConversationManager(ttl_seconds=ttl, max_messages=max_messages)
    
    try:
        if not args.quiet:
            print(f"\n🚀 Lancement benchmark...")
            print(f"   • {max_users} utilisateurs")
            print(f"   • {args.messages} messages/user")
            print(f"   • Mode: {'séquentiel' if args.sequential else 'parallèle'}")
        
        # Run benchmark
        start_time = time.time()
        
        if args.sequential:
            results = await run_sequential_benchmark(users, args.messages, conv_mgr, config, args.quiet)
        else:
            results = await run_parallel_benchmark(users, args.messages, conv_mgr, config, args.quiet)
        
        total_time = time.time() - start_time
        
        # Calculate metrics
        config_params = {
            "max_users": max_users,
            "max_messages": max_messages,
            "messages_per_user": args.messages,
            "ttl": ttl,
            "mode": "sequential" if args.sequential else "parallel",
        }
        
        metrics = calculate_metrics(results, total_time, config_params)
        
        # Print report
        print_report(metrics, args.quiet)
        
        # Export if requested
        if args.export:
            with open(args.export, "w", encoding="utf-8") as f:
                json.dump(metrics, f, indent=2)
            print(f"\n💾 Résultats exportés: {args.export}")
        
        print()
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Benchmark interrompu par l'utilisateur")
    except Exception as e:
        print(f"\n❌ ERREUR durant le benchmark: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
