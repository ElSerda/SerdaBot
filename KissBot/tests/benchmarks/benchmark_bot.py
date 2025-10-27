#!/usr/bin/env python3
"""
🔥 KISSBOT FULL BENCHMARK
Teste performance bot + LLM + cache + cascade
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
    from config_loader import load_config
    import yaml
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("💡 Make sure you're running from KissBot/test/ directory")
    print("💡 And that local_llm.py exists in parent directory")
    sys.exit(1)

class KissBotBenchmark:
    def __init__(self):
        """Initialize benchmark with config."""
        config = load_config()
        self.config = config
        
        self.llm = LLMHandler(config)
        self.results = {}
        
        print("🔥 KISSBOT BENCHMARK INITIALIZED")
        print(f"Local LLM: {'✅' if self.llm.local_llm_enabled else '❌'}")
        print(f"OpenAI: {'✅' if self.llm.openai_key else '❌'}")
        print("-" * 50)

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
                        results["local"]["times"].append(end - start)
                        results["local"]["success"] += 1
                        print(f"  ✅ {prompt}: {end-start:.2f}s - {len(response)} chars")
                    else:
                        results["local"]["errors"] += 1
                        print(f"  ❌ {prompt}: No response")
                        
                except Exception as e:
                    results["local"]["errors"] += 1
                    print(f"  💥 {prompt}: {e}")
                    
                await asyncio.sleep(0.5)  # Rate limiting
        
        # Test OpenAI
        if self.llm.openai_key:
            print("🔬 Testing OpenAI...")
            for prompt in test_prompts:
                try:
                    start = time.time()
                    response = await self.llm._try_openai(
                        prompt,
                        "Réponds en français, concis.",
                        200,
                        0.5
                    )
                    end = time.time()
                    
                    if response:
                        results["openai"]["times"].append(end - start)
                        results["openai"]["success"] += 1
                        print(f"  ✅ {prompt}: {end-start:.2f}s - {len(response)} chars")
                    else:
                        results["openai"]["errors"] += 1
                        print(f"  ❌ {prompt}: No response")
                        
                except Exception as e:
                    results["openai"]["errors"] += 1
                    print(f"  💥 {prompt}: {e}")
                    
                await asyncio.sleep(0.5)
        
        return results

    async def benchmark_cascade_fallback(self) -> Dict[str, Any]:
        """Test cascade fallback performance."""
        print("\n🔄 BENCHMARKING CASCADE FALLBACK...")
        
        test_cases = [
            {"prompt": "golang", "context": "ask"},
            {"prompt": "docker", "context": "ask"}, 
            {"prompt": "kubernetes", "context": "mention"},
            {"prompt": "react", "context": "chill"},
        ]
        
        results = {"times": [], "fallback_triggered": 0}
        
        for case in test_cases:
            try:
                start = time.time()
                response = await self.llm.generate_response(
                    case["prompt"],
                    context=case["context"],
                    user_name="benchmark_user"
                )
                end = time.time()
                
                duration = end - start
                results["times"].append(duration)
                
                if duration > 15:  # Si > 15s, probablement fallback
                    results["fallback_triggered"] += 1
                    
                print(f"  ✅ {case['prompt']} ({case['context']}): {duration:.2f}s")
                if response:
                    print(f"    📝 Response: {response[:100]}...")
                
            except Exception as e:
                print(f"  💥 {case['prompt']}: {e}")
                
            await asyncio.sleep(1)
        
        return results

    async def benchmark_context_switching(self) -> Dict[str, Any]:
        """Test different context performance."""
        print("\n🎭 BENCHMARKING CONTEXT SWITCHING...")
        
        contexts = ["ask", "mention", "chill"]
        prompt = "python web development"
        results = {}
        
        for context in contexts:
            times = []
            responses = []
            
            print(f"🔬 Testing context: {context}")
            
            for i in range(3):  # 3 tests per context
                try:
                    start = time.time()
                    response = await self.llm.generate_response(
                        prompt,
                        context=context,
                        user_name=f"test_user_{i}"
                    )
                    end = time.time()
                    
                    duration = end - start
                    times.append(duration)
                    responses.append(response[:50] if response else "No response")
                    
                    print(f"  ✅ Test {i+1}: {duration:.2f}s")
                    
                except Exception as e:
                    print(f"  💥 Test {i+1}: {e}")
                    
                await asyncio.sleep(0.5)
            
            results[context] = {
                "times": times,
                "avg_time": statistics.mean(times) if times else 0,
                "responses": responses
            }
        
        return results

    async def benchmark_stress_test(self) -> Dict[str, Any]:
        """Stress test with concurrent requests."""
        print("\n⚡ STRESS TEST - CONCURRENT REQUESTS...")
        
        async def single_request(prompt: str, context: str) -> float:
            start = time.time()
            try:
                response = await self.llm.generate_response(
                    prompt, context=context, user_name="stress_user"
                )
                return time.time() - start
            except:
                return -1  # Error
        
        # Test 5 concurrent requests
        tasks = []
        prompts = ["python", "javascript", "golang", "rust", "kotlin"]
        
        print("🔬 Launching 5 concurrent requests...")
        start_total = time.time()
        
        for i, prompt in enumerate(prompts):
            task = single_request(prompt, "ask")
            tasks.append(task)
        
        results = await asyncio.gather(*tasks)
        end_total = time.time()
        
        successful = [r for r in results if r > 0]
        failed = len([r for r in results if r < 0])
        
        return {
            "total_time": end_total - start_total,
            "individual_times": successful,
            "avg_time": statistics.mean(successful) if successful else 0,
            "success_rate": len(successful) / len(results) * 100,
            "failed_requests": failed
        }

    def generate_report(self) -> str:
        """Generate comprehensive benchmark report."""
        report = "\n" + "="*60 + "\n"
        report += "🔥 KISSBOT BENCHMARK REPORT\n"
        report += "="*60 + "\n"
        
        # LLM Endpoints
        if "llm_endpoints" in self.results:
            report += "\n🧠 LLM ENDPOINTS PERFORMANCE:\n"
            for endpoint, data in self.results["llm_endpoints"].items():
                if data["times"]:
                    avg_time = statistics.mean(data["times"])
                    min_time = min(data["times"])
                    max_time = max(data["times"])
                    
                    report += f"\n{endpoint.upper()}:\n"
                    report += f"  • Average: {avg_time:.2f}s\n"
                    report += f"  • Min: {min_time:.2f}s\n"
                    report += f"  • Max: {max_time:.2f}s\n"
                    report += f"  • Success: {data['success']}/{data['success']+data['errors']}\n"
                    report += f"  • Success Rate: {data['success']/(data['success']+data['errors'])*100:.1f}%\n"
        
        # Cascade Fallback
        if "cascade" in self.results:
            data = self.results["cascade"]
            if data["times"]:
                report += f"\n🔄 CASCADE FALLBACK:\n"
                report += f"  • Average Response Time: {statistics.mean(data['times']):.2f}s\n"
                report += f"  • Fallback Triggered: {data['fallback_triggered']} times\n"
        
        # Context Switching
        if "context" in self.results:
            report += f"\n🎭 CONTEXT SWITCHING:\n"
            for context, data in self.results["context"].items():
                report += f"  • {context.upper()}: {data['avg_time']:.2f}s avg\n"
        
        # Stress Test
        if "stress" in self.results:
            data = self.results["stress"]
            report += f"\n⚡ STRESS TEST (5 concurrent):\n"
            report += f"  • Total Time: {data['total_time']:.2f}s\n"
            report += f"  • Average per Request: {data['avg_time']:.2f}s\n"
            report += f"  • Success Rate: {data['success_rate']:.1f}%\n"
            report += f"  • Failed Requests: {data['failed_requests']}\n"
        
        report += "\n" + "="*60 + "\n"
        return report

    async def run_full_benchmark(self):
        """Run complete benchmark suite."""
        print("🚀 STARTING FULL KISSBOT BENCHMARK")
        print("☕ Grab your tisane, this will take a moment...\n")
        
        try:
            # LLM Endpoints
            self.results["llm_endpoints"] = await self.benchmark_llm_endpoints()
            
            # Cascade Fallback
            self.results["cascade"] = await self.benchmark_cascade_fallback()
            
            # Context Switching
            self.results["context"] = await self.benchmark_context_switching()
            
            # Stress Test
            self.results["stress"] = await self.benchmark_stress_test()
            
            # Generate and save report
            report = self.generate_report()
            print(report)
            
            # Save to file
            with open("benchmark_results.json", "w") as f:
                json.dump(self.results, f, indent=2)
            
            with open("benchmark_report.txt", "w") as f:
                f.write(report)
            
            print("📊 Results saved to benchmark_results.json and benchmark_report.txt")
            
        except Exception as e:
            print(f"💥 Benchmark failed: {e}")

async def main():
    """Main benchmark entry point."""
    benchmark = KissBotBenchmark()
    await benchmark.run_full_benchmark()

if __name__ == "__main__":
    asyncio.run(main())