import pandas as pd
import pytest
from alpha_datasets import load_daily, AssetType


# Dummy functions to simulate storage module file listing and loading
def dummy_list_parquet_files(bucket_name, repo_name, token=None):
    return {
        "2023.01": f"{bucket_name}/ds/{repo_name}/2023.01.parquet",
        "2023.02": f"{bucket_name}/ds/{repo_name}/2023.02.parquet",
        "2023.03": f"{bucket_name}/ds/{repo_name}/2023.03.parquet",
    }


def dummy_load_parquet_file(bucket_name, repo_name, month, token=None):
    # Simulate returning a simple DataFrame; one row per month
    data = {"date": [f"2023-{month[-2:]}-01"], "value": [int(month[-2:])]}
    return pd.DataFrame(data)


# Use monkeypatch to replace the functions in the storage module with our dummy functions.
import alpha_datasets.storage as storage


@pytest.fixture(autouse=True)
def patch_storage(monkeypatch):
    monkeypatch.setattr(storage, "list_parquet_files", dummy_list_parquet_files)
    monkeypatch.setattr(storage, "load_parquet_file", dummy_load_parquet_file)


def test_load_daily_all_months():
    df = load_daily(
        asset_type=AssetType.Stocks,
        bucket_name="alpha",
        token={
            "R2_ENDPOINT_URL": "http://dummy",
            "R2_ACCESS_KEY_ID": "dummy",
            "R2_SECRET_ACCESS_KEY": "dummy",
        },
    )
    # According to dummy data, there should be 3 records
    assert len(df) == 3
    expected_values = [1, 2, 3]
    assert list(df["value"]) == expected_values


def test_load_daily_with_range():
    # Test loading only from "2023.02" to "2023.03"
    df = load_daily(
        asset_type=AssetType.Stocks,
        bucket_name="alpha",
        month_range=("2023.02", "2023.03"),
        token={
            "R2_ENDPOINT_URL": "http://dummy",
            "R2_ACCESS_KEY_ID": "dummy",
            "R2_SECRET_ACCESS_KEY": "dummy",
        },
    )
    assert len(df) == 2
    expected_values = [2, 3]
    assert list(df["value"]) == expected_values


def test_load_daily_missing_month():
    # Simulate missing a middle month, which should raise an exception.
    def dummy_list_missing(bucket_name, repo_name, token=None):
        return {
            "2023.01": f"{bucket_name}/ds/{repo_name}/2023.01.parquet",
            # "2023.02" is missing
            "2023.03": f"{bucket_name}/ds/{repo_name}/2023.03.parquet",
        }

    monkeypatch = pytest.MonkeyPatch()
    monkeypatch.setattr(storage, "list_parquet_files", dummy_list_missing)

    with pytest.raises(ValueError):
        load_daily(
            asset_type=AssetType.Stocks,
            bucket_name="alpha",
            token={
                "R2_ENDPOINT_URL": "http://dummy",
                "R2_ACCESS_KEY_ID": "dummy",
                "R2_SECRET_ACCESS_KEY": "dummy",
            },
        )
    monkeypatch.undo()
