from setuptools import setup, find_namespace_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="alpha-isnow",
    version="0.1.5",
    author="Wan, Guolin <wanguolin@gmail.com>",
    description="A library to for https://alpha.isnow.ai",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_namespace_packages(include=["alpha.*"], exclude=["tests.*"]),
    install_requires=[
        "pandas",  # For DataFrame handling
        "s3fs",  # For accessing Cloudflare R2 via S3 interface
        "boto3",  # For boto3 client usage
        "pyarrow>=19.0.0",  # For parquet file support
    ],
    extras_require={
        "dev": [
            "pytest>=8.0.0",  # For running tests
            "python-dotenv>=1.0.0",  # For loading environment variables
            "black>=24.0.0",  # For code formatting
            "isort>=5.0.0",  # For import sorting
            "mypy>=1.8.0",  # For type checking
            "flake8>=7.0.0",  # For linting
            "build>=1.0.0",  # For building distribution packages
            "twine>=4.0.0",  # For uploading to PyPI
        ],
    },
    python_requires=">=3.12",
    data_files=[
        ("", ["LICENSE"]),
        ("", ["README.md"]),
        ("", ["CHANGELOG.md"]),
    ],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
)
