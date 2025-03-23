from setuptools import setup, find_packages

setup(
    name="alpha-datasets",
    version="0.1.0",
    author="Your Name",
    description="A library to load daily asset data from Cloudflare R2 and merge into a DataFrame.",
    packages=find_packages(),
    install_requires=[
        "pandas",  # For DataFrame handling
        "s3fs",  # For accessing Cloudflare R2 via S3 interface
        "boto3",  # For boto3 client usage
    ],
    python_requires=">=3.12",
)
