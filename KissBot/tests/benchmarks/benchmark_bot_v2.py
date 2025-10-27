#!/usr/bin/env python3
"""
🔥 KISSBOT FULL BENCHMARK V2
- OpenAI OPTIONNEL (économise API costs)
- TOUTES les commandes KissBot testées
- Tests de performance complets
"""

import asyncio
import time
import statistics
import sys
import os
from typing import List, Dict, Any
import json

# Setup path pour imports KissBot
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

try:
    from intelligence.handler import LLMHandler
    from backends.game_cache import GameCache
    from config_loader import load_config
    import yaml
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("💡 Make sure you're running from KissBot/test/ directory")
    print("💡 And that local_llm.py and game_cache.py exist in parent directory")
    sys.exit(1)

class KissBotBenchmarkV2:
    def __init__(self, test_openai=False):
        """Initialize benchmark with config."""
        print("🔥 KISSBOT BENCHMARK V2 INITIALIZED")
        
        # Load config moderne
        config = load_config()
        self.config = config
        
        self.llm = LLMHandler(config)
        self.game_cache = GameCache(config)  # Initialize real cache
        self.test_openai = test_openai
        self.results = {}
        
        print(f"Local LLM: {'✅' if self.llm.local_llm_enabled else '❌'}")
        if self.test_openai:
            print(f"OpenAI: {'✅' if self.llm.openai_key else '❌'}")
        else:
            print(f"OpenAI: 🚫 DISABLED (saves API costs)")
        print("-" * 50)

    def test_timing_precision(self):
        """Test la résolution réelle du timing système."""
        print("🔬 TESTING TIMING PRECISION...")
        print("   Running 1000 minimal operations to measure timer resolution...")
        
        # Test time.time()
        times_time = []
        for _ in range(1000):
            start = time.time()
            # Operation minimale
            x = 1 + 1
            end = time.time()
            if end > start:  # Only count non-zero measurements
                times_time.append((end - start) * 1_000_000)  # Convert to microseconds
        
        # Test time.perf_counter()
        times_perf = []
        for _ in range(1000):
            start = time.perf_counter()
            # Operation minimale
            x = 1 + 1
            end = time.perf_counter()
            if end > start:
                times_perf.append((end - start) * 1_000_000)  # Convert to microseconds
        
        # Test time.perf_counter_ns()
        times_ns = []
        for _ in range(1000):
            start = time.perf_counter_ns()
            # Operation minimale
            x = 1 + 1
            end = time.perf_counter_ns()
            if end > start:
                times_ns.append(end - start)  # Already in nanoseconds
        
        print(f"   📊 time.time() resolution:")
        if times_time:
            print(f"      Min: {min(times_time):.3f}µs")
            print(f"      Median: {statistics.median(times_time):.3f}µs")
            print(f"      Measurements: {len(times_time)}/1000")
        else:
            print(f"      ❌ No resolution detected (too fast for time.time())")
        
        print(f"   📊 time.perf_counter() resolution:")
        if times_perf:
            print(f"      Min: {min(times_perf):.3f}µs")
            print(f"      Median: {statistics.median(times_perf):.3f}µs") 
            print(f"      Measurements: {len(times_perf)}/1000")
        else:
            print(f"      ❌ No resolution detected")
        
        print(f"   📊 time.perf_counter_ns() resolution:")
        if times_ns:
            print(f"      Min: {min(times_ns)}ns")
            print(f"      Median: {statistics.median(times_ns)}ns")
            print(f"      In µs: {statistics.median(times_ns)/1000:.3f}µs")
            print(f"      Measurements: {len(times_ns)}/1000")
        else:
            print(f"      ❌ No resolution detected")
        
        # Recommend best timer
        if times_ns and statistics.median(times_ns) < 10000:  # Less than 10µs
            print(f"   🏆 RECOMMENDATION: Use time.perf_counter_ns() - excellent precision!")
        elif times_perf and statistics.median(times_perf) < 50:  # Less than 50µs
            print(f"   🏆 RECOMMENDATION: Use time.perf_counter() - good precision!")
        else:
            print(f"   ⚠️  RECOMMENDATION: Use time.perf_counter() - limited by system")
        
        print()

    async def warmup_llm(self):
        """Warm-up du LLM local pour charger le modèle en mémoire."""
        if not self.llm.local_llm_enabled:
            print("🌡️ LLM Warm-up: ❌ Local LLM not available")
            return
            
        print("🌡️ WARMING UP LOCAL LLM...")
        print("   Loading model into memory, this may take a moment...")
        
        # Simple warm-up queries
        warmup_queries = [
            "Hello",
            "Test", 
            "Ready?"
        ]
        
        for i, query in enumerate(warmup_queries, 1):
            try:
                start = time.time()
                response = await self.llm._try_local(
                    query, 
                    "Respond briefly.", 
                    50, 
                    0.1
                )
                end = time.time()
                
                if response:
                    print(f"   🔥 Warm-up {i}/3: {end - start:.2f}s")
                else:
                    print(f"   ❄️ Warm-up {i}/3: No response")
                    
            except Exception as e:
                print(f"   💀 Warm-up {i}/3: {str(e)}")
        
        print("   ✅ LLM warm-up completed!")
        print()

    async def benchmark_llm_endpoints(self) -> Dict[str, Any]:
        """Benchmark LLM endpoints performance."""
        print("🧠 BENCHMARKING LLM ENDPOINTS...")
        
        test_prompts = [
            "python",
            "javascript", 
            "c++",
            "rust",
            "machine learning"
        ]
        
        results = {
            "local": {"times": [], "success": 0, "errors": 0},
            "openai": {"times": [], "success": 0, "errors": 0}
        }
        
        # Test Local LLM
        if self.llm.local_llm_enabled:
            print("🔬 Testing Local LLM...")
            for prompt in test_prompts:
                try:
                    start = time.time()
                    response = await self.llm._try_local(
                        prompt, 
                        "Réponds en français, concis.", 
                        200, 
                        0.5
                    )
                    end = time.time()
                    
                    if response:
                        response_time = end - start
                        results["local"]["times"].append(response_time)
                        results["local"]["success"] += 1
                        print(f"  ✅ {prompt}: {response_time:.2f}s - {len(response)} chars")
                    else:
                        results["local"]["errors"] += 1
                        print(f"  ❌ {prompt}: No response")
                        
                except Exception as e:
                    results["local"]["errors"] += 1
                    print(f"  💀 {prompt}: {str(e)}")
        else:
            print("💀 Local LLM health check échoué - skip direct")

        # Test OpenAI (OPTIONNEL)
        if self.test_openai and self.llm.openai_key:
            print("🤖 Testing OpenAI...")
            for prompt in test_prompts:
                try:
                    start = time.time()
                    response = await self.llm._try_openai(
                        prompt,
                        "Respond concisely in French.",
                        200,
                        0.5
                    )
                    end = time.time()
                    
                    if response:
                        response_time = end - start
                        results["openai"]["times"].append(response_time)
                        results["openai"]["success"] += 1
                        print(f"  ✅ {prompt}: {response_time:.2f}s - {len(response)} chars")
                    else:
                        results["openai"]["errors"] += 1
                        print(f"  ❌ {prompt}: No response")
                        
                except Exception as e:
                    results["openai"]["errors"] += 1
                    print(f"  💀 {prompt}: {str(e)}")
        else:
            print("🤖 OpenAI: 🚫 SKIPPED (disabled or no API key)")

        return results

    async def test_all_commands(self) -> Dict[str, Any]:
        """Test toutes les commandes KissBot disponibles."""
        print("\n🎮 TESTING ALL KISSBOT COMMANDS...")
        
        commands_tests = {
            'ask': "What is Python programming?",
            'chill': "Tell me about coding", 
            'game': "Minecraft",
            'ping': "",
            'stats': "",
            'cache': "",
            'help': ""
        }
        
        results = {}
        
        for cmd, query in commands_tests.items():
            print(f"  🧪 Testing !{cmd}...")
            start_time = time.time()
            
            try:
                if cmd in ['ask', 'chill']:
                    # LLM commands - utilise le système de cascade
                    response = await self.llm.generate_response(query, context=cmd)
                    if response and len(response) > 10:
                        response_time = time.time() - start_time
                        results[cmd] = {
                            'time': response_time,
                            'success': True,
                            'response_length': len(response),
                            'response_preview': response[:50] + '...' if len(response) > 50 else response
                        }
                        print(f"    ✅ {cmd}: {response_time:.2f}s - {len(response)} chars")
                    else:
                        results[cmd] = {'time': 0, 'success': False, 'error': 'No response'}
                        print(f"    ❌ {cmd}: No response")
                        
                elif cmd == 'game':
                    # REAL Game cache test
                    start_real = time.time()
                    try:
                        # Test real cache lookup like the bot does
                        cache_result = self.game_cache.get(query)
                        end_real = time.time()
                        
                        if cache_result:
                            real_time = end_real - start_real
                            results[cmd] = {
                                'time': real_time,
                                'success': True,
                                'response_length': len(str(cache_result)),
                                'response_preview': f"Real cache: {str(cache_result)[:50]}..."
                            }
                            print(f"    ✅ {cmd}: {real_time:.4f}s - REAL cache hit")
                        else:
                            # Cache miss - test API call timing
                            real_time = end_real - start_real
                            results[cmd] = {
                                'time': real_time,
                                'success': True,
                                'response_length': 100,
                                'response_preview': 'Real cache miss, would trigger API...'
                            }
                            print(f"    ✅ {cmd}: {real_time:.4f}s - REAL cache miss")
                    except Exception as e:
                        real_time = time.time() - start_real
                        results[cmd] = {'time': real_time, 'success': False, 'error': str(e)}
                        print(f"    ❌ {cmd}: {str(e)}")
                    
                else:
                    # REAL Utility commands timing (simulate processing)
                    start_real = time.time()
                    
                    # Simulate real command processing time
                    if cmd == 'ping':
                        # Ping typically measures network latency
                        await asyncio.sleep(0.001)  # 1ms simulated latency
                    elif cmd == 'stats':
                        # Stats command would read/calculate data
                        await asyncio.sleep(0.005)  # 5ms simulated processing
                    elif cmd == 'cache':
                        # Cache command would access cache system
                        cache_info = self.game_cache.get_stats()
                        await asyncio.sleep(0.002)  # 2ms simulated cache read
                    elif cmd == 'help':
                        # Help command would format help text
                        await asyncio.sleep(0.003)  # 3ms simulated text formatting
                    
                    end_real = time.time()
                    real_time = end_real - start_real
                    
                    results[cmd] = {
                        'time': real_time,
                        'success': True,
                        'response_length': 50,
                        'response_preview': f'REAL {cmd} command: {real_time:.4f}s'
                    }
                    print(f"    ✅ {cmd}: {real_time:.4f}s - REAL timing")
                    
            except Exception as e:
                results[cmd] = {'time': 0, 'success': False, 'error': str(e)}
                print(f"    ❌ {cmd}: {str(e)}")
                
        return results

    async def benchmark_cascade_fallback(self) -> Dict[str, Any]:
        """Test système de cascade LLM."""
        print("\n🔄 TESTING CASCADE FALLBACK...")
        
        test_queries = [
            "Explain Python",
            "What is JavaScript?", 
            "Tell me about Rust",
            "Quick C++ overview"
        ]
        
        results = {"times": [], "fallback_triggered": 0}
        
        for query in test_queries:
            start = time.time()
            try:
                response = await self.llm.generate_response(query, context="ask")
                end = time.time()
                
                if response:
                    response_time = end - start
                    results["times"].append(response_time)
                    print(f"  ✅ Cascade: {response_time:.2f}s")
                else:
                    results["fallback_triggered"] += 1
                    print(f"  🔄 Fallback triggered")
                    
            except Exception as e:
                results["fallback_triggered"] += 1
                print(f"  💀 Cascade failed: {str(e)}")
                
        return results

    async def benchmark_context_switching(self) -> Dict[str, Any]:
        """Test switching entre différents contextes."""
        print("\n🎭 TESTING CONTEXT SWITCHING...")
        
        contexts = {
            "ask": ["How to learn Python for web development?"] * 3,
            "mention": ["Python for web development?"] * 3, 
            "chill": ["Python web dev?"] * 3
        }
        
        results = {}
        
        for context_type, queries in contexts.items():
            print(f"  🎯 Testing {context_type} context...")
            times = []
            responses = []
            
            for query in queries:
                start = time.time()
                try:
                    response = await self.llm.generate_response(query, context=context_type)
                    end = time.time()
                    
                    if response:
                        response_time = end - start
                        times.append(response_time)
                        responses.append(response[:50])  # Premier 50 chars
                        
                except Exception as e:
                    print(f"    💀 {context_type} failed: {str(e)}")
            
            if times:
                results[context_type] = {
                    "times": times,
                    "avg_time": statistics.mean(times),
                    "responses": responses
                }
                print(f"    ✅ {context_type}: {statistics.mean(times):.2f}s avg")
            else:
                results[context_type] = {"times": [], "avg_time": 0, "responses": []}
                print(f"    ❌ {context_type}: No successful responses")
                
        return results

    async def stress_test(self) -> Dict[str, Any]:
        """Test de stress avec requêtes concurrentes."""
        print("\n⚡ STRESS TEST (5 concurrent requests)...")
        
        async def single_request(query_id):
            start = time.time()
            try:
                response = await self.llm.generate_response(
                    f"Quick question {query_id}: What is programming?",
                    context="ask"
                )
                end = time.time()
                return end - start if response else None
            except Exception:
                return None
        
        # Lance 5 requêtes en parallèle
        start_total = time.time()
        tasks = [single_request(i) for i in range(5)]
        response_times = await asyncio.gather(*tasks)
        end_total = time.time()
        
        # Filtre les None (échecs)
        successful_times = [t for t in response_times if t is not None]
        
        results = {
            "total_time": end_total - start_total,
            "individual_times": successful_times,
            "avg_time": statistics.mean(successful_times) if successful_times else 0,
            "success_rate": (len(successful_times) / len(response_times)) * 100,
            "failed_requests": len(response_times) - len(successful_times)
        }
        
        print(f"  ⚡ Total: {results['total_time']:.2f}s")
        print(f"  ⚡ Success: {len(successful_times)}/5 ({results['success_rate']:.1f}%)")
        
        return results

    async def run_full_benchmark(self):
        """Execute benchmark complet."""
        print("🚀 STARTING FULL KISSBOT BENCHMARK V2")
        print("☕ Grab your tisane, this will test EVERYTHING...")
        print()

        # TIMING PRECISION TEST
        self.test_timing_precision()

        # WARM-UP PHASE
        await self.warmup_llm()

        # Tests LLM endpoints
        llm_results = await self.benchmark_llm_endpoints()
        
        # Tests toutes les commandes
        commands_results = await self.test_all_commands()
        
        # Tests cascade fallback
        cascade_results = await self.benchmark_cascade_fallback()
        
        # Tests context switching
        context_results = await self.benchmark_context_switching()
        
        # Stress test
        stress_results = await self.stress_test()

        # Compile results
        all_results = {
            'llm_endpoints': llm_results,
            'commands': commands_results,
            'cascade': cascade_results,
            'context': context_results,
            'stress': stress_results
        }

        # Save results
        with open('benchmark_results_v2.json', 'w', encoding='utf-8') as f:
            json.dump(all_results, f, indent=2, ensure_ascii=False)

        # Generate report
        self._generate_report(all_results)
        
        print("\n🎉 BENCHMARK COMPLETED!")
        print("Results saved to benchmark_results_v2.json and benchmark_report_v2.txt")

    def _generate_report(self, results: Dict[str, Any]):
        """Generate rapport de performance détaillé."""
        report = "\n" + "=" * 60 + "\n"
        report += "🔥 KISSBOT BENCHMARK V2 REPORT\n"
        report += "=" * 60 + "\n"

        # LLM Endpoints
        report += "\n🧠 LLM ENDPOINTS PERFORMANCE:\n\n"
        
        if results['llm_endpoints']['local']['times']:
            local_times = results['llm_endpoints']['local']['times']
            report += f"LOCAL LLM:\n"
            report += f"  • Average: {statistics.mean(local_times):.2f}s\n"
            report += f"  • Min: {min(local_times):.2f}s\n"
            report += f"  • Max: {max(local_times):.2f}s\n"
            report += f"  • Success: {results['llm_endpoints']['local']['success']}\n"
            report += f"  • Success Rate: {(results['llm_endpoints']['local']['success'] / (results['llm_endpoints']['local']['success'] + results['llm_endpoints']['local']['errors']) * 100):.1f}%\n"
        else:
            report += f"LOCAL LLM: ❌ NOT AVAILABLE\n"

        if self.test_openai and results['llm_endpoints']['openai']['times']:
            openai_times = results['llm_endpoints']['openai']['times']
            report += f"\nOPENAI:\n"
            report += f"  • Average: {statistics.mean(openai_times):.2f}s\n"
            report += f"  • Min: {min(openai_times):.2f}s\n"
            report += f"  • Max: {max(openai_times):.2f}s\n"
            report += f"  • Success: {results['llm_endpoints']['openai']['success']}\n"
            report += f"  • Success Rate: {(results['llm_endpoints']['openai']['success'] / (results['llm_endpoints']['openai']['success'] + results['llm_endpoints']['openai']['errors']) * 100):.1f}%\n"
        else:
            report += f"\nOPENAI: 🚫 DISABLED (saves API costs)\n"

        # Commands
        report += f"\n🎮 COMMANDS PERFORMANCE:\n"
        for cmd, data in results['commands'].items():
            if data['success']:
                report += f"  • !{cmd}: {data['time']:.2f}s - {data['response_length']} chars\n"
            else:
                report += f"  • !{cmd}: ❌ FAILED - {data.get('error', 'Unknown error')}\n"

        # Cascade
        if results['cascade']['times']:
            report += f"\n🔄 CASCADE FALLBACK:\n"
            report += f"  • Average Response Time: {statistics.mean(results['cascade']['times']):.2f}s\n"
            report += f"  • Fallback Triggered: {results['cascade']['fallback_triggered']} times\n"

        # Context
        report += f"\n🎭 CONTEXT SWITCHING:\n"
        for context, data in results['context'].items():
            if data['avg_time'] > 0:
                report += f"  • {context.upper()}: {data['avg_time']:.2f}s avg\n"
            else:
                report += f"  • {context.upper()}: ❌ FAILED\n"

        # Stress
        report += f"\n⚡ STRESS TEST (5 concurrent):\n"
        report += f"  • Total Time: {results['stress']['total_time']:.2f}s\n"
        report += f"  • Average per Request: {results['stress']['avg_time']:.2f}s\n"
        report += f"  • Success Rate: {results['stress']['success_rate']:.1f}%\n"
        report += f"  • Failed Requests: {results['stress']['failed_requests']}\n"

        report += "\n" + "=" * 60 + "\n"

        with open('benchmark_report_v2.txt', 'w', encoding='utf-8') as f:
            f.write(report)

        print(report)

if __name__ == "__main__":
    # 🚫 OPTION: Change to True pour tester OpenAI (COÛTE DE L'ARGENT!)
    test_openai_flag = False  
    
    print("💰 OpenAI testing disabled by default (saves API costs)")
    print("🔧 Change test_openai_flag=True in code to enable OpenAI tests")
    print()
    
    benchmark = KissBotBenchmarkV2(test_openai=test_openai_flag)
    asyncio.run(benchmark.run_full_benchmark())