###
# Direct test for logging functionality.
# When using pytest, logs won't show by default - use:
# pytest -v --log-cli-level=DEBUG tests/test_set_log_level.py
##########


import logging
import os
import sys
from pathlib import Path

# Add project root to Python path if needed
project_root = Path(__file__).parent.parent.absolute()
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# Now import modules
from alpha.datasets import set_log_level
from alpha.datasets.enums import AssetType
from alpha.datasets.loader import load_daily

# Configure root logger to directly output to console
# logging.basicConfig(
#     level=logging.INFO,
#     format="[%(asctime)s] %(levelname)s - %(name)s - %(message)s",
#     force=True,
# )


print("=" * 80)
print("Starting test with DEBUG level logging")
print("=" * 80)

# Load .env file if present
try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass

# Try to list available months
try:
    # Get credentials from environment
    token = {
        "R2_ENDPOINT_URL": os.getenv("R2_ENDPOINT_URL"),
        "R2_ACCESS_KEY_ID": os.getenv("R2_ACCESS_KEY_ID"),
        "R2_SECRET_ACCESS_KEY": os.getenv("R2_SECRET_ACCESS_KEY"),
    }

    print("\nAttempting to load data...")
    # Will likely fail with invalid credentials, but should log attempts
    print(
        "Loading data and you should see DEBUG, INFO, and ERROR logs (DEBUG is the lowest)"
    )
    set_log_level(logging.DEBUG, module="loader")
    data = load_daily(
        asset_type=AssetType.Stocks, month_range=("2023.01", "2023.02"), token=token
    )

    print("Loading data and you should see INFO logs ONLY")
    set_log_level(logging.INFO, module="loader")
    data = load_daily(
        asset_type=AssetType.Stocks, month_range=("2023.01", "2023.02"), token=token
    )
except Exception as e:
    print(f"\nError occurred: {e}")

print("=" * 80)
print("Test complete - you should see logging output above")
print("=" * 80)
