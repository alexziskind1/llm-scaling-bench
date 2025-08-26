#!/usr/bin/env python3
"""
Master benchmark script that runs concurrent scaling tests across multiple providers
and generates comparison graphs.
"""

import asyncio
import subprocess
import sys
import glob
import os
from datetime import datetime
import argparse

# Available benchmark scripts
BENCHMARK_SCRIPTS = {
    'docker': 'benchmarks/bench_concurrent_scaling.py',
    'ollama': 'benchmarks/bench_ollama_scaling.py',
    'ttllm': 'benchmarks/bench_ttllm_scaling.py',
    'lmstudio': 'benchmarks/bench_lmstudio_scaling.py',
    # Add more providers here as you create scaling scripts for them
    # 'mlc': 'benchmarks/bench_mlc_scaling.py',
    # 'mlc': 'benchmarks/bench_mlc_scaling.py',
}

def run_benchmark(script_name, provider_name):
    """
    Run a specific benchmark script and return the output filename.
    """
    print(f"\n{'='*50}")
    print(f"Running {provider_name.upper()} benchmark...")
    print(f"{'='*50}")
    
    try:
        # Run the benchmark script
        result = subprocess.run([sys.executable, script_name], 
                              capture_output=False, 
                              text=True, 
                              check=True)
        
        # Find the most recent CSV file for this provider
        pattern = f"results/{provider_name}_benchmark_results_*.csv" if provider_name != 'docker' else "results/benchmark_results_*.csv"
        csv_files = glob.glob(pattern)
        
        if csv_files:
            latest_file = max(csv_files, key=os.path.getctime)
            print(f"✓ {provider_name} benchmark completed. Results: {latest_file}")
            return latest_file
        else:
            print(f"✗ No results file found for {provider_name}")
            return None
            
    except subprocess.CalledProcessError as e:
        print(f"✗ Error running {provider_name} benchmark: {e}")
        return None
    except KeyboardInterrupt:
        print(f"\n✗ {provider_name} benchmark interrupted by user")
        return None

def install_dependencies():
    """
    Install required dependencies.
    """
    print("Installing dependencies...")
    try:
        subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'], 
                      check=True)
        print("✓ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ Error installing dependencies: {e}")
        return False

def generate_comparison_plots(csv_files):
    """
    Generate comparison plots from multiple benchmark results.
    """
    if len(csv_files) < 2:
        print("Need at least 2 result files to generate comparison plots")
        return
    
    print(f"\nGenerating comparison plots from {len(csv_files)} result files...")
    try:
        # Use the plotting script with compare option
        subprocess.run([sys.executable, 'scripts/plot_results.py', '--compare'], check=True)
        print("✓ Comparison plots generated successfully")
    except subprocess.CalledProcessError as e:
        print(f"✗ Error generating comparison plots: {e}")

def main():
    parser = argparse.ArgumentParser(description='Run concurrent scaling benchmarks across multiple providers')
    parser.add_argument('--providers', nargs='+', choices=list(BENCHMARK_SCRIPTS.keys()), 
                        help='Specific providers to benchmark')
    parser.add_argument('--all', action='store_true', 
                        help='Run benchmarks for all available providers')
    parser.add_argument('--install-deps', action='store_true', 
                        help='Install dependencies before running benchmarks')
    parser.add_argument('--no-plots', action='store_true', 
                        help='Skip generating comparison plots')
    
    args = parser.parse_args()
    
    # Install dependencies if requested
    if args.install_deps:
        if not install_dependencies():
            print("Failed to install dependencies. Exiting.")
            sys.exit(1)
    
    # Determine which providers to benchmark
    if args.all:
        providers_to_run = list(BENCHMARK_SCRIPTS.keys())
    elif args.providers:
        providers_to_run = args.providers
    else:
        # Interactive selection
        print("Available providers:")
        for i, provider in enumerate(BENCHMARK_SCRIPTS.keys(), 1):
            print(f"  {i}. {provider}")
        print(f"  {len(BENCHMARK_SCRIPTS) + 1}. All providers")
        
        while True:
            try:
                choice = input(f"\nSelect providers (1-{len(BENCHMARK_SCRIPTS) + 1}) or comma-separated list: ").strip()
                
                if choice == str(len(BENCHMARK_SCRIPTS) + 1):
                    providers_to_run = list(BENCHMARK_SCRIPTS.keys())
                    break
                else:
                    indices = [int(x.strip()) - 1 for x in choice.split(',')]
                    providers_to_run = [list(BENCHMARK_SCRIPTS.keys())[i] for i in indices 
                                      if 0 <= i < len(BENCHMARK_SCRIPTS)]
                    if providers_to_run:
                        break
                    else:
                        print("Invalid selection. Please try again.")
            except (ValueError, IndexError):
                print("Invalid input. Please try again.")
    
    print(f"\nSelected providers: {', '.join(providers_to_run)}")
    
    # Confirm before starting
    if not args.all and not args.providers:
        confirm = input("\nProceed with benchmarks? This may take a while. (y/N): ").strip().lower()
        if confirm != 'y':
            print("Benchmark cancelled.")
            sys.exit(0)
    
    # Run benchmarks
    completed_files = []
    start_time = datetime.now()
    
    for provider in providers_to_run:
        if provider not in BENCHMARK_SCRIPTS:
            print(f"Warning: No benchmark script found for {provider}")
            continue
        
        script_name = BENCHMARK_SCRIPTS[provider]
        if not os.path.exists(script_name):
            print(f"Warning: Benchmark script {script_name} not found for {provider}")
            continue
        
        result_file = run_benchmark(script_name, provider)
        if result_file:
            completed_files.append(result_file)
    
    end_time = datetime.now()
    total_duration = end_time - start_time
    
    # Summary
    print(f"\n{'='*50}")
    print("BENCHMARK SUITE COMPLETE")
    print(f"{'='*50}")
    print(f"Total duration: {total_duration}")
    print(f"Completed benchmarks: {len(completed_files)}/{len(providers_to_run)}")
    
    if completed_files:
        print("\nResult files:")
        for file in completed_files:
            print(f"  - {file}")
        
        # Generate comparison plots
        if not args.no_plots and len(completed_files) > 1:
            generate_comparison_plots(completed_files)
        elif not args.no_plots:
            print("\nGenerating individual plots...")
            for file in completed_files:
                try:
                    subprocess.run([sys.executable, 'scripts/plot_results.py', '--csv', file], check=True)
                except subprocess.CalledProcessError as e:
                    print(f"Warning: Could not generate plots for {file}: {e}")
    else:
        print("\nNo benchmarks completed successfully.")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nBenchmark suite interrupted by user.")
        sys.exit(1)
