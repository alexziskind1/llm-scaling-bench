#!/usr/bin/env python3
"""
Helper script to create new benchmark files for different providers.
"""

import os
import sys
import argparse

def create_benchmark_script(provider_name, api_url, model_name, api_key="test"):
    """
    Create a new benchmark script from the template.
    """
    template_file = "benchmarks/bench_template.py"
    output_file = f"benchmarks/bench_{provider_name}_scaling.py"
    
    if not os.path.exists(template_file):
        print(f"Error: Template file {template_file} not found")
        return False
    
    if os.path.exists(output_file):
        overwrite = input(f"File {output_file} already exists. Overwrite? (y/N): ").strip().lower()
        if overwrite != 'y':
            print("Cancelled.")
            return False
    
    try:
        # Read the template
        with open(template_file, 'r') as f:
            content = f.read()
        
        # Replace placeholders
        content = content.replace('API_URL = "http://localhost:8000/v1/chat/completions"', f'API_URL = "{api_url}"')
        content = content.replace('API_KEY = "your-api-key"', f'API_KEY = "{api_key}"')
        content = content.replace('MODEL_NAME = "your-model-name"', f'MODEL_NAME = "{model_name}"')
        content = content.replace('PROVIDER_NAME = "your-provider"', f'PROVIDER_NAME = "{provider_name}"')
        
        # Write the new file
        with open(output_file, 'w') as f:
            f.write(content)
        
        print(f"✓ Created {output_file}")
        print(f"  Provider: {provider_name}")
        print(f"  API URL: {api_url}")
        print(f"  Model: {model_name}")
        print(f"  API Key: {api_key}")
        
        return True
        
    except Exception as e:
        print(f"Error creating benchmark script: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description='Create a new benchmark script from template')
    parser.add_argument('provider', help='Provider name (e.g., "lmstudio", "mlc", "openai")')
    parser.add_argument('api_url', help='API endpoint URL')
    parser.add_argument('model_name', help='Model name to test')
    parser.add_argument('--api-key', default='test', help='API key (default: "test")')
    
    args = parser.parse_args()
    
    # Validate provider name (should be simple alphanumeric)
    if not args.provider.replace('_', '').isalnum():
        print("Error: Provider name should only contain letters, numbers, and underscores")
        sys.exit(1)
    
    success = create_benchmark_script(args.provider, args.api_url, args.model_name, args.api_key)
    
    if success:
        print(f"\nNext steps:")
        print(f"1. Review and modify benchmarks/bench_{args.provider}_scaling.py if needed")
        print(f"2. Test: python benchmarks/bench_{args.provider}_scaling.py")
        print(f"3. Add to scripts/run_all_benchmarks.py if desired")
    else:
        sys.exit(1)

if __name__ == "__main__":
    main()
