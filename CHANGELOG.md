# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.5] - 2025-03-30

### Fixed
- Fix the issue that the cache file is not updated when cache age is less than 24 hours 

## [0.1.4] - 2025-03-29

### Added
- Add `extend` parameter to `load_daily` function for ETFs
- Polished test cases:
	- Streamline test cases
	- Reduce complexity in test cases
	- Add test cases for symbol: `spy500` or `SPY500`


## [0.1.3] - 2025-03-29

### Added
- Add symbols parameter to `load_daily` function
- Support for SP500 symbols in `load_daily` function

## [0.1.2] - 2024-03-29

### Added
- Detailed parameter documentation for `load_daily` function
- Support for price adjustment with `adjust` parameter
- Currency conversion to USD with `to_usd` parameter
- Bond rate to price conversion with `rate_to_price` parameter
- Comprehensive documentation in README.md

### Changed
- Improved code organization and readability
- Enhanced error messages for better debugging
- Updated documentation with detailed parameter descriptions

### Fixed
- Documentation clarity for function parameters
- Improved parameter validation and error handling

## [0.1.1] - 2024-03-29

### Added
- Local caching mechanism for improved performance
  - Cache location: ~/.alpha_isnow_cache/
  - Cache validity: 24 hours
  - Significant performance improvement (100x faster)
- Development environment setup
  - Added development dependencies in setup.py
  - Comprehensive test suite with pytest
  - Code quality tools (black, isort, mypy, flake8)

### Fixed
- Data consistency issues with DataFrame sorting
- Proper separation of runtime and development dependencies
- Documentation improvements in README.md

### Dependencies
- Added pyarrow>=19.0.0 as a required dependency for parquet support

## [0.1.0] - 2024-03-21

### Added
- Initial release of alpha-isnow library
- Core functionality for loading daily asset data from Cloudflare R2
- Support for multiple asset types:
  - Stocks
  - ETFs
  - Indices
  - Cryptocurrencies
- Features:
  - Concurrent data loading with configurable thread count
  - Monthly data validation to ensure continuity
  - Flexible date range selection
  - Environment variable support for R2 credentials
  - Comprehensive logging system

### Dependencies
- pandas: For DataFrame handling
- s3fs: For accessing Cloudflare R2 via S3 interface
- boto3: For AWS S3 client functionality
- Python >= 3.12

### Technical Details
- Uses namespace package structure under `alpha.*`
- Implements efficient parquet file handling
- Provides thread-safe concurrent data loading
- Includes comprehensive test suite
- Follows Python best practices and PEP standards 