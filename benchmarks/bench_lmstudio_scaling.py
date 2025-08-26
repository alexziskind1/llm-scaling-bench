"""
Template for creating new benchmark scaling scripts.
Copy this file and modify the configuration section for your specific provider.
"""

import asyncio
import aiohttp
import time
import json
import csv
import os
import sys
from datetime import datetime

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.benchmark_config import CONCURRENT_USER_COUNTS, DEFAULT_TIMEOUT, DELAY_BETWEEN_BENCHMARKS, TIMESTAMP_FORMAT

# --- Configuration - MODIFY THESE FOR YOUR PROVIDER ---
API_URL = "http://localhost:1234/v1/chat/completions"  # Change this
API_KEY = "test"  # Change this
MODEL_NAME = "gemma3"  # Change this
PROVIDER_NAME = "lmstudio"  # Change this (used in filename)
PROMPT = "write me a 1000 word essay on AI"
MAX_TOKENS_PER_RESPONSE = 512

# --- Request Payload ---
PAYLOAD = {
    "model": MODEL_NAME,
    "messages": [
        {"role": "user", "content": PROMPT}
    ],
    "max_tokens": MAX_TOKENS_PER_RESPONSE,
    "temperature": 0.7,
}

# --- Headers ---
HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

async def send_request(session, user_id):
    """
    Sends a single asynchronous request to the LLM endpoint.
    Returns a tuple of (success, tokens_generated, duration)
    """
    request_start_time = time.time()
    try:
        timeout = aiohttp.ClientTimeout(total=DEFAULT_TIMEOUT)

        async with session.post(API_URL, json=PAYLOAD, headers=HEADERS, timeout=timeout) as response:
            response_data = await response.json()
            request_duration = time.time() - request_start_time

            if response.status == 200:
                completion_tokens = response_data.get("usage", {}).get("completion_tokens", 0)
                if completion_tokens > 0:
                    return True, completion_tokens, request_duration
                else:
                    if user_id <= 2:  # Show warning for first 2 users only
                        print(f"User {user_id}: Warning - HTTP 200 but no completion_tokens in {request_duration:.2f}s")
                    return False, 0, request_duration
            else:
                error_text = await response.text()
                if user_id <= 2:  # Show error for first 2 users only
                    print(f"User {user_id}: Error ({response.status}) in {request_duration:.2f}s. Response: {error_text[:200]}")
                return False, 0, request_duration

    except aiohttp.ClientConnectorError as e:
        if user_id <= 2:  # Show error for first 2 users only
            print(f"User {user_id}: Connection Error - {e}")
        return False, 0, time.time() - request_start_time
    except aiohttp.ClientTimeout as e:
        if user_id <= 2:  # Show error for first 2 users only
            print(f"User {user_id}: Request Timeout Error - {e}")
        return False, 0, time.time() - request_start_time
    except json.JSONDecodeError as e:
        if user_id <= 2:  # Show error for first 2 users only
            print(f"User {user_id}: JSON Decode Error - {e}")
        return False, 0, time.time() - request_start_time
    except Exception as e:
        if user_id <= 2:  # Show error for first 2 users only
            print(f"User {user_id}: Unexpected error - {type(e).__name__}: {e}")
        return False, 0, time.time() - request_start_time


async def run_benchmark(num_concurrent_users):
    """
    Runs a single benchmark with the specified number of concurrent users.
    Returns a dictionary with the results.
    """
    print(f"\nRunning benchmark with {num_concurrent_users} concurrent users...")
    
    overall_start_time = time.time()
    total_tokens_generated = 0
    successful_requests = 0
    failed_requests = 0
    
    # Create connector with appropriate limits
    connector = aiohttp.TCPConnector(limit=max(num_concurrent_users, 100), force_close=True)

    async with aiohttp.ClientSession(connector=connector) as session:
        tasks = []
        for i in range(num_concurrent_users):
            # Stagger task starts to avoid thundering herd
            if i > 0 and i % 100 == 0:
                await asyncio.sleep(0.05)
            tasks.append(send_request(session, i + 1))

        # Wait for all tasks to complete
        try:
            results = await asyncio.gather(*tasks, return_exceptions=True)
        except Exception as e:
            print(f"Error in asyncio.gather: {e}")
            results = [(False, 0, 0) for _ in range(num_concurrent_users)]

    overall_end_time = time.time()
    total_time_taken = overall_end_time - overall_start_time

    # Process results
    for result in results:
        if isinstance(result, Exception):
            # Handle exceptions returned by gather
            failed_requests += 1
        elif isinstance(result, tuple) and len(result) == 3:
            success, tokens, duration = result
            if success:
                successful_requests += 1
                total_tokens_generated += tokens
            else:
                failed_requests += 1
        else:
            # Unexpected result format
            failed_requests += 1

    # Calculate metrics
    tokens_per_second = total_tokens_generated / total_time_taken if total_time_taken > 0 else 0
    requests_per_second = successful_requests / total_time_taken if total_time_taken > 0 else 0
    success_rate = (successful_requests / num_concurrent_users) * 100 if num_concurrent_users > 0 else 0

    result = {
        'concurrent_users': num_concurrent_users,
        'total_time': total_time_taken,
        'successful_requests': successful_requests,
        'failed_requests': failed_requests,
        'total_tokens': total_tokens_generated,
        'tokens_per_second': tokens_per_second,
        'requests_per_second': requests_per_second,
        'success_rate': success_rate
    }

    print(f"Results: {successful_requests}/{num_concurrent_users} successful, "
          f"{total_tokens_generated} tokens, {tokens_per_second:.2f} tokens/sec")

    return result


def save_results_to_csv(results, filename):
    """
    Saves the benchmark results to a CSV file.
    """
    fieldnames = [
        'concurrent_users', 'total_time', 'successful_requests', 'failed_requests',
        'total_tokens', 'tokens_per_second', 'requests_per_second', 'success_rate'
    ]
    
    file_exists = os.path.exists(filename)
    
    with open(filename, 'a', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        # Write header if file is new
        if not file_exists:
            writer.writeheader()
        
        # Write all results
        for result in results:
            writer.writerow(result)


async def main():
    """
    Main function that runs benchmarks with different concurrent user counts.
    """
    print(f"Starting {PROVIDER_NAME} concurrent scaling benchmark...")
    print(f"Target URL: {API_URL}")
    print(f"Model: {MODEL_NAME}")
    print(f"Max tokens per response: {MAX_TOKENS_PER_RESPONSE}")
    print("=" * 50)

    # Use concurrent user counts from config
    concurrent_user_counts = CONCURRENT_USER_COUNTS
    
    results = []
    
    for num_users in concurrent_user_counts:
        try:
            result = await run_benchmark(num_users)
            results.append(result)
            
            # Small delay between benchmarks to let the server recover
            await asyncio.sleep(DELAY_BETWEEN_BENCHMARKS)
            
        except KeyboardInterrupt:
            print("\nBenchmark interrupted by user.")
            break
        except Exception as e:
            print(f"Error running benchmark with {num_users} users: {e}")
            # Create a failed result entry
            failed_result = {
                'concurrent_users': num_users,
                'total_time': 0,
                'successful_requests': 0,
                'failed_requests': num_users,
                'total_tokens': 0,
                'tokens_per_second': 0,
                'requests_per_second': 0,
                'success_rate': 0
            }
            results.append(failed_result)

    # Save results to CSV
    timestamp = datetime.now().strftime(TIMESTAMP_FORMAT)
    filename = os.path.join("results", f"{PROVIDER_NAME}_benchmark_results_{timestamp}.csv")
    
    save_results_to_csv(results, filename)
    
    print("\n" + "=" * 50)
    print(f"{PROVIDER_NAME.upper()} BENCHMARK COMPLETE")
    print("=" * 50)
    print(f"Results saved to: {filename}")
    print("\nSummary:")
    print("Concurrent Users | Tokens/Sec | Success Rate")
    print("-" * 40)
    
    for result in results:
        print(f"{result['concurrent_users']:14d} | {result['tokens_per_second']:9.2f} | {result['success_rate']:10.1f}%")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print(f"\n{PROVIDER_NAME} benchmark suite interrupted by user.")
