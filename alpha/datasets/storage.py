import re
import logging
import s3fs
import pandas as pd
from typing import Dict

logger = logging.getLogger(__name__)

_BUCKET_NAME = "alpha"


def get_r2_filesystem(token: dict | None = None) -> s3fs.S3FileSystem:
    """
    Create and return an s3fs.S3FileSystem object for accessing Cloudflare R2.

    The token dictionary must contain keys: R2_ENDPOINT_URL, R2_ACCESS_KEY_ID, R2_SECRET_ACCESS_KEY.
    If token is None, environment variables will be used.
    """
    if token:
        endpoint_url = token.get("R2_ENDPOINT_URL")
        access_key = token.get("R2_ACCESS_KEY_ID")
        secret_key = token.get("R2_SECRET_ACCESS_KEY")
    else:
        import os

        endpoint_url = os.getenv("R2_ENDPOINT_URL")
        access_key = os.getenv("R2_ACCESS_KEY_ID")
        secret_key = os.getenv("R2_SECRET_ACCESS_KEY")

    if not endpoint_url or not access_key or not secret_key:
        raise ValueError(
            "Incomplete R2 credentials. Provide them via token or environment variables."
        )

    fs = s3fs.S3FileSystem(
        client_kwargs={"endpoint_url": endpoint_url},
        key=access_key,
        secret=secret_key,
        config_kwargs={"signature_version": "s3v4"},
    )
    return fs


def list_parquet_files(repo_name: str, token: dict | None = None) -> Dict[str, str]:
    """
    List all files in the R2 bucket under the path ds/<repo_name>/ that match the format "YYYY.MM.parquet".

    Returns a dictionary where the key is the month string (YYYY.MM) and the value is the full file path.
    """
    fs = get_r2_filesystem(token)
    base_path = f"{_BUCKET_NAME}/ds/{repo_name}/"
    logger.debug(f"Listing files under path {base_path}")
    try:
        files = fs.ls(base_path)
    except Exception as e:
        logger.error(f"Error listing files under {base_path}: {e}")
        raise e

    pattern = re.compile(r"(\d{4}\.\d{2})\.parquet$")
    file_dict = {}
    for file in files:
        match = pattern.search(file)
        if match:
            month_str = match.group(1)
            file_dict[month_str] = file
    return file_dict


def load_parquet_file(
    repo_name: str, month: str, token: dict | None = None
) -> pd.DataFrame:
    """
    Load the parquet file for a specified month.
    """
    fs = get_r2_filesystem(token)
    file_path = f"s3://{_BUCKET_NAME}/ds/{repo_name}/{month}.parquet"
    logger.debug(f"Loading file {file_path}")
    df = pd.read_parquet(file_path, filesystem=fs)
    return df
