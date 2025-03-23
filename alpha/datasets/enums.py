from enum import Enum


class AssetType(Enum):
    Stocks = "ds/stocks-daily-price"
    ETFs = "ds/etfs-daily-price"
    Indices = "ds/indices-daily-price"
    Cryptocurrencies = "ds/cryptocurrencies-daily-price"
