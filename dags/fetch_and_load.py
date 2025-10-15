import os
import time
import logging
from datetime import datetime, timezone
from typing import Dict, List

import requests
from google.cloud import bigquery

# configuration
ALPHAVANTAGE_KEY = os.getenv("ALPHAVANTAGE_KEY")           
PROJECT = os.getenv("BQ_PROJECT") or os.getenv("GOOGLE_CLOUD_PROJECT")
DATASET = os.getenv("BQ_DATASET", "stock_etl")
TABLE = os.getenv("BQ_TABLE", "daily_prices")
SYMBOLS = [s.strip().upper() for s in os.getenv("SYMBOLS", "AAPL").split(",") if s.strip()]

API_URL = "https://www.alphavantage.co/query"
API_FUNC = "TIME_SERIES_DAILY"     
OUTPUTSIZE = os.getenv("OUTPUTSIZE", "compact")  # "compact" 100 rows, "full" for all history (don't do full)

SLEEP_BETWEEN_SYMBOLS_SEC = 15 
MAX_ATTEMPTS = 3
BACKOFF_SEC = 20                

BQ_TABLE_ID = f"{PROJECT}.{DATASET}.{TABLE}"

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


def fetch_daily(symbol: str) -> Dict[str, Dict[str, str]]:
    #Fetch daily stock prices
    params = {
        "function": API_FUNC,
        "symbol": symbol,
        "apikey": ALPHAVANTAGE_KEY,
        "outputsize": OUTPUTSIZE,
    }
    r = requests.get(API_URL, params=params, timeout=30)
    r.raise_for_status()
    data = r.json()

    if "Error Message" in data:
        raise RuntimeError(f"Alpha Vantage error for {symbol}: {data['Error Message']}")
    if "Information" in data:
        raise RuntimeError(f"Alpha Vantage info/premium message: {data['Information']}")
    if "Note" in data:
        raise RuntimeError(f"Alpha Vantage throttle note: {data['Note']}")

    series = data.get("Time Series (Daily)")
    if not series:
        raise RuntimeError(f"No 'Time Series (Daily)' found for {symbol}. Response snippet: {str(data)[:300]}")
    return series


def to_rows(symbol: str, series: Dict[str, Dict[str, str]]) -> List[Dict]:
    #Transform API JSON into list of dicts matching the BigQuery table schema
    fetched_at = datetime.now(timezone.utc).isoformat()
    rows = []
    for date_str, stats in series.items():
        rows.append({
            "symbol": symbol,
            "date": date_str,
            "open": float(stats["1. open"]),
            "high": float(stats["2. high"]),
            "low": float(stats["3. low"]),
            "close": float(stats["4. close"]),
            "volume": int(stats["5. volume"]),
            "fetched_at": fetched_at,
        })
    return rows


def load_rows(client: bigquery.Client, rows: List[Dict], symbol: str):
    if not rows:
        logging.info(f"No rows for {symbol}")
        return

    row_ids = [f"{symbol}_{r['date']}" for r in rows]
    errors = client.insert_rows_json(
        BQ_TABLE_ID, rows, row_ids=row_ids,
        skip_invalid_rows=True, ignore_unknown_values=True
    )
    if errors:
        raise RuntimeError(f"BigQuery insert errors: {errors}")
    logging.info(f"Loaded {len(rows)} rows into {BQ_TABLE_ID} for {symbol}.")


def main():
    if not ALPHAVANTAGE_KEY:
        raise RuntimeError("Missing ALPHAVANTAGE_KEY env var.")
    if not PROJECT:
        raise RuntimeError("Missing BQ_PROJECT or GOOGLE_CLOUD_PROJECT env var.")

    client = bigquery.Client(project=PROJECT)

    for idx, sym in enumerate(SYMBOLS):
        if idx > 0:
            time.sleep(SLEEP_BETWEEN_SYMBOLS_SEC)
        logging.info(f"Fetching {sym}…")

        for attempt in range(1, MAX_ATTEMPTS + 1):
            try:
                series = fetch_daily(sym)
                rows = to_rows(sym, series)
                load_rows(client, rows, sym)
                break
            except RuntimeError as e:
                msg = str(e).lower()
                if ("throttle" in msg or "note" in msg) and attempt < MAX_ATTEMPTS:
                    logging.warning(f"{e} | attempt {attempt}/{MAX_ATTEMPTS}, sleeping {BACKOFF_SEC}s…")
                    time.sleep(BACKOFF_SEC)
                    continue
                raise

if __name__ == "__main__":
    main()
