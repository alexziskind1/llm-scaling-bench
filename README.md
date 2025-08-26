# LLM Benchmark Suite

This benchmark suite allows you to test how different LLM providers handle concurrent requests and measure their throughput scaling characteristics.

## 🚀 Quick Start

**1. Install dependencies:**
```bash
pip install -r requirements.txt
# or with uv:
uv pip install -r requirements.txt
```

**2. Run a benchmark:**
```bash
# TTLLM/TensorRT-LLM (fastest)
python benchmarks/bench_ttllm_scaling.py

# Ollama
python benchmarks/bench_ollama_scaling.py

# Docker/Local server
python benchmarks/bench_concurrent_scaling.py
```

**3. Generate interactive plots:**
```bash
# Plot latest results
python scripts/plot_results.py --latest

# Compare all benchmarks
python scripts/plot_results.py --compare

# Provider performance comparison
python scripts/plot_results.py --provider-comparison
```

**4. View results:**
- Open `results/*.html` files in your browser for interactive charts
- CSV data files are saved in `results/` directory

## Project Structure

```
bench_ubuntu_box/
├── config/
│   └── benchmark_config.py          # Central configuration
├── benchmarks/
│   ├── bench_concurrent_scaling.py  # Docker/Local server benchmark
│   ├── bench_ollama_scaling.py      # Ollama benchmark
│   ├── bench_template.py            # Template for new benchmarks
│   └── bench_*.py                   # Original benchmark files
├── scripts/
│   ├── plot_results.py              # Generate graphs from results
│   ├── run_all_benchmarks.py        # Run multiple benchmarks
│   └── create_benchmark.py          # Create new benchmark scripts
├── results/                         # CSV output files
├── requirements.txt                 # Python dependencies
└── run_benchmark.sh                 # Quick start script
```

## Configuration

### Central Configuration

All benchmark scripts now use a central configuration file `config/benchmark_config.py`. To change the concurrent user counts tested across all benchmarks, edit this file:

```python
# Current default: 1, 2, 3, 4, 5, 6, 7, 8, 16, 32, 64, 128, 256
CONCURRENT_USER_COUNTS = list(range(1, 8)) + [2**i for i in range(3, 9)]
```

Alternative configurations are provided as comments in the file:
- Powers of 2 only: `[2**i for i in range(9)]`
- Linear progression: `list(range(1, 51, 5))`
- Custom values: `[1, 2, 4, 8, 12, 16, 24, 32, 48, 64, 96, 128, 192, 256]`

### Provider-Specific Configuration

Edit the configuration variables at the top of each benchmark script:

```python
API_URL = "http://localhost:12434/engines/llama.cpp/v1/chat/completions"
API_KEY = "test"
MODEL_NAME = "ai/qwen2.5"
PROMPT = "write me a 1000 word essay on AI"
MAX_TOKENS_PER_RESPONSE = 512
```

## 🔧 Provider Setup

**Before running benchmarks, ensure your LLM provider is running:**

```bash
# TTLLM/TensorRT-LLM (edit IP in bench_ttllm_scaling.py)
# Default: http://192.168.1.188:8000/v1/chat/completions

# Ollama (make sure it's running)
ollama serve
# Test: curl http://localhost:11434/api/generate

# Docker/Local server (edit URL in bench_concurrent_scaling.py)
# Default: http://localhost:8000/v1/chat/completions

# LMStudio (start local server)
# Default: http://localhost:1234/v1/chat/completions
```

## Running Benchmarks

### Single Provider

Run the concurrent scaling benchmark for Docker/Local:
```bash
python benchmarks/bench_concurrent_scaling.py
```

Run the concurrent scaling benchmark for Ollama:
```bash
python benchmarks/bench_ollama_scaling.py
```

### Multiple Providers

Run benchmarks across all available providers:
```bash
python scripts/run_all_benchmarks.py --all
```

Run benchmarks for specific providers:
```bash
python scripts/run_all_benchmarks.py --providers docker ollama
```

Interactive provider selection:
```bash
python scripts/run_all_benchmarks.py
```

All scripts will test with the concurrent user counts defined in `config/benchmark_config.py` (default: 1, 2, 3, 4, 5, 6, 7, 8, 16, 32, 64, 128, 256)

### Creating New Provider Benchmarks

Use the helper script to create benchmarks for new providers:

```bash
# Create a new benchmark for LMStudio
python scripts/create_benchmark.py lmstudio "http://localhost:1234/v1/chat/completions" "your-model-name"

# Create a new benchmark for OpenAI
python scripts/create_benchmark.py openai "https://api.openai.com/v1/chat/completions" "gpt-4" --api-key "your-api-key"
```

### Output

The benchmarks will:
1. Print progress information to the console
2. Save detailed results to timestamped CSV files in the `results/` directory:
   - Docker/Local: `results/benchmark_results_YYYYMMDD_HHMMSS.csv`
   - Ollama: `results/ollama_benchmark_results_YYYYMMDD_HHMMSS.csv`
3. Display a summary table at the end

When using `scripts/run_all_benchmarks.py`, it will also generate comparison plots automatically.

### CSV Output Format

The CSV file contains the following columns:
- `concurrent_users` - Number of concurrent requests
- `total_time` - Total time for all requests to complete
- `successful_requests` - Number of successful requests
- `failed_requests` - Number of failed requests
- `total_tokens` - Total tokens generated across all requests
- `tokens_per_second` - Throughput in tokens per second
- `requests_per_second` - Request rate
- `success_rate` - Percentage of successful requests

## 📊 Interactive Plotting with Plotly

### Plot Latest Results
```bash
python scripts/plot_results.py --latest
```

### Plot Specific File
```bash
python scripts/plot_results.py --csv results/benchmark_results_20250723_143022.csv
```

### Compare Multiple Runs
```bash
python scripts/plot_results.py --compare
```

### Provider Performance Comparison
```bash
python scripts/plot_results.py --provider-comparison
```

**Output Files:**
- `*.html` - Interactive charts (open in browser)
- `*.png` - Static images for presentations

The plotting generates **interactive charts** with:
1. **Hover tooltips** - See exact values on mouse hover
2. **Zoom & Pan** - Explore specific ranges in detail  
3. **Linear axes** - Better visualization of scaling patterns
4. **Multi-provider comparison** - Compare different LLM providers
5. **2x2 subplot layout** - Tokens/sec, Requests/sec, Response time, Success rate

**Chart Types:**
- Single benchmark analysis (4-panel dashboard)
- Multi-benchmark timeline comparison  
- Cross-provider performance analysis

## Customizing Concurrency Levels

To test different concurrency levels, modify the `CONCURRENT_USER_COUNTS` list in `config/benchmark_config.py`:

```python
# Default: 1, 2, 3, 4, 5, 6, 7, 8, 16, 32, 64, 128, 256
CONCURRENT_USER_COUNTS = list(range(1, 8)) + [2**i for i in range(3, 9)]

# Powers of 2 only: 1, 2, 4, 8, 16, 32, 64, 128, 256
CONCURRENT_USER_COUNTS = [2**i for i in range(9)]

# Custom example: specific values
CONCURRENT_USER_COUNTS = [1, 5, 10, 20, 50, 100]

# Custom example: linear progression
CONCURRENT_USER_COUNTS = list(range(1, 51, 5))  # 1, 6, 11, 16, ..., 46
```

This change will affect all benchmark scripts automatically.

## Tips for Different Providers

### For Docker/Local Servers
- Start with lower concurrency levels if your server has limited resources
- Monitor CPU and memory usage during tests
- Consider the timeout settings based on your model's response time

### For Cloud APIs
- Be aware of rate limits and adjust concurrent user counts accordingly
- Consider adding longer delays between benchmark runs
- Monitor your API usage/costs

### For Production Testing
- Run benchmarks during off-peak hours
- Start with lower concurrency and gradually increase
- Monitor server logs for errors or resource exhaustion

## Troubleshooting

### Connection Errors
- Verify the API_URL is correct and the server is running
- Check if the server supports the expected number of concurrent connections
- Adjust the timeout settings if requests are timing out

### Memory Issues
- Reduce the maximum concurrent users if you encounter memory errors
- Increase the delay between benchmark runs
- Consider running benchmarks in smaller batches

### Inconsistent Results
- Run multiple benchmark sessions and compare results

---

## 📝 Summary Workflow

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Start your LLM provider (Ollama, TTLLM, etc.)

# 3. Run benchmark
python benchmarks/bench_ttllm_scaling.py

# 4. Generate interactive plots  
python scripts/plot_results.py --latest

# 5. Open results/*.html in browser
```

**Key Files:**
- `config/benchmark_config.py` - Adjust concurrency levels
- `results/*.csv` - Raw benchmark data
- `results/*.html` - Interactive charts
- Ensure the server is in a consistent state between runs
- Consider warm-up runs before collecting data

## Example Workflow

1. Configure your API endpoint in the appropriate benchmark file
2. Run the benchmark: `python benchmarks/bench_concurrent_scaling.py`
3. Generate plots: `python scripts/plot_results.py --latest`
4. Repeat with different configurations or providers
5. Compare results: `python scripts/plot_results.py --compare`

This will give you a comprehensive view of how your LLM provider scales with concurrent load.
