#!/bin/bash
"""
🚀 KISSBOT BENCHMARK RUNNER
Run this script to benchmark your bot performance
"""

echo "🔥 KISSBOT FULL BENCHMARK"
echo "=========================="
echo ""
echo "☕ Grab your tisane, this will take a moment..."
echo ""

cd "$(dirname "$0")"

echo "📋 Tests to run:"
echo "  🧠 LLM Endpoints Performance"
echo "  🔄 Cascade Fallback System"  
echo "  🎭 Context Switching Speed"
echo "  ⚡ Stress Test (5 concurrent)"
echo ""

echo "🏃‍♂️ Starting benchmark..."
python3 benchmark_bot.py

echo ""
echo "✅ Benchmark completed!"
echo "📊 Check benchmark_report.txt for full results"