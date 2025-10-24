# 🔥 KISSBOT BENCHMARK SUITE

This folder contains comprehensive benchmarking tools for KissBot performance testing.

## 📋 What it tests

### 🧠 LLM Endpoints Performance
- **Local LLM** response times (Qwen 7B)
- **OpenAI API** response times  
- **Success rates** and error handling
- **Response quality** analysis

### 🔄 Cascade Fallback System
- **Primary → Fallback** transition speed
- **Health check** performance
- **Fallback trigger** accuracy

### 🎭 Context Switching
- **ask** vs **mention** vs **chill** performance
- **Prompt variation** impact
- **Response consistency**

### ⚡ Stress Testing
- **5 concurrent requests** handling
- **Rate limiting** effectiveness
- **System stability** under load

## 🚀 How to run

### Quick benchmark:
```bash
cd test/
chmod +x run_benchmark.sh
./run_benchmark.sh
```

### Manual benchmark:
```bash
cd test/
python3 benchmark_bot.py
```

## 📊 Results

Results are saved to:
- `benchmark_results.json` - Raw data
- `benchmark_report.txt` - Human-readable report

## 🎯 Performance Targets

### Local LLM (Qwen 7B)
- **Target**: < 3 seconds average
- **Acceptable**: < 5 seconds  
- **Critical**: > 10 seconds

### OpenAI Fallback
- **Target**: < 2 seconds average
- **Acceptable**: < 4 seconds
- **Critical**: > 8 seconds

### Cascade System
- **Target**: < 5 seconds total (local + fallback)
- **Fallback Rate**: < 20% in normal conditions

### Stress Test
- **Target**: 5 concurrent requests in < 15 seconds
- **Success Rate**: > 90%

## 🔧 Troubleshooting

### Common issues:
- **Import errors**: Make sure you're in the right directory
- **LM Studio down**: Local benchmark will fail, OpenAI should work
- **Rate limiting**: Increase delays between requests

## 📈 Optimization Tips

Based on benchmark results:
- **Slow local LLM**: Check LM Studio settings, GPU usage
- **High fallback rate**: Increase local LLM timeout
- **Context switching slow**: Review prompt complexity
- **Stress test fails**: Implement better rate limiting

---

**Happy benchmarking!** ⚡🔥