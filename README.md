# LLM Scaling Benchmark Suite

A comprehensive benchmarking tool to test how different LLM providers handle concurrent requests and measure their throughput scaling characteristics.

## 🚀 Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run a benchmark
python benchmarks/bench_ollama_scaling.py

# 3. Generate interactive plots
python scripts/plot_results.py --latest

# 4. View results in browser
open results/*.html
```

## Supported Providers

- **TensorRT-LLM (TTLLM)** - High-performance inference
- **Ollama** - Local LLM serving
- **Docker/Local servers** - Custom deployments
- **LMStudio** - Desktop LLM interface

## Project Structure

```
llm_scaling_bench/
├── config/
│   └── benchmark_config.py     # Central configuration
├── benchmarks/
│   ├── bench_ttllm_scaling.py  # TensorRT-LLM benchmark
│   ├── bench_ollama_scaling.py # Ollama benchmark
│   └── bench_*.py              # Other provider benchmarks
├── scripts/
│   ├── plot_results.py         # Generate interactive charts
│   ├── run_all_benchmarks.py   # Run multiple providers
│   └── create_benchmark.py     # Create new benchmarks
├── results/                    # CSV output and charts
└── requirements.txt
```

## Configuration

### Global Settings

Edit `config/benchmark_config.py` to change concurrent user counts for all benchmarks:

```python
# Default: 1, 2, 3, 4, 5, 6, 7, 8, 16, 32, 64, 128, 256
CONCURRENT_USER_COUNTS = list(range(1, 8)) + [2**i for i in range(3, 9)]
```

### Provider Settings

Each benchmark script has configuration at the top:

```python
API_URL = "http://localhost:11434/v1/chat/completions"
MODEL_NAME = "llama3.2:3b"
PROMPT = "Write a brief essay about artificial intelligence"
MAX_TOKENS_PER_RESPONSE = 512
```

## Running Benchmarks

### Single Provider

```bash
# TensorRT-LLM
python benchmarks/bench_ttllm_scaling.py

# Ollama
python benchmarks/bench_ollama_scaling.py

# Docker/Local
python benchmarks/bench_concurrent_scaling.py
```

### Multiple Providers

```bash
# All available providers
python scripts/run_all_benchmarks.py --all

# Specific providers
python scripts/run_all_benchmarks.py --providers ollama ttllm

# Interactive selection
python scripts/run_all_benchmarks.py
```

### Creating New Benchmarks

```bash
# Generate benchmark for new provider
python scripts/create_benchmark.py lmstudio "http://localhost:1234/v1/chat/completions" "model-name"
```

## Visualization

### Generate Charts

```bash
# Latest results
python scripts/plot_results.py --latest

# Specific file
python scripts/plot_results.py --csv results/benchmark_results_20250826_120000.csv

# Compare multiple runs
python scripts/plot_results.py --compare

# Provider comparison
python scripts/plot_results.py --provider-comparison
```

### Chart Features

- **Interactive Plotly charts** with hover tooltips and zoom
- **Four-panel dashboard**: Tokens/sec, Requests/sec, Response time, Success rate
- **Multi-provider comparisons** to evaluate performance differences
- **HTML and PNG outputs** for sharing and presentations

## Output Format

Results are saved as CSV files with these columns:

| Column | Description |
|--------|-------------|
| `concurrent_users` | Number of concurrent requests |
| `total_time` | Total time for all requests |
| `successful_requests` | Number of successful requests |
| `failed_requests` | Number of failed requests |
| `total_tokens` | Total tokens generated |
| `tokens_per_second` | Throughput metric |
| `requests_per_second` | Request rate |
| `success_rate` | Percentage of successful requests |

## Provider Setup

### TensorRT-LLM
```bash
# Update IP in bench_ttllm_scaling.py
# Default: http://192.168.1.188:8000/v1/chat/completions
```

### Ollama
```bash
ollama serve
# Test: curl http://localhost:11434/api/generate
```

### Docker/Local
```bash
# Start your server on http://localhost:8000/v1/chat/completions
```

### LMStudio
```bash
# Start local server in LMStudio
# Default: http://localhost:1234/v1/chat/completions
```

## Troubleshooting

### Common Issues

**Connection Errors**
- Verify API URL and server status
- Check concurrent connection limits
- Adjust timeout settings

**Memory Issues**
- Reduce maximum concurrent users
- Increase delays between runs
- Monitor system resources

**Inconsistent Results**
- Run multiple sessions for comparison
- Check for background processes
- Ensure stable network conditions

### Best Practices

- Start with lower concurrency for resource-limited servers
- Monitor API rate limits for cloud providers
- Run benchmarks during off-peak hours for production testing
- Save results with descriptive timestamps
