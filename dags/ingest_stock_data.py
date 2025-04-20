from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
from datetime import datetime, timedelta
import yfinance as yf
import pandas as pd
import psycopg2
import os

TICKERS = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'META', 'NVDA', 'TSLA', 'BRK-B', 'JPM', 'JNJ']
RAW_CSV = "/opt/airflow/dags/stock_data_raw.csv"
CLEANED_CSV = "/opt/airflow/dags/stock_data_cleaned.csv"
DBT_DIR = "/opt/airflow/dbt/stock_project"
# ----------- TASK 1: Fetch Data -----------

def fetch_data():
    today = datetime.today()
    start_date = (today - timedelta(days=2)).strftime('%Y-%m-%d')
    end_date = today.strftime('%Y-%m-%d')

    data = yf.download(TICKERS, start=start_date, end=end_date, group_by='ticker', interval='1d')

    all_data = []
    for ticker in TICKERS:
        try:
            df = data[ticker].copy()
            if df.empty:
                print(f"⚠️ No data for {ticker}")
                continue
            df["ticker"] = ticker
            df["date"] = df.index
            df.reset_index(drop=True, inplace=True)
            df.columns = [col.lower() for col in df.columns]
            all_data.append(df)
        except Exception as e:
            print(f"❌ Failed {ticker}: {e}")

    if not all_data:
        raise ValueError("❌ No data downloaded from yfinance.")

    final_df = pd.concat(all_data, ignore_index=True)
    final_df.to_csv(RAW_CSV, index=False)
    print(f"📁 Raw data saved to {RAW_CSV}")

# ----------- TASK 2: Clean Data -----------

def clean_data():
    if not os.path.exists(RAW_CSV):
        raise FileNotFoundError("Raw CSV not found")

    df = pd.read_csv(RAW_CSV)
    df['date'] = pd.to_datetime(df['date']).dt.strftime('%Y-%m-%d')
    df.columns = [col.lower() for col in df.columns]
    df.dropna(subset=['open', 'high', 'low', 'close', 'volume'], inplace=True)
    df = df[['date', 'ticker', 'open', 'high', 'low', 'close', 'volume']]
    df['volume'] = df['volume'].astype('Int64')

    df.to_csv(CLEANED_CSV, index=False)
    print(f"🧼 Cleaned data saved to {CLEANED_CSV}")

# ----------- TASK 3: Load to Postgres -----------

def load_to_postgres():
    if not os.path.exists(CLEANED_CSV):
        raise FileNotFoundError("Cleaned CSV not found")

    df = pd.read_csv(CLEANED_CSV)

    conn = psycopg2.connect(
        dbname="finance_project",
        user="airflow",
        password="airflow",
        host="postgres",
        port=5432
    )
    cur = conn.cursor()

    for row in df.itertuples():
        cur.execute("SELECT 1 FROM stock_prices WHERE date = %s AND ticker = %s LIMIT 1;", (row.date, row.ticker))
        if cur.fetchone():
            print(f"⏭️ Skipping duplicate: {row.ticker} on {row.date}")
        else:
            cur.execute("""
                INSERT INTO stock_prices (date, ticker, open, high, low, close, volume)
                VALUES (%s, %s, %s, %s, %s, %s, %s);
            """, (row.date, row.ticker, row.open, row.high, row.low, row.close, row.volume))
            print(f"✅ Inserted {row.ticker} on {row.date}")

    conn.commit()
    cur.close()
    conn.close()
    print("📥 Data load complete")

# ----------- DAG Definition -----------

default_args = {
    'owner': 'airflow',
    'start_date': datetime(2025, 1, 1),
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

with DAG(
    dag_id='ingest_stock_data',
    default_args=default_args,
    schedule_interval="0 12 * * *",
    catchup=False,
    description="Fetch, clean, and store stock data as 3 separate tasks",
    tags=['stocks', 'modular']
) as dag:

    task_fetch = PythonOperator(
        task_id='fetch_stock_data',
        python_callable=fetch_data,
    )

    task_clean = PythonOperator(
        task_id='clean_stock_data',
        python_callable=clean_data,
    )

    task_load = PythonOperator(
        task_id='load_to_postgres',
        python_callable=load_to_postgres,
    )
    dbt_run = BashOperator(
        task_id='dbt_run',
        bash_command=f'cd {DBT_DIR} && dbt run --profiles-dir /opt/airflow/dbt/profiles',
)

    dbt_test = BashOperator(
        task_id='dbt_test',
        bash_command=f'cd {DBT_DIR} && dbt test --profiles-dir /opt/airflow/dbt/profiles',
)

    # DAG flow: fetch → clean → load
    task_fetch >> task_clean >> task_load >> dbt_run >> dbt_test
