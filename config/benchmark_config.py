"""
Central configuration file for benchmark suite.
This file contains shared settings that can be used across all benchmark scripts.
"""

# Concurrent user counts to test
# Current setup: 1, 2, 3, 4, 5, 6, 7, 8, 16, 32, 64, 128, 256
# CONCURRENT_USER_COUNTS = list(range(1, 8)) + [2**i for i in range(3, 9)]

# Alternative configurations (uncomment to use):

# Powers of 2 only: 1, 2, 4, 8, 16, 32, 64, 128, 256
# CONCURRENT_USER_COUNTS = [2**i for i in range(9)]

# Linear progression: 1, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50
# CONCURRENT_USER_COUNTS = list(range(1, 51, 5))

# Custom specific values
# CONCURRENT_USER_COUNTS = [1, 2, 4, 8, 12, 16, 24, 32, 48, 64, 96, 128, 192, 256]

# Smaller range for quick testing
CONCURRENT_USER_COUNTS = [230]

# Common benchmark settings
DEFAULT_PROMPT = "write me a 1000 word essay on AI"
DEFAULT_MAX_TOKENS = 512
DEFAULT_TEMPERATURE = 0.7
DEFAULT_TIMEOUT = 600  # 10 minutes

# Benchmark timing settings
DELAY_BETWEEN_BENCHMARKS = 2  # seconds
STAGGER_DELAY_INTERVAL = 100  # stagger every N tasks
STAGGER_DELAY_DURATION = 0.05  # seconds

# Output settings
TIMESTAMP_FORMAT = "%Y%m%d_%H%M%S"
