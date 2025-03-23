from enum import Enum


class AssetType(Enum):
    Stocks = "stocks-daily-price"
    ETFs = "etfs-daily-price"
    Indices = "indices-daily-price"
    Cryptocurrencies = "cryptocurrencies-daily-price"
