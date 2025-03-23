# alpha-isnow

**alpha-isnow** is a Python library to load daily asset data (Stocks, ETFs, Indices, and Cryptocurrencies) from Cloudflare R2 and merge them into a single Pandas DataFrame. The library:

- Lists parquet files stored under `bucket_name/ds/<repo_id>/*.parquet` for each asset.
- Validates that the monthly slices (files named as `YYYY.MM.parquet`) are continuous with no missing months.
- Supports loading data concurrently using a configurable number of threads (default is 4).
- Uses Python's built-in logging module to log messages to the console (default level is ERROR).

## Installation

When you install **alpha-isnow** via pip, its dependencies (pandas, s3fs, boto3) will be automatically installed. To install the package:

```bash
pip install alpha-isnow
```

## Usage

```python
from alpha.datasets import load_daily, AssetType

# Load all available months of stock data
df = load_daily(
    asset_type=AssetType.Stocks,
    token={  # Optional, defaults to environment variables
        "R2_ENDPOINT_URL": "your-r2-endpoint",
        "R2_ACCESS_KEY_ID": "your-access-key",
        "R2_SECRET_ACCESS_KEY": "your-secret-key",
    }
)

# Load a specific range of months
df_range = load_daily(
    asset_type=AssetType.ETFs, 
    month_range=("2023.01", "2023.03")
)

print(f"Loaded {len(df)} records")
```

The package uses a namespace package structure, so even though the package name is **alpha-isnow**, you import it with `from alpha.datasets import ...`
