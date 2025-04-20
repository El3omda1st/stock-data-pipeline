from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import yfinance as yf
import pandas as pd
import psycopg2
from io import StringIO

# List of top 10 stock tickers
TICKERS = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'META', 'NVDA', 'TSLA', 'BRK-B', 'JPM', 'JNJ']

def backfill_stock_data():
    # Define backfill range (e.g., from Jan 1, 2023 to yesterday)
    start_date = "2023-01-01"
    end_date = (datetime.today() - timedelta(days=1)).strftime('%Y-%m-%d')

    print(f"Backfilling from {start_date} to {end_date}")
    
    # Download stock data
    data = yf.download(TICKERS, start=start_date, end=end_date, group_by='ticker', interval='1d', auto_adjust=True)

    all_data = []
    for ticker in TICKERS:
        try:
            df = data[ticker].copy()
            if df.empty:
                print(f"Warning: No data for {ticker}")
                continue

            df['ticker'] = ticker
            df['date'] = df.index
            df.reset_index(drop=True, inplace=True)
            df.columns = [col.lower() for col in df.columns]
            df.dropna(subset=['open', 'high', 'low', 'close', 'volume'], inplace=True)
            all_data.append(df)

        except Exception as e:
            print(f"Failed to process {ticker}: {e}")

    if not all_data:
        raise ValueError("No stock data was fetched successfully.")

    final_df = pd.concat(all_data, ignore_index=True)
    final_df = final_df[['date', 'ticker', 'open', 'high', 'low', 'close', 'volume']]

    # Store into Postgres
    conn = psycopg2.connect(
        dbname="finance_project",
        user="airflow",
        password="airflow",
        host="postgres",
        port=5432
    )
    cur = conn.cursor()

    buffer = StringIO()
    final_df.to_csv(buffer, index=False, header=False)
    buffer.seek(0)

    cur.copy_expert(
        "COPY stock_prices(date, ticker, open, high, low, close, volume) FROM STDIN WITH CSV",
        buffer
    )

    conn.commit()
    cur.close()
    conn.close()

default_args = {
    'owner': 'airflow',
    'start_date': datetime(2025, 1, 1),
    'retries': 0,
}

with DAG(
    dag_id='backfill_until_yesterday',
    default_args=default_args,
    schedule_interval=None,  # manual run
    catchup=False,
    tags=['backfill']
) as dag:

    backfill_task = PythonOperator(
        task_id='fetch_and_store_backfill',
        python_callable=backfill_stock_data
    )

    backfill_task