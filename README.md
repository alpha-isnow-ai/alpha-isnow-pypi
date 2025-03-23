# alpha-datasets

**alpha-datasets** is a Python library to load daily asset data (Stocks, ETFs, Indices, and Cryptocurrencies) from Cloudflare R2 and merge them into a single Pandas DataFrame. The library:

- Lists parquet files stored under `bucket_name/ds/<repo_id>/*.parquet` for each asset.
- Validates that the monthly slices (files named as `YYYY.MM.parquet`) are continuous with no missing months.
- Supports loading data concurrently using a configurable number of threads (default is 4).
- Uses Python’s built-in logging module to log messages to the console (default level is ERROR).

## Installation

When you install **alpha-datasets** via pip, its dependencies (pandas, s3fs, boto3) will be automatically installed. To install the package:

```bash
pip install alpha-datasets
