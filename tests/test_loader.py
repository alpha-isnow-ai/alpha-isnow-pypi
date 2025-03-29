import pandas as pd
import pytest
import datetime
import time
from alpha.datasets import load_daily, AssetType, list_available_months
import dotenv
import os
import warnings
import sys

# Suppress boto3 deprecation warnings
warnings.filterwarnings("ignore", category=DeprecationWarning, module="botocore.auth")

dotenv.load_dotenv()

R2_ENDPOINT_URL = os.getenv("R2_ENDPOINT_URL")
R2_ACCESS_KEY_ID = os.getenv("R2_ACCESS_KEY_ID")
R2_SECRET_ACCESS_KEY = os.getenv("R2_SECRET_ACCESS_KEY")


token = {
    "R2_ENDPOINT_URL": R2_ENDPOINT_URL,
    "R2_ACCESS_KEY_ID": R2_ACCESS_KEY_ID,
    "R2_SECRET_ACCESS_KEY": R2_SECRET_ACCESS_KEY,
}

_stock_available_months = list_available_months(
    asset_type=AssetType.Stocks, token=token
)
_stock_recent_months = _stock_available_months[-3:]

assert len(_stock_available_months) > 0


def test_list_available_months():

    for month in _stock_available_months:
        assert len(month) == 7  # YYYY.MM format
        assert month[4] == "."

    assert _stock_available_months == sorted(_stock_available_months)
    print(f"Available months: {_stock_available_months}")
    if len(_stock_available_months) > 100:
        assert "2020.01" in _stock_available_months


def test_no_missing_months_in_available_data():
    """Test to verify there are no gaps in the available months sequence."""
    if len(_stock_available_months) < 2:
        pytest.skip("Not enough months available for continuity test")

    dates = [datetime.datetime.strptime(m, "%Y.%m") for m in _stock_available_months]

    for i in range(1, len(dates)):
        prev_date = dates[i - 1]
        curr_date = dates[i]

        expected_next = prev_date.replace(day=1)
        if prev_date.month == 12:
            expected_next = expected_next.replace(year=prev_date.year + 1, month=1)
        else:
            expected_next = expected_next.replace(month=prev_date.month + 1)

        assert (
            curr_date == expected_next
        ), f"Missing month between {prev_date.strftime('%Y.%m')} and {curr_date.strftime('%Y.%m')}"

    print(f"Verified continuity of {len(_stock_available_months)} months with no gaps")


def verify_df_contains_months(df, start_month, end_month):
    """Helper function to verify DataFrame contains data for all months in range"""
    assert not df.empty, "DataFrame should not be empty"

    if not pd.api.types.is_datetime64_dtype(df["date"]):
        raise ValueError("Date column should be a datetime")

    df_months = set(df["date"].dt.strftime("%Y.%m").unique())

    # Filter available months to the requested range
    expected_months = set(
        month for month in _stock_available_months if start_month <= month <= end_month
    )

    # Check if all expected months are in the DataFrame
    missing_months = expected_months - df_months
    assert not missing_months, f"Missing data for months: {missing_months}"

    print(
        f"Verified DataFrame contains data for all {len(expected_months)} expected months in range"
    )
    return True


def test_load_daily_with_range():
    middle_index = len(_stock_available_months) // 2
    start_month = _stock_available_months[middle_index]
    end_month = _stock_available_months[middle_index + 1]

    print(f"\nTesting with month range: {start_month} to {end_month}")

    df = load_daily(
        asset_type=AssetType.Stocks,
        month_range=(start_month, end_month),
        token=token,
    )

    assert len(df) > 0
    print(f"Loaded dataframe with {len(df)} rows")

    if not df.empty:
        print(f"DataFrame columns: {df.columns.tolist()}")
        print(f"First few rows:\n{df.head(3)}")

        # Verify all months in range are present
        verify_df_contains_months(df, start_month, end_month)

        # Verify date range matches expectation
        min_date = df["date"].min()
        max_date = df["date"].max()

        expected_start_year_month = pd.to_datetime(
            f"{start_month.replace('.', '-')}-01"
        )
        expected_end_year_month = pd.to_datetime(
            f"{end_month.replace('.', '-')}-01"
        ) + pd.offsets.MonthEnd(1)

        assert (
            min_date.strftime("%Y.%m") == start_month
        ), f"Minimum date {min_date} should be in {start_month}"
        assert (
            max_date.strftime("%Y.%m") == end_month
        ), f"Maximum date {max_date} should be in {end_month}"


def test_load_daily_all_months():

    start_month = _stock_recent_months[0]
    end_month = _stock_recent_months[-1]

    print(f"\nTesting with recent months: {start_month} to {end_month}")

    df = load_daily(
        asset_type=AssetType.Stocks,
        cache=True,
        token=token,
    )

    assert len(df) > 0
    print(f"Loaded dataframe with {len(df)} rows")

    if not df.empty:
        print(f"DataFrame columns: {df.columns.tolist()}")
        print(f"First few rows:\n{df.head(3)}")

        # Verify all months in range are present
        verify_df_contains_months(df, start_month, end_month)

        # Verify and print date range info
        if "date" in df.columns:
            min_date = df["date"].min()
            max_date = df["date"].max()
            print(f"Date range: {min_date} to {max_date}")

            # Verify each requested month has data
            df["year_month"] = df["date"].dt.strftime("%Y.%m")
            months_in_df = df["year_month"].unique()
            print(f"Months with data: {sorted(months_in_df)}")

            # Count rows per month for basic distribution check
            monthly_counts = df.groupby("year_month").size()
            print(f"Rows per month: \n{monthly_counts}")

            assert len(months_in_df) >= len(
                _stock_recent_months
            ), f"Expected at least {len(_stock_recent_months)} months, got {len(months_in_df)}"


def test_load_daily_cache_performance():
    """Test that loading data with cache is significantly faster than without cache"""
    # Use last 3 months of data for testing
    start_month = _stock_recent_months[0]
    end_month = _stock_recent_months[-1]

    print(f"\nTesting cache performance with months: {start_month} to {end_month}")

    # First warm up the cache
    print("Warming up cache...")
    _ = load_daily(
        asset_type=AssetType.Stocks,
        month_range=(start_month, end_month),
        token=token,
        cache=True,
    )

    # Then load without cache
    print("Testing without cache...")
    start_time = time.time()
    df_without_cache = load_daily(
        asset_type=AssetType.Stocks,
        month_range=(start_month, end_month),
        token=token,
        cache=False,
    )
    time_without_cache = time.time() - start_time
    print(f"Time without cache: {time_without_cache:.2f} seconds")

    # Finally load with cache
    print("Testing with cache...")
    start_time = time.time()
    df_with_cache = load_daily(
        asset_type=AssetType.Stocks,
        month_range=(start_month, end_month),
        token=token,
        cache=True,
    )
    time_with_cache = time.time() - start_time
    print(f"Time with cache: {time_with_cache:.2f} seconds")

    # Verify that loading with cache is significantly faster
    # We expect at least 2x faster with cache
    assert (
        time_without_cache > time_with_cache * 2
    ), f"Loading with cache ({time_with_cache:.2f}s) should be significantly faster than without cache ({time_without_cache:.2f}s)"

    print(
        f"Cache performance test passed: {time_without_cache/time_with_cache:.1f}x faster with cache"
    )


def test_load_daily_with_sp500():
    start_month = _stock_recent_months[0]
    end_month = _stock_recent_months[-1]

    print(f"\nTesting cache performance with months: {start_month} to {end_month}")
    df = load_daily(
        asset_type=AssetType.Stocks, symbols=["AAPL", "SP500"], cache=True, token=token
    )
    assert not df.empty, "DataFrame should not be empty"
    assert len(df) > 0, "DataFrame should have rows"
    assert "date" in df.columns, "DataFrame should have a date column"
    assert "symbol" in df.columns, "DataFrame should have a symbol column"

    # Check that SPY is in the symbols
    assert "AAPL" in df["symbol"].values, "AAPL should be in the loaded symbols"

    # Check that we have more than 500 symbols (for SP500)
    unique_symbols = df["symbol"].nunique()
    assert (
        unique_symbols > 500
    ), f"Expected more than 500 unique symbols, got {unique_symbols}"
