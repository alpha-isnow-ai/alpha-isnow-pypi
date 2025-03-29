from collections import defaultdict
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


SP500_SYMBOLS = [
    "MMM",
    "AOS",
    "ABT",
    "ABBV",
    "ACN",
    "ADBE",
    "AMD",
    "AES",
    "AFL",
    "A",
    "APD",
    "ABNB",
    "AKAM",
    "ALB",
    "ARE",
    "ALGN",
    "ALLE",
    "LNT",
    "ALL",
    "GOOGL",
    "GOOG",
    "MO",
    "AMZN",
    "AMCR",
    "AEE",
    "AEP",
    "AXP",
    "AIG",
    "AMT",
    "AWK",
    "AMP",
    "AME",
    "AMGN",
    "APH",
    "ADI",
    "ANSS",
    "AON",
    "APA",
    "AAPL",
    "AMAT",
    "APTV",
    "ACGL",
    "ADM",
    "ANET",
    "AJG",
    "AIZ",
    "T",
    "ATO",
    "ADSK",
    "ADP",
    "AZO",
    "AVB",
    "AVY",
    "AXON",
    "BKR",
    "BALL",
    "BAC",
    "BK",
    "BBWI",
    "BAX",
    "BDX",
    "BRK-B",
    "BBY",
    "TECH",
    "BIIB",
    "BLK",
    "BX",
    "BA",
    "BKNG",
    "BWA",
    "BSX",
    "BMY",
    "AVGO",
    "BR",
    "BRO",
    "BF-B",
    "BLDR",
    "BG",
    "BXP",
    "CHRW",
    "CDNS",
    "CZR",
    "CPT",
    "CPB",
    "COF",
    "CAH",
    "KMX",
    "CCL",
    "CARR",
    "CTLT",
    "CAT",
    "CBOE",
    "CBRE",
    "CDW",
    "CE",
    "COR",
    "CNC",
    "CNP",
    "CF",
    "CRL",
    "SCHW",
    "CHTR",
    "CVX",
    "CMG",
    "CB",
    "CHD",
    "CI",
    "CINF",
    "CTAS",
    "CSCO",
    "C",
    "CFG",
    "CLX",
    "CME",
    "CMS",
    "KO",
    "CTSH",
    "CL",
    "CMCSA",
    "CAG",
    "COP",
    "ED",
    "STZ",
    "CEG",
    "COO",
    "CPRT",
    "GLW",
    "CPAY",
    "CTVA",
    "CSGP",
    "COST",
    "CTRA",
    "CRWD",
    "CCI",
    "CSX",
    "CMI",
    "CVS",
    "DHR",
    "DRI",
    "DVA",
    "DAY",
    "DECK",
    "DE",
    "DELL",
    "DAL",
    "DVN",
    "DXCM",
    "FANG",
    "DLR",
    "DFS",
    "DG",
    "DLTR",
    "D",
    "DPZ",
    "DOV",
    "DOW",
    "DHI",
    "DTE",
    "DUK",
    "DD",
    "EMN",
    "ETN",
    "EBAY",
    "ECL",
    "EIX",
    "EW",
    "EA",
    "ELV",
    "EMR",
    "ENPH",
    "ETR",
    "EOG",
    "EPAM",
    "EQT",
    "EFX",
    "EQIX",
    "EQR",
    "ERIE",
    "ESS",
    "EL",
    "EG",
    "EVRG",
    "ES",
    "EXC",
    "EXPE",
    "EXPD",
    "EXR",
    "XOM",
    "FFIV",
    "FDS",
    "FICO",
    "FAST",
    "FRT",
    "FDX",
    "FIS",
    "FITB",
    "FSLR",
    "FE",
    "FI",
    "FMC",
    "F",
    "FTNT",
    "FTV",
    "FOXA",
    "FOX",
    "BEN",
    "FCX",
    "GRMN",
    "IT",
    "GE",
    "GEHC",
    "GEV",
    "GEN",
    "GNRC",
    "GD",
    "GIS",
    "GM",
    "GPC",
    "GILD",
    "GPN",
    "GL",
    "GDDY",
    "GS",
    "HAL",
    "HIG",
    "HAS",
    "HCA",
    "DOC",
    "HSIC",
    "HSY",
    "HES",
    "HPE",
    "HLT",
    "HOLX",
    "HD",
    "HON",
    "HRL",
    "HST",
    "HWM",
    "HPQ",
    "HUBB",
    "HUM",
    "HBAN",
    "HII",
    "IBM",
    "IEX",
    "IDXX",
    "ITW",
    "INCY",
    "IR",
    "PODD",
    "INTC",
    "ICE",
    "IFF",
    "IP",
    "IPG",
    "INTU",
    "ISRG",
    "IVZ",
    "INVH",
    "IQV",
    "IRM",
    "JBHT",
    "JBL",
    "JKHY",
    "J",
    "JNJ",
    "JCI",
    "JPM",
    "JNPR",
    "K",
    "KVUE",
    "KDP",
    "KEY",
    "KEYS",
    "KMB",
    "KIM",
    "KMI",
    "KKR",
    "KLAC",
    "KHC",
    "KR",
    "LHX",
    "LH",
    "LRCX",
    "LW",
    "LVS",
    "LDOS",
    "LEN",
    "LLY",
    "LIN",
    "LYV",
    "LKQ",
    "LMT",
    "L",
    "LOW",
    "LULU",
    "LYB",
    "MTB",
    "MRO",
    "MPC",
    "MKTX",
    "MAR",
    "MMC",
    "MLM",
    "MAS",
    "MA",
    "MTCH",
    "MKC",
    "MCD",
    "MCK",
    "MDT",
    "MRK",
    "META",
    "MET",
    "MTD",
    "MGM",
    "MCHP",
    "MU",
    "MSFT",
    "MAA",
    "MRNA",
    "MHK",
    "MOH",
    "TAP",
    "MDLZ",
    "MPWR",
    "MNST",
    "MCO",
    "MS",
    "MOS",
    "MSI",
    "MSCI",
    "NDAQ",
    "NTAP",
    "NFLX",
    "NEM",
    "NWSA",
    "NWS",
    "NEE",
    "NKE",
    "NI",
    "NDSN",
    "NSC",
    "NTRS",
    "NOC",
    "NCLH",
    "NRG",
    "NUE",
    "NVDA",
    "NVR",
    "NXPI",
    "ORLY",
    "OXY",
    "ODFL",
    "OMC",
    "ON",
    "OKE",
    "ORCL",
    "OTIS",
    "PCAR",
    "PKG",
    "PLTR",
    "PANW",
    "PARA",
    "PH",
    "PAYX",
    "PAYC",
    "PYPL",
    "PNR",
    "PEP",
    "PFE",
    "PCG",
    "PM",
    "PSX",
    "PNW",
    "PNC",
    "POOL",
    "PPG",
    "PPL",
    "PFG",
    "PG",
    "PGR",
    "PLD",
    "PRU",
    "PEG",
    "PTC",
    "PSA",
    "PHM",
    "QRVO",
    "PWR",
    "QCOM",
    "DGX",
    "RL",
    "RJF",
    "RTX",
    "O",
    "REG",
    "REGN",
    "RF",
    "RSG",
    "RMD",
    "RVTY",
    "ROK",
    "ROL",
    "ROP",
    "ROST",
    "RCL",
    "SPGI",
    "CRM",
    "SBAC",
    "SLB",
    "STX",
    "SRE",
    "NOW",
    "SHW",
    "SPG",
    "SWKS",
    "SJM",
    "SW",
    "SNA",
    "SOLV",
    "SO",
    "LUV",
    "SWK",
    "SBUX",
    "STT",
    "STLD",
    "STE",
    "SYK",
    "SMCI",
    "SYF",
    "SNPS",
    "SYY",
    "TMUS",
    "TROW",
    "TTWO",
    "TPR",
    "TRGP",
    "TGT",
    "TEL",
    "TDY",
    "TFX",
    "TER",
    "TSLA",
    "TXN",
    "TXT",
    "TMO",
    "TJX",
    "TSCO",
    "TT",
    "TDG",
    "TRV",
    "TRMB",
    "TFC",
    "TYL",
    "TSN",
    "USB",
    "UBER",
    "UDR",
    "ULTA",
    "UNP",
    "UAL",
    "UPS",
    "URI",
    "UNH",
    "UHS",
    "VLO",
    "VTR",
    "VLTO",
    "VRSN",
    "VRSK",
    "VZ",
    "VRTX",
    "VTRS",
    "VICI",
    "V",
    "VST",
    "VMC",
    "WRB",
    "GWW",
    "WAB",
    "WBA",
    "WMT",
    "DIS",
    "WBD",
    "WM",
    "WAT",
    "WEC",
    "WFC",
    "WELL",
    "WST",
    "WDC",
    "WY",
    "WMB",
    "WTW",
    "WYNN",
    "XEL",
    "XYL",
    "YUM",
    "ZBRA",
    "ZBH",
    "ZTS",
]


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
    symbols: list[str] | None = None,
    extend: bool = False,
    adjust: bool = True,
    to_usd: bool = True,
    rate_to_price: bool = True,
    token: dict | None = None,
    cache: bool = False,
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
        cache: Whether to use caching for loading parquet files (default is False).

    Returns:
        A merged pandas DataFrame containing the data from all loaded parquet files.
    """
    # Get repo_id from asset_type and compute repo_name (last part of the repo_id in lowercase)
    if isinstance(symbols, list):
        if "sp500" in symbols:
            symbols.remove("sp500")
            symbols += SP500_SYMBOLS
        elif "SP500" in symbols:
            symbols.remove("SP500")
            symbols += SP500_SYMBOLS

    repo_id = asset_type.value
    repo_name = repo_id.split("/")[-1].lower()
    logger.debug(f"Loading data: repo_id={repo_id}, repo_name={repo_name}")

    # List all parquet files under ds/<repo_name>/ on R2
    file_dict = list_parquet_files(repo_name=repo_name, token=token)
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
            executor.submit(
                load_parquet_file,
                repo_name=repo_name,
                month=month,
                token=token,
                cache=cache,
            ): month
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
    combined_df["date"] = pd.to_datetime(combined_df["date"])

    combined_df = (
        pd.concat(dfs, ignore_index=True)
        .sort_values(["date", "symbol"])
        .reset_index(drop=True)
    )

    if symbols:
        combined_df = combined_df[combined_df["symbol"].isin(symbols)].copy()

    if adjust and "adj_close" in combined_df.columns:
        adj_factor = combined_df["adj_close"] / combined_df["close"]
        combined_df["adj_open"] = combined_df["open"] * adj_factor
        combined_df["adj_high"] = combined_df["high"] * adj_factor
        combined_df["adj_low"] = combined_df["low"] * adj_factor
        combined_df.drop(columns=["open", "high", "low", "close"], inplace=True)
        combined_df.rename(
            columns={
                "adj_open": "open",
                "adj_high": "high",
                "adj_low": "low",
                "adj_close": "close",
            },
            inplace=True,
        )
    else:
        if "adj_close" in combined_df.columns:
            combined_df.drop(columns=["adj_close"])

    if extend and asset_type == AssetType.ETFs:
        combined_df = extend_etfs(combined_df, month_range=month_range, cache=cache)

    if to_usd:
        if asset_type == AssetType.Forex:
            for index, row in combined_df.iterrows():
                if row["symbol"].endswith("USD"):
                    continue
                combined_df.at[index, "open"] = 1 / row["open"]
                combined_df.at[index, "high"] = 1 / row["high"]
                combined_df.at[index, "low"] = 1 / row["low"]
                combined_df.at[index, "close"] = 1 / row["close"]
                combined_df.at[index, "symbol"] = row["symbol"][3:] + "USD"
        elif asset_type == AssetType.Indices:
            df_forex = load_daily(
                AssetType.Forex,
                token=token,
                month_range=month_range,
                cache=cache,
                to_usd=True,
            )
            combined_df = __convert_indices_to_usd(combined_df, df_forex)

    if rate_to_price and asset_type == AssetType.Bonds:
        for index, row in combined_df.iterrows():
            years_to_maturity = __extract_years_to_maturity(row["symbol"])
            if not years_to_maturity:
                continue
            face_value = 100
            for col in ["open", "high", "low", "close"]:
                rate = row[col]
                combined_df.loc[index, col] = (
                    face_value / (1 + rate) ** years_to_maturity
                )

    combined_df = combined_df.sort_values(["date", "symbol"]).reset_index(drop=True)

    logger.info(f"Merged DataFrame record count: {len(combined_df)}")
    return combined_df


def __extract_years_to_maturity(bond_symbol):
    match = re.search(r"(\d+)([YM])$", bond_symbol)
    if match:
        time_value = int(match.group(1))  # Extract the numeric value
        time_unit = match.group(2)  # Extract the time unit (Y or M)
        if time_unit == "Y":
            return time_value  # It's already in years
        elif time_unit == "M":
            return time_value / 12  # Convert months to years


def extend_etfs(
    df_etfs, cache: bool = False, month_range: tuple[str, str] | None = None
):

    mapping = {
        "AGG": [AssetType.Bonds, "US10Y"],
        "EPP": [AssetType.Indices, "HSI"],
        "EWA": [AssetType.Indices, "AS30"],  # Australia
        "EWO": [AssetType.Indices, "ATX"],  # Austria
        "EWK": [AssetType.Indices, "BEL20"],  # Belgium
        "EWZ": [AssetType.Indices, "IBOV"],  # Brazil
        "EWC": [AssetType.Indices, "SPTSX"],  # Canada
        "FXI": [AssetType.Indices, "SSE50"],  # China
        "EWQ": [AssetType.Indices, "CAC"],  # France
        "EWG": [AssetType.Indices, "DAX"],  # Germany
        "EWH": [AssetType.Indices, "HSI"],  # Hong Kong
        "EWI": [AssetType.Indices, "FTSEMIB"],  # Italy
        "EWJ": [AssetType.Indices, "NKY"],
        "EWM": [AssetType.Indices, "FBMKLCI"],  # Malaysia
        "EWW": [AssetType.Indices, "MEXBOL"],  # Mexico
        "EWN": [AssetType.Indices, "AEX"],  # Netherlands
        "EWS": [AssetType.Indices, "FSSTI"],  # Singapore
        "EZA": [AssetType.Indices, "TOP40"],  # South Africa
        "EWP": [AssetType.Indices, "IBEX"],  # Spain
        "EWD": [AssetType.Indices, "OMX"],  # Sweden
        "EWL": [AssetType.Indices, "SMI"],  # Switzerland
        "EWT": [AssetType.Indices, "TWSE"],  # Taiwan
        "EWU": [AssetType.Indices, "UKX"],  # United Kingdom
        "GLD": [AssetType.Commodities, "GC1"],
        "IEF": [AssetType.Bonds, "US10Y"],
        "IEV": [AssetType.Indices, "SX5E"],
        "IWB": [AssetType.Indices, "SPX"],
        "SHY": [AssetType.Bonds, "US1Y"],
        "SPY": [AssetType.Indices, "SPX"],
        "THD": [AssetType.Indices, "SET50"],  # Thailand
    }
    symbols = df_etfs.symbol.unique()
    mapping = {k: v for k, v in mapping.items() if k in symbols}

    grouped_path_symbols = defaultdict(list)
    for value in mapping.values():
        grouped_path_symbols[value[0]].append(value[1])
    grouped_path_symbols = dict(grouped_path_symbols)
    df_others = pd.concat(
        [
            load_daily(
                asset_type=asset_type,
                symbols=symbols,
                month_range=month_range,
                cache=cache,
                to_usd=True,
            )
            for asset_type, symbols in grouped_path_symbols.items()
        ]
    )

    frames = []
    for etf, other in mapping.items():
        other_symbol = other[1]
        # Get the ETF & Index data
        etf_data = df_etfs[df_etfs["symbol"] == etf]
        if etf_data.empty:
            continue
        other_data = df_others[df_others["symbol"] == other_symbol]
        if other_data.empty:
            continue

        # Find the first overlapping date
        common_dates = etf_data["date"].isin(other_data["date"])
        first_common_date = etf_data.loc[common_dates, "date"].min()

        if pd.isnull(first_common_date):
            print(f"No common date found for {etf} and {other_symbol}")
            continue

        etf_first_common = etf_data[etf_data["date"] == first_common_date]
        other_first_common = other_data[other_data["date"] == first_common_date]

        # Compute the adjustment factor (using closing prices for simplicity)
        adjustment_factor = (
            etf_first_common["close"].values[0] / other_first_common["close"].values[0]
        )

        # Adjust index data before the first common date
        index_data_before_common = other_data[
            other_data["date"] < first_common_date
        ].copy()
        for column in ["open", "high", "low", "close"]:
            index_data_before_common.loc[:, column] *= adjustment_factor
        index_data_before_common.loc[:, "symbol"] = etf

        # Combine adjusted index data with ETF data
        combined_data = pd.concat([index_data_before_common, etf_data])
        frames.append(combined_data)

    symbols_not_in_mapping = set(symbols) - set(mapping.keys())
    frames.append(df_etfs[df_etfs["symbol"].isin(symbols_not_in_mapping)])

    # Concatenate all frames to form the final dataframe
    df = pd.concat(frames).sort_values(by=["date", "symbol"]).reset_index(drop=True)
    return df


def __convert_indices_to_usd(df_indices, df_forex):
    mapping = {
        "ADSMI": "AED",  # United Arab Emirates
        "AEX": "EUR",  # Netherlands
        "AS30": "AUD",  # Australia
        "AS51": "AUD",  # Australia
        "AS52": "AUD",  # Australia
        "ASE": "EUR",  # Greece
        "ATX": "EUR",  # Austria
        "BEL20": "EUR",  # Belgium
        "BELEX15": "RSD",  # Serbia
        "BGSMDC": "BWP",  # Botswana
        "BHSEEI": "BHD",  # Bahrain
        "BKA": "BAM",  # Bosnia and Herzegovina
        "BLOM": "LBP",  # Lebanon
        "BSX": "BMD",  # Bermuda
        "BUX": "HUF",  # Hungary
        "BVLX": "BOB",  # Bolivia
        "BVPSBVPS": "PAB",  # Panama
        "BVQA": "USD",  # Ecuador
        "CAC": "EUR",  # France
        "CASE": "EGP",  # Egypt
        "CCMP": "USD",  # United States
        "COLCAP": "COP",  # Colombia
        "CRSMBCT": "CRC",  # Costa Rica
        "CSEALL": "LKR",  # Sri Lanka
        "CYSMMAPA": "EUR",  # Cyprus
        "DARSDSEI": "TZS",  # Tanzania
        "DAX": "EUR",  # Germany
        "DFMGI": "AED",  # United Arab Emirates
        "DSEX": "BDT",  # Bangladesh
        "DSM": "QAR",  # Qatar
        "ECU": "USD",  # Ecuador
        "FBMKLCI": "MYR",  # Malaysia
        "FSSTI": "SGD",  # Singapore
        "FTN098": "NAD",  # Namibia
        "FTSEMIB": "EUR",  # Italy
        "GGSECI": "GHS",  # Ghana
        "HEX": "EUR",  # Finland
        "HEX25": "EUR",  # Finland
        "HSI": "HKD",  # Hong Kong
        "IBEX": "EUR",  # Spain
        "IBOV": "BRL",  # Brazil
        "IBVC": "VES",  # Venezuela
        "ICEXI": "ISK",  # Iceland
        "IGPA": "CLP",  # Chile
        "INDEXCF": "RUB",  # Russia
        "INDU": "USD",  # United States
        "INDZI": "IDR",  # Indonesia
        "ISEQ": "EUR",  # Ireland
        "JALSH": "ZAR",  # South Africa
        "JCI": "IDR",  # Indonesia
        "JMSMX": "JMD",  # Jamaica
        "JOSMGNFF": "JOD",  # Jordan
        "KFX": "DKK",  # Denmark
        "KNSMIDX": "KES",  # Kenya
        "KSE100": "PKR",  # Pakistan
        "KZKAK": "KZT",  # Kazakhstan
        "LSXC": "LAK",  # Laos
        "LUXXX": "EUR",  # Luxembourg
        "MALTEX": "EUR",  # Malta
        "MBI": "MKD",  # North Macedonia
        "MERVAL": "ARS",  # Argentina
        "MEXBOL": "MXN",  # Mexico
        "MONEX": "EUR",  # Montenegro
        "MOSENEW": "MAD",  # Morocco
        "MSETOP": "MKD",  # North Macedonia
        "MSM30": "OMR",  # Oman
        "NDX": "USD",  # United States
        "NGSEINDX": "NGN",  # Nigeria
        "NIFTY": "INR",  # India
        "NKY": "JPY",  # Japan
        "NSEASI": "KES",  # Kenya
        "NZSE50FG": "NZD",  # New Zealand
        "OMX": "SEK",  # Sweden
        "OSEAX": "NOK",  # Norway
        "PCOMP": "PHP",  # Philippines
        "PFTS": "UAH",  # Ukraine
        "PSI20": "EUR",  # Portugal
        "PX": "CZK",  # Czech Republic
        "RIGSE": "EUR",  # Latvia
        "RTY": "USD",  # United States
        "SASEIDX": "SAR",  # Saudi Arabia
        "SASX10": "BAM",  # Bosnia and Herzegovina
        "SBITOP": "EUR",  # Slovenia
        "SEMDEX": "MUR",  # Mauritius
        "SENSEX": "INR",  # India
        "SET50": "THB",  # Thailand
        "SHCOMP": "CNY",  # China
        "SHSZ300": "CNY",  # China
        "SKSM": "EUR",  # Slovakia
        "SMI": "CHF",  # Switzerland
        "SOFIX": "BGN",  # Bulgaria
        "SPBLPGPT": "PEN",  # Peru
        "SPTSX": "CAD",  # Canada
        "SPX": "USD",  # United States
        "SSE50": "CNY",  # China
        "SX5E": "EUR",  # Europe
        "TA125": "ILS",  # Israel
    }
    symbols = df_indices.symbol.unique()
    mapping = {k: v for k, v in mapping.items() if k in symbols}
    frames = []
    for symbol, currency in mapping.items():
        df_index = df_indices[df_indices["symbol"] == symbol].copy()
        if currency == "USD":
            frames.append(df_index)
            continue
        df_forex_currency = df_forex[df_forex["symbol"] == currency + "USD"].copy()
        if df_index.empty or df_forex_currency.empty:
            continue
        # Merge dataframes on the date column
        merged_df = pd.merge(
            df_index, df_forex_currency, on="date", suffixes=("", "_forex")
        )

        # Multiply the index prices by the corresponding forex rates
        merged_df["open"] = merged_df["open"] * merged_df["open_forex"]
        merged_df["high"] = merged_df["high"] * merged_df["high_forex"]
        merged_df["low"] = merged_df["low"] * merged_df["low_forex"]
        merged_df["close"] = merged_df["close"] * merged_df["close_forex"]

        frames.append(merged_df[["symbol", "date", "open", "high", "low", "close"]])

    df = pd.concat(frames, ignore_index=True)
    return df


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
    file_dict = list_parquet_files(repo_name=repo_name, token=token)
    available_months = sorted(file_dict.keys())
    return available_months
