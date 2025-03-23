from setuptools import setup, find_namespace_packages

setup(
    name="alpha-isnow",
    version="0.1.0",
    author="Wan, Guolin <wanguolin@gmail.com>",
    description="A library to for https://alpha.isnow.ai",
    packages=find_namespace_packages(include=["alpha.*"]),
    install_requires=[
        "pandas",  # For DataFrame handling
        "s3fs",  # For accessing Cloudflare R2 via S3 interface
        "boto3",  # For boto3 client usage
    ],
    python_requires=">=3.12",
)
