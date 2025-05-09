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

### Function Parameters

The `load_daily` function accepts the following parameters:

- `asset_type` (AssetType): The type of asset to load (Stocks, ETFs, Indices, or Cryptocurrencies)
- `month_range` (tuple[str, str] | None): Optional tuple (start, end) with month strings in 'YYYY.MM' format. If None, loads all available months
- `symbols` (list[str] | None): Optional list of symbols to load. If None, loads all available symbols. If `sp500` is in the list, it will be removed and SP500 symbols will be added.
- `threads` (int): Number of threads to use for concurrent loading (default: 4)
- `adjust` (bool): Whether to adjust prices using the adjustment factor (default: True)
- `to_usd` (bool): Whether to convert prices to USD (default: True)
  - For Forex: Inverts exchange rates (e.g., EURUSD becomes USDEUR)
  - For Indices: Converts to USD using corresponding currency exchange rates
- `rate_to_price` (bool): For Bonds, whether to convert interest rates to prices (default: True)
- `token` (dict | None): Optional dictionary containing R2 credentials:
  ```python
  {
      "R2_ENDPOINT_URL": "your-r2-endpoint",
      "R2_ACCESS_KEY_ID": "your-access-key",
      "R2_SECRET_ACCESS_KEY": "your-secret-key"
  }
  ```
  If None, environment variables are used
- `cache` (bool): Whether to use local caching for improved performance (default: False)

The package uses a namespace package structure, so even though the package name is **alpha-isnow**, you import it with `from alpha.datasets import ...`

## Logging Configuration

The library uses Python's standard `logging` module with a default level of `ERROR`. You can configure the logging level to get more detailed information:

```python
import logging
from alpha.datasets import set_log_level

# Set log level for all modules to DEBUG
set_log_level(logging.DEBUG)

# Or set log level for a specific module
set_log_level(logging.INFO, module="loader")
```

Available log levels:
- `logging.DEBUG`: Detailed debugging information
- `logging.INFO`: Confirmation that things are working as expected
- `logging.WARNING`: Indication that something unexpected happened
- `logging.ERROR`: Error that prevented a function from working (default)
- `logging.CRITICAL`: Critical error that prevents the program from continuing

Example with logging enabled:
```python
import logging
from alpha.datasets import set_log_level, load_daily, AssetType

# Enable informational logging
set_log_level(logging.INFO)

# Now load data (with logging output)
df = load_daily(AssetType.Stocks, month_range=("2023.01", "2023.02"))
```

## Development

### Installation for Development

For development, install the package in editable mode with development dependencies:

```bash
pip install -e ".[dev]"
```

This will install:
- Runtime dependencies (pandas, s3fs, boto3, pyarrow)
- Development tools:
  - pytest: For running tests
  - black: For code formatting
  - isort: For import sorting
  - mypy: For type checking
  - flake8: For code quality checks
  - build: For building distribution packages
  - twine: For uploading to PyPI

### Building and Releasing

To build distribution packages:

```bash
# Build both wheel and source distribution
python -m build

# The packages will be created in the dist/ directory
```

To release to PyPI:

> [!NOTE]
> Before building and uploading to PyPI, don't forget to bump the version in `setup.py` and `CHANGELOG.md`.

```bash
# Clean previous builds
rm -rf dist/* && python -m build --clean && python -m twine upload dist/*

```

### Release Best Practices

When upgrading your library:

1. **Version Management**:
   - Always increment the version number in `setup.py` following semantic versioning (MAJOR.MINOR.PATCH)
   - Update `CHANGELOG.md` with details of changes in the new version
   - Consider using `0.x.y` for pre-stable releases and `1.0.0+` for stable API

2. **Build Process**:
   - Always clean previous build artifacts with `rm -rf dist/*` before building
   - Use `python -m build` to generate both wheel and source distribution
   - Verify the build artifacts in the `dist/` directory before uploading

3. **Upload Process**:
   - For important releases, test on TestPyPI first: `python -m twine upload --repository testpypi dist/*`
   - Install from TestPyPI to verify: `pip install --index-url https://test.pypi.org/simple/ alpha-isnow`
   - Only after verification, upload to PyPI: `python -m twine upload dist/*`
   - Never reuse version numbers - PyPI permanently reserves each version name

4. **Post-Release**:
   - Verify the package can be installed: `pip install --no-cache-dir alpha-isnow==x.y.z`
   - Tag the release in your version control system: `git tag -a vX.Y.Z -m "Version X.Y.Z"`
   - Push tags: `git push --tags`

Note: You only need to upload the latest version. PyPI will maintain the version history automatically.

### PyPI Configuration

Before uploading to PyPI, you need to configure your credentials. Create or edit `~/.pypirc` file:

```ini
[pypi]
username = __token__
password = your-pypi-token

[testpypi]
username = __token__
password = your-testpypi-token
```

Replace `your-pypi-token` and `your-testpypi-token` with your actual PyPI and TestPyPI tokens. You can generate these tokens from your PyPI account settings.

### Local Cache

The library implements a local caching mechanism to improve data loading performance:
- Cache location: `~/.alpha_isnow_cache/`
- Cache format: Parquet files named as `{repo_name}_{month}.parquet`
- Cache validity: 24 hours
- Performance: Loading from cache is typically 100x faster than loading from R2

### Running Tests

```bash
# Run all tests
pytest tests/

# Run specific test file
pytest tests/test_loader.py

# Run tests with verbose output
pytest -v tests/test_loader.py
```

### Code Quality

The project follows Python best practices:
- Code formatting with black
- Import sorting with isort
- Type checking with mypy
- Code quality checks with flake8

All code changes should pass these checks before being committed.
