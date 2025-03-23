import pandas as pd
import pytest
import datetime
from alpha.datasets import load_daily, AssetType, list_available_months
import alpha.datasets.storage as storage
import dotenv
import os
import warnings

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


def get_available_months():
    """Helper function to get available months for tests"""
    return list_available_months(AssetType.Stocks)


def test_list_available_months():
    months = get_available_months()
    print(f"\nAvailable months: {months}")

    assert len(months) > 0

    for month in months:
        assert len(month) == 7  # YYYY.MM format
        assert month[4] == "."

    assert months == sorted(months)

    if len(months) > 100:
        assert "2020.01" in months


def verify_df_contains_months(df, start_month, end_month):
    """Helper function to verify DataFrame contains data for all months in range"""
    assert not df.empty, "DataFrame should not be empty"

    # Convert date column to datetime if it's not already
    if not pd.api.types.is_datetime64_dtype(df["date"]):
        df["date"] = pd.to_datetime(df["date"])

    # Get the unique year-month combinations in the DataFrame
    df_months = set(df["date"].dt.strftime("%Y.%m").unique())

    # Generate all months in the requested range
    all_months = []
    start_year, start_month_num = int(start_month.split(".")[0]), int(
        start_month.split(".")[1]
    )
    end_year, end_month_num = int(end_month.split(".")[0]), int(end_month.split(".")[1])

    current_year, current_month = start_year, start_month_num
    while (current_year < end_year) or (
        current_year == end_year and current_month <= end_month_num
    ):
        all_months.append(f"{current_year}.{current_month:02d}")
        current_month += 1
        if current_month > 12:
            current_month = 1
            current_year += 1

    # Intersect with available months to get expected months
    available_months = set(get_available_months())
    expected_months = set(all_months) & available_months

    # Check if all expected months are in the DataFrame
    missing_months = expected_months - df_months
    assert not missing_months, f"Missing data for months: {missing_months}"

    print(
        f"Verified DataFrame contains data for all {len(expected_months)} expected months in range"
    )
    return True


def test_load_daily_with_range():
    available_months = get_available_months()

    if len(available_months) >= 2:
        middle_index = len(available_months) // 2
        start_month = available_months[middle_index]
        end_month = available_months[middle_index + 1]

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
    else:
        pytest.skip("Not enough months available for range test")


def test_load_daily_all_months():
    available_months = get_available_months()

    recent_months = (
        available_months[-3:] if len(available_months) >= 3 else available_months
    )
    start_month = recent_months[0]
    end_month = recent_months[-1]

    print(f"\nTesting with recent months: {start_month} to {end_month}")

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
                recent_months
            ), f"Expected at least {len(recent_months)} months, got {len(months_in_df)}"
