import logging
import re
import pandas as pd
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from .enums import AssetType
from .storage import list_parquet_files, load_parquet_file

# Set up logger
logger = logging.getLogger(__name__)

if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter("[%(asctime)s] %(levelname)s - %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)
logger.setLevel(logging.ERROR)  # Default log level is ERROR


def _parse_month(month_str: str) -> datetime:
    """Parse a month string formatted as 'YYYY.MM' into a datetime object."""
    return datetime.strptime(month_str, "%Y.%m")


def _validate_contiguity(months: list[str]):
    """
    Check if the list of month strings is contiguous.
    The list must contain consecutive months without any missing month.
    Raises ValueError if there is a gap.
    """
    if not months:
        raise ValueError("No month files found.")
    parsed = sorted([_parse_month(m) for m in months])
    current = parsed[0]
    for dt in parsed[1:]:
        # Compute the expected next month
        year = current.year + (current.month // 12)
        month = current.month % 12 + 1
        expected = current.replace(year=year, month=month)
        if dt.year != expected.year or dt.month != expected.month:
            raise ValueError(
                f"Missing month: expected {expected.strftime('%Y.%m')} after {current.strftime('%Y.%m')}, "
                f"but got {dt.strftime('%Y.%m')}"
            )
        current = dt


def load_daily(
    asset_type: AssetType,
    month_range: tuple[str, str] | None = None,
    threads: int = 4,
    token: dict | None = None,
) -> pd.DataFrame:
    """
    Load the daily data for the specified asset type and merge into one DataFrame.

    Parameters:
        asset_type: An AssetType enum value (Stocks, ETFs, Indices, or Cryptocurrencies).
        bucket_name: The R2 bucket name (default is "alpha").
        month_range: Optional tuple (start, end) with month strings in 'YYYY.MM' format.
                     If None, load all available months and validate contiguity.
        threads: Number of threads to use for concurrent loading (default is 4).
        token: A dictionary containing R2 credentials with keys: R2_ENDPOINT_URL, R2_ACCESS_KEY_ID, R2_SECRET_ACCESS_KEY.
               If None, environment variables are used.

    Returns:
        A merged pandas DataFrame containing the data from all loaded parquet files.
    """
    # Get repo_id from asset_type and compute repo_name (last part of the repo_id in lowercase)
    repo_id = asset_type.value
    repo_name = repo_id.split("/")[-1].lower()
    logger.debug(f"Loading data: repo_id={repo_id}, repo_name={repo_name}")

    # List all parquet files under ds/<repo_name>/ on R2
    file_dict = list_parquet_files(repo_name, token)
    if not file_dict:
        raise ValueError(f"No parquet files found for repo {repo_name}.")
    available_months = sorted(file_dict.keys())
    logger.debug(f"Available months: {available_months}")

    # Filter by month_range if provided; otherwise, validate the entire range for contiguity
    if month_range:
        start, end = month_range
        filtered_months = [m for m in available_months if start <= m <= end]
        if not filtered_months:
            raise ValueError("No parquet files found within the specified month range.")
        _validate_contiguity(filtered_months)
        selected_months = filtered_months
    else:
        _validate_contiguity(available_months)
        selected_months = available_months

    logger.info(f"Selected months: {selected_months}")

    # Concurrently load each month's parquet file using a thread pool
    dfs = []
    with ThreadPoolExecutor(max_workers=threads) as executor:
        future_to_month = {
            executor.submit(load_parquet_file, repo_name, month, token): month
            for month in selected_months
        }
        for future in as_completed(future_to_month):
            month = future_to_month[future]
            try:
                df = future.result()
                logger.debug(
                    f"Successfully loaded month {month} with {len(df)} records"
                )
                dfs.append(df)
            except Exception as exc:
                logger.error(f"Error loading month {month}: {exc}")
                raise exc

    if not dfs:
        raise ValueError("No data loaded.")
    combined_df = pd.concat(dfs, ignore_index=True)
    logger.info(f"Merged DataFrame record count: {len(combined_df)}")
    return combined_df


def list_available_months(
    asset_type: AssetType,
    token: dict | None = None,
) -> list[str]:
    """
    List all available month strings (in 'YYYY.MM' format) for the specified asset type.

    Parameters:
        asset_type: An AssetType enum value (Stocks, ETFs, Indices, or Cryptocurrencies).
        bucket_name: The R2 bucket name (default is "alpha").
        token: A dictionary containing R2 credentials with keys: R2_ENDPOINT_URL, R2_ACCESS_KEY_ID, R2_SECRET_ACCESS_KEY.
               If None, environment variables are used.

    Returns:
        A sorted list of month strings (e.g., ['2023.01', '2023.02']).
    """
    repo_id = asset_type.value
    repo_name = repo_id.split("/")[-1].lower()
    file_dict = list_parquet_files(repo_name, token)
    available_months = sorted(file_dict.keys())
    return available_months
