#!/bin/bash

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Run the concurrent scaling benchmark
echo "Starting concurrent scaling benchmark..."
python benchmarks/bench_concurrent_scaling.py
