#!/usr/bin/env python3
"""
Benchmark complet du cache sur différentes configurations matérielles.
Teste l'impact du cache avec différents modèles et génère un rapport détaillé.

Usage:
    python scripts/benchmark_cache_hardware.py

Le script génère automatiquement :
- scripts/benchmark_results.json : Résultats bruts
- scripts/BENCHMARK_REPORT.md : Rapport formaté avec comparaisons
"""

import asyncio
import json
import platform
import psutil
import sys
import time
from datetime import datetime
from pathlib import Path

# Ajoute le répertoire racine au PYTHONPATH
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.config.config import load_config
from src.utils.cache_manager import get_cached_or_fetch, load_cache
from src.utils.model_utils import call_model


def get_system_info() -> dict:
    """Récupère les informations système."""
    cpu_freq = psutil.cpu_freq()
    
    return {
        "os": platform.system(),
        "os_version": platform.release(),
        "python_version": platform.python_version(),
        "cpu_model": platform.processor() or "Unknown",
        "cpu_cores": psutil.cpu_count(logical=False),
        "cpu_threads": psutil.cpu_count(logical=True),
        "cpu_freq_max": f"{cpu_freq.max:.0f} MHz" if cpu_freq else "Unknown",
        "ram_total_gb": round(psutil.virtual_memory().total / (1024**3), 2),
        "architecture": platform.machine(),
    }


def get_cpu_brand() -> str:
    """Détecte le vendor CPU (AMD/Intel/Apple/etc)."""
    processor = platform.processor().lower()
    
    if "amd" in processor or "ryzen" in processor or "epyc" in processor:
        return "AMD"
    elif "intel" in processor or "core" in processor or "xeon" in processor:
        return "Intel"
    elif "apple" in processor or "m1" in processor or "m2" in processor or "m3" in processor:
        return "Apple Silicon"
    elif "arm" in processor or "aarch64" in platform.machine().lower():
        return "ARM"
    else:
        return "Unknown"


async def benchmark_query(question: str, use_cache: bool, config: dict) -> dict:
    """Benchmark une seule question avec métriques CPU/RAM."""
    
    # Métriques avant
    process = psutil.Process()
    cpu_before = process.cpu_percent(interval=0.1)
    mem_before = process.memory_info().rss / (1024**2)  # MB
    
    start_time = time.perf_counter()
    
    if use_cache:
        # Test avec cache
        cached_answer = await get_cached_or_fetch(question)
        if cached_answer:
            answer = cached_answer
            source = "cache"
        else:
            answer = await call_model(
                prompt=f"{question} ? Réponds en une phrase.",
                config=config,
                mode="ask"
            )
            source = "model_after_cache_miss"
    else:
        # Test sans cache (direct au modèle)
        answer = await call_model(
            prompt=f"{question} ? Réponds en une phrase.",
            config=config,
            mode="ask"
        )
        source = "model_direct"
    
    elapsed_ms = (time.perf_counter() - start_time) * 1000
    
    # Métriques après
    cpu_after = process.cpu_percent(interval=0.1)
    mem_after = process.memory_info().rss / (1024**2)  # MB
    
    return {
        "question": question,
        "answer": answer,
        "source": source,
        "time_ms": round(elapsed_ms, 2),
        "cpu_usage_percent": round((cpu_before + cpu_after) / 2, 2),
        "ram_usage_mb": round((mem_before + mem_after) / 2, 2),
        "answer_length": len(answer)
    }


async def run_benchmark():
    """Lance le benchmark complet."""
    
    config = load_config()
    system_info = get_system_info()
    cpu_brand = get_cpu_brand()
    
    print("=" * 70)
    print("🚀 BENCHMARK CACHE vs NO-CACHE")
    print("=" * 70)
    print(f"\n📊 Configuration système:")
    print(f"  • CPU: {cpu_brand} - {system_info['cpu_model']}")
    print(f"  • Cores: {system_info['cpu_cores']} physiques / {system_info['cpu_threads']} threads")
    print(f"  • Fréquence max: {system_info['cpu_freq_max']}")
    print(f"  • RAM: {system_info['ram_total_gb']} GB")
    print(f"  • OS: {system_info['os']} {system_info['os_version']}")
    print(f"  • Architecture: {system_info['architecture']}")
    
    # Questions de test (variées pour tester différents cas)
    test_questions = [
        "c'est quoi un axolotl",           # Dans le cache
        "c'est quoi Python",                # Dans le cache (redirection)
        "c'est quoi React",                 # Dans le cache (redirection)
        "c'est quoi la photosynthèse",     # Dans le cache
        "c'est quoi Minecraft",             # Dans le cache
        "c'est quoi un trou noir",          # Dans le cache
        "c'est quoi Docker",                # Possiblement pas en cache
        "c'est quoi TypeScript",            # Possiblement pas en cache
    ]
    
    # Charge le cache pour voir combien de hits on aura
    cache = load_cache()
    cache_size = len(cache) if cache else 0
    print(f"\n📦 Cache actuel: {cache_size} entrées")
    
    results = {
        "timestamp": datetime.now().isoformat(),
        "system_info": system_info,
        "cpu_brand": cpu_brand,
        "model_name": config.get("bot", {}).get("model_name", "unknown"),
        "tests": []
    }
    
    total_tests = len(test_questions) * 2  # avec et sans cache
    current_test = 0
    
    for question in test_questions:
        current_test += 1
        print(f"\n{'─' * 70}")
        print(f"[{current_test}/{total_tests}] 🔵 TEST AVEC CACHE: {question}")
        print(f"{'─' * 70}")
        
        result_with_cache = await benchmark_query(question, use_cache=True, config=config)
        
        print(f"  ⏱️  Temps: {result_with_cache['time_ms']:.2f}ms")
        print(f"  📊 CPU: {result_with_cache['cpu_usage_percent']:.1f}%")
        print(f"  🧠 RAM: {result_with_cache['ram_usage_mb']:.1f} MB")
        print(f"  📝 Source: {result_with_cache['source']}")
        print(f"  💬 Réponse: {result_with_cache['answer'][:80]}...")
        
        # Pause entre les tests
        await asyncio.sleep(1)
        
        current_test += 1
        print(f"\n{'─' * 70}")
        print(f"[{current_test}/{total_tests}] 🔴 TEST SANS CACHE: {question}")
        print(f"{'─' * 70}")
        
        result_without_cache = await benchmark_query(question, use_cache=False, config=config)
        
        print(f"  ⏱️  Temps: {result_without_cache['time_ms']:.2f}ms")
        print(f"  📊 CPU: {result_without_cache['cpu_usage_percent']:.1f}%")
        print(f"  🧠 RAM: {result_without_cache['ram_usage_mb']:.1f} MB")
        print(f"  📝 Source: {result_without_cache['source']}")
        print(f"  💬 Réponse: {result_without_cache['answer'][:80]}...")
        
        # Compare
        if result_with_cache['source'] == 'cache':
            speedup = result_without_cache['time_ms'] / result_with_cache['time_ms']
            time_saved = result_without_cache['time_ms'] - result_with_cache['time_ms']
            print(f"\n  ⚡ GAIN: {speedup:.1f}x plus rapide ({time_saved:.1f}ms économisés)")
        
        results["tests"].append({
            "question": question,
            "with_cache": result_with_cache,
            "without_cache": result_without_cache
        })
        
        # Pause entre les questions
        await asyncio.sleep(1)
    
    # Sauvegarde les résultats bruts
    output_file = Path(__file__).parent / "benchmark_results.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"\n{'=' * 70}")
    print(f"✅ Résultats bruts sauvegardés: {output_file}")
    print(f"{'=' * 70}")
    
    # Génère le rapport markdown
    generate_report(results)


def generate_report(results: dict):
    """Génère un rapport markdown avec les résultats."""
    
    report_file = Path(__file__).parent / "BENCHMARK_REPORT.md"
    
    # Calcule les statistiques
    cache_hits = sum(1 for t in results["tests"] if t["with_cache"]["source"] == "cache")
    cache_misses = len(results["tests"]) - cache_hits
    
    avg_time_with_cache = sum(t["with_cache"]["time_ms"] for t in results["tests"]) / len(results["tests"])
    avg_time_without_cache = sum(t["without_cache"]["time_ms"] for t in results["tests"]) / len(results["tests"])
    
    avg_cpu_with_cache = sum(t["with_cache"]["cpu_usage_percent"] for t in results["tests"]) / len(results["tests"])
    avg_cpu_without_cache = sum(t["without_cache"]["cpu_usage_percent"] for t in results["tests"]) / len(results["tests"])
    
    avg_ram_with_cache = sum(t["with_cache"]["ram_usage_mb"] for t in results["tests"]) / len(results["tests"])
    avg_ram_without_cache = sum(t["without_cache"]["ram_usage_mb"] for t in results["tests"]) / len(results["tests"])
    
    # Calcule le speedup moyen (seulement pour les cache hits)
    cache_hit_tests = [t for t in results["tests"] if t["with_cache"]["source"] == "cache"]
    if cache_hit_tests:
        avg_speedup = sum(
            t["without_cache"]["time_ms"] / t["with_cache"]["time_ms"] 
            for t in cache_hit_tests
        ) / len(cache_hit_tests)
    else:
        avg_speedup = 1.0
    
    with open(report_file, "w", encoding="utf-8") as f:
        f.write(f"# 🚀 Benchmark Cache vs No-Cache\n\n")
        f.write(f"**Date**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        # Informations système
        f.write(f"## 📊 Configuration Système\n\n")
        f.write(f"| Composant | Spécification |\n")
        f.write(f"|-----------|---------------|\n")
        f.write(f"| **CPU Brand** | {results['cpu_brand']} |\n")
        f.write(f"| **Processeur** | {results['system_info']['cpu_model']} |\n")
        f.write(f"| **Cores/Threads** | {results['system_info']['cpu_cores']} / {results['system_info']['cpu_threads']} |\n")
        f.write(f"| **Fréquence Max** | {results['system_info']['cpu_freq_max']} |\n")
        f.write(f"| **RAM** | {results['system_info']['ram_total_gb']} GB |\n")
        f.write(f"| **OS** | {results['system_info']['os']} {results['system_info']['os_version']} |\n")
        f.write(f"| **Architecture** | {results['system_info']['architecture']} |\n")
        f.write(f"| **Modèle IA** | {results['model_name']} |\n\n")
        
        # Résumé
        f.write(f"## 📈 Résumé des Performances\n\n")
        f.write(f"| Métrique | Avec Cache | Sans Cache | Gain |\n")
        f.write(f"|----------|------------|------------|------|\n")
        f.write(f"| **Temps moyen** | {avg_time_with_cache:.1f}ms | {avg_time_without_cache:.1f}ms | **{avg_speedup:.1f}x** |\n")
        f.write(f"| **CPU moyen** | {avg_cpu_with_cache:.1f}% | {avg_cpu_without_cache:.1f}% | {avg_cpu_without_cache - avg_cpu_with_cache:+.1f}% |\n")
        f.write(f"| **RAM moyenne** | {avg_ram_with_cache:.1f} MB | {avg_ram_without_cache:.1f} MB | {avg_ram_without_cache - avg_ram_with_cache:+.1f} MB |\n")
        f.write(f"| **Cache Hits** | {cache_hits}/{len(results['tests'])} | N/A | {cache_hits/len(results['tests'])*100:.1f}% |\n\n")
        
        # Résultats détaillés
        f.write(f"## 📋 Résultats Détaillés\n\n")
        
        for i, test in enumerate(results["tests"], 1):
            f.write(f"### {i}. {test['question']}\n\n")
            
            with_cache = test["with_cache"]
            without_cache = test["without_cache"]
            
            f.write(f"| | Avec Cache | Sans Cache |\n")
            f.write(f"|---|------------|------------|\n")
            f.write(f"| **Temps** | {with_cache['time_ms']:.2f}ms | {without_cache['time_ms']:.2f}ms |\n")
            f.write(f"| **CPU** | {with_cache['cpu_usage_percent']:.1f}% | {without_cache['cpu_usage_percent']:.1f}% |\n")
            f.write(f"| **RAM** | {with_cache['ram_usage_mb']:.1f} MB | {without_cache['ram_usage_mb']:.1f} MB |\n")
            f.write(f"| **Source** | {with_cache['source']} | {without_cache['source']} |\n")
            
            if with_cache['source'] == 'cache':
                speedup = without_cache['time_ms'] / with_cache['time_ms']
                f.write(f"| **Speedup** | **{speedup:.1f}x plus rapide** | - |\n")
            
            f.write(f"\n**Réponse (cache)**: {with_cache['answer']}\n\n")
            f.write(f"**Réponse (modèle)**: {without_cache['answer']}\n\n")
            
            f.write(f"---\n\n")
        
        # Conclusions
        f.write(f"## 💡 Conclusions\n\n")
        
        if avg_speedup > 100:
            f.write(f"- ⚡ **Speedup spectaculaire**: Le cache est **{avg_speedup:.0f}x plus rapide** que les appels modèle\n")
        elif avg_speedup > 10:
            f.write(f"- ⚡ **Speedup significatif**: Le cache est **{avg_speedup:.1f}x plus rapide** que les appels modèle\n")
        else:
            f.write(f"- ⚡ **Speedup modéré**: Le cache est **{avg_speedup:.1f}x plus rapide** que les appels modèle\n")
        
        f.write(f"- 📦 **Taux de hit**: {cache_hits/len(results['tests'])*100:.1f}% des questions trouvées dans Wikipedia\n")
        f.write(f"- 🧠 **RAM économisée**: {avg_ram_without_cache - avg_ram_with_cache:.1f} MB en moyenne\n")
        f.write(f"- 📊 **CPU économisé**: {avg_cpu_without_cache - avg_cpu_with_cache:.1f}% en moyenne\n")
        f.write(f"- ✅ **Fiabilité**: Le cache fournit des faits vérifiés depuis Wikipedia\n\n")
        
        f.write(f"### Recommandations\n\n")
        f.write(f"Pour un bot Discord/Twitch avec **{results['cpu_brand']}**:\n\n")
        
        if cache_hits / len(results["tests"]) > 0.7:
            f.write(f"- ✅ Le cache est **très efficace** sur ce type de questions\n")
        else:
            f.write(f"- ⚠️ Le cache a un taux de hit de {cache_hits/len(results['tests'])*100:.0f}%, optimiser les redirections\n")
        
        if avg_speedup > 50:
            f.write(f"- ⚡ Utiliser systématiquement le cache pour les questions factuelles\n")
        
        f.write(f"- 💾 Pré-charger le cache avec les questions fréquentes du chat\n")
        f.write(f"- 🔄 Mettre à jour le cache régulièrement (TTL: 7 jours recommandé)\n")
    
    print(f"\n{'=' * 70}")
    print(f"📄 Rapport généré: {report_file}")
    print(f"{'=' * 70}\n")
    
    # Affiche un aperçu du rapport
    print(f"📊 APERÇU DU RAPPORT:")
    print(f"  • Temps: {avg_time_with_cache:.1f}ms (cache) vs {avg_time_without_cache:.1f}ms (modèle)")
    print(f"  • Speedup: {avg_speedup:.1f}x plus rapide")
    print(f"  • Cache hits: {cache_hits}/{len(results['tests'])} ({cache_hits/len(results['tests'])*100:.1f}%)")
    print(f"  • CPU: {avg_cpu_with_cache:.1f}% (cache) vs {avg_cpu_without_cache:.1f}% (modèle)")
    print(f"  • RAM: {avg_ram_with_cache:.1f}MB (cache) vs {avg_ram_without_cache:.1f}MB (modèle)")
    print()


if __name__ == "__main__":
    print("\n🔬 Démarrage du benchmark...")
    print("⏳ Cela peut prendre 1-2 minutes...\n")
    
    asyncio.run(run_benchmark())
    
    print("\n✅ Benchmark terminé avec succès!")
    print("📁 Consultez scripts/BENCHMARK_REPORT.md pour le rapport complet\n")
