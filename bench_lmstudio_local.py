import asyncio
import aiohttp
import time
import json

# --- Configuration ---
API_URL = "http://127.0.0.1:1234/v1/chat/completions"
API_KEY = "test"  # As per your request
MODEL_NAME = "gemma3" 
PROMPT = "write me a 1000 word essay on AI"
NUM_CONCURRENT_USERS = 4
MAX_TOKENS_PER_RESPONSE = 512 # Max tokens expected for the essay

# --- Request Payload ---
# This structure is typical for OpenAI-compatible chat completion endpoints
PAYLOAD = {
    "model": MODEL_NAME,
    "messages": [
        {"role": "user", "content": PROMPT}
    ],
    "max_tokens": MAX_TOKENS_PER_RESPONSE,
    "temperature": 0.7,  # You can adjust temperature if needed
    # "stream": False, # Explicitly not streaming for easier token counting from final response
}

# --- Headers ---
HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

# --- Global Stats ---
total_tokens_generated_accumulator = 0
successful_requests_accumulator = 0
failed_requests_accumulator = 0

async def send_request(session, user_id):
    """
    Sends a single asynchronous request to the LLM endpoint.
    Updates global accumulators for tokens and request status.
    """
    global total_tokens_generated_accumulator, successful_requests_accumulator, failed_requests_accumulator

    # print(f"User {user_id}: Sending request...") # Uncomment for verbose logging
    request_start_time = time.time()
    try:
        # Define a timeout for each request (e.g., 10 minutes)
        # Adjust as needed based on expected generation time for one essay
        timeout = aiohttp.ClientTimeout(total=600) # 10 minutes

        async with session.post(API_URL, json=PAYLOAD, headers=HEADERS, timeout=timeout) as response:
            response_data = await response.json() # Try to get JSON first
            request_duration = time.time() - request_start_time

            if response.status == 200:
                # Extract completion tokens from the response's 'usage' field
                completion_tokens = response_data.get("usage", {}).get("completion_tokens", 0)
                if completion_tokens > 0:
                    total_tokens_generated_accumulator += completion_tokens
                    successful_requests_accumulator += 1
                    # print(f"User {user_id}: Success ({response.status}) in {request_duration:.2f}s, Tokens: {completion_tokens}")
                else:
                    # Successful HTTP status but no completion tokens or malformed 'usage'
                    failed_requests_accumulator += 1
                    print(f"User {user_id}: Warning - HTTP 200 but no completion_tokens in {request_duration:.2f}s. Response: {response_data}")

            else:
                failed_requests_accumulator += 1
                error_text = await response.text() # Get raw text if JSON failed or for more error details
                print(f"User {user_id}: Error ({response.status}) in {request_duration:.2f}s. Response: {error_text[:200]}") # Log first 200 chars

    except aiohttp.ClientConnectorError as e:
        failed_requests_accumulator += 1
        print(f"User {user_id}: Connection Error - {e}")
    except aiohttp.ClientTimeout as e:
        failed_requests_accumulator += 1
        print(f"User {user_id}: Request Timeout Error - {e}")
    except json.JSONDecodeError as e:
        failed_requests_accumulator += 1
        # It's possible the server returned non-JSON on error
        raw_response_text = "N/A"
        if 'response' in locals() and hasattr(response, 'text'):
            try:
                raw_response_text = await response.text()
            except Exception:
                pass # Already tried
        print(f"User {user_id}: JSON Decode Error - {e}. Raw Response (first 200 chars): {raw_response_text[:200]}")
    except Exception as e:
        failed_requests_accumulator += 1
        print(f"User {user_id}: An unexpected error occurred - {type(e).__name__}: {e}")


async def run_load_test():
    """
    Manages the concurrent execution of requests and reports results.
    """
    print("Starting load test...")
    print(f"Target URL: {API_URL}")
    print(f"Model: {MODEL_NAME}")
    # print(f"Prompt: \"{PROMPT[:50]}...\"") # Removed prompt from startup message
    print("-" * 30)

    overall_start_time = time.time()

    # Create a TCPConnector with a limit.
    # The default limit is 100. For a large number of users, we might need to increase it.
    # 'limit_per_host' could also be relevant if all requests go to the exact same host/port.
    # Setting 'force_close'=True can help prevent 'too many files open' errors on some systems
    # by not keeping connections alive after each request, though it might reduce performance slightly.
    # For a load test where new connections are expected, this might be more stable.
    connector = aiohttp.TCPConnector(limit=NUM_CONCURRENT_USERS, force_close=True)


    async with aiohttp.ClientSession(connector=connector) as session:
        tasks = []
        for i in range(NUM_CONCURRENT_USERS):
            # Stagger the start of tasks slightly to avoid thundering herd on the client side
            # This is a small delay, adjust if NUM_CONCURRENT_USERS is extremely large
            # or if client-side resource exhaustion is observed at the very start.
            if i > 0 and i % 100 == 0: # Every 100 tasks, pause briefly
                   await asyncio.sleep(0.05)
            tasks.append(send_request(session, i + 1)) # User IDs 1 to N

        # await asyncio.gather will wait for all tasks to complete
        await asyncio.gather(*tasks)

    overall_end_time = time.time()
    total_time_taken = overall_end_time - overall_start_time

    # --- Results ---
    print("\n" + "=" * 30)
    print("Load Test Results")
    print("=" * 30)
    print(f"Total time taken: {total_time_taken:.2f} seconds")
    print(f"Total requests attempted: {NUM_CONCURRENT_USERS}")
    print(f"Successful requests (got completion_tokens): {successful_requests_accumulator}")
    print(f"Failed/Error requests: {failed_requests_accumulator}")
    print(f"Total completion tokens generated: {total_tokens_generated_accumulator}")

    if total_time_taken > 0 and total_tokens_generated_accumulator > 0 :
        # Calculate throughput based on all tokens generated over the total test duration
        tokens_per_second = total_tokens_generated_accumulator / total_time_taken
        print(f"Overall Throughput: {tokens_per_second:.2f} tokens/second")
    else:
        print("Overall Throughput: N/A (No successful requests with tokens or time taken was zero)")

    if successful_requests_accumulator > 0 and total_time_taken > 0:
        avg_request_latency_successful = total_time_taken / successful_requests_accumulator # This is not true latency per request, but an average over the batch
        # For true per-request latency, each `send_request` would need to return its duration.
        # This is a simplification.
        print(f"Requests per second (successful): {(successful_requests_accumulator / total_time_taken):.2f} RPS")


    if failed_requests_accumulator > 0:
        print("\nNote: Some requests failed. Check the logs above for specific error messages.")
        print("Throughput calculation considers only tokens from successful responses.")

if __name__ == "__main__":
    # For Windows, the default event loop policy might cause issues with a large number of connections.
    # asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy()) # Uncomment if on Windows and facing issues
    try:
        asyncio.run(run_load_test())
    except KeyboardInterrupt:
        print("\nLoad test interrupted by user.")
