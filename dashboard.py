import streamlit as st
import psycopg2
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.ticker import MaxNLocator

# Set page config
st.set_page_config(page_title="Stock Dashboard", layout="wide")

# Database connection
def get_connection():
    try:
        conn = psycopg2.connect(
            host="localhost",
            port="5432",
            dbname="finance_project",
            user="airflow",
            password="airflow"
        )
        return conn
    except Exception as e:
        st.error(f"Error connecting to database: {e}")
        return None

# Load available tickers (no caching here)
def load_tickers(conn):
    query = "SELECT DISTINCT company FROM fact_stock_prices ORDER BY company;"
    try:
        return pd.read_sql(query, conn)['company'].tolist()
    except Exception as e:
        st.error(f"Error loading tickers: {e}")
        return []

# Load data for a selected ticker (no caching here)
def load_data(conn, ticker):
    query = """
        SELECT date, close
        FROM fact_stock_prices
        WHERE company = %s
        ORDER BY date;
    """
    try:
        return pd.read_sql(query, conn, params=(ticker,))
    except Exception as e:
        st.error(f"Error loading data for {ticker}: {e}")
        return pd.DataFrame()

# App layout
st.title("📈 Stock Price Dashboard")

conn = get_connection()

if conn:
    tickers = load_tickers(conn)
    selected_ticker = st.selectbox("Select a company ticker:", tickers)

    df = load_data(conn, selected_ticker)

    if not df.empty:
        st.subheader(f"Closing Prices for {selected_ticker}")
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.plot(df['date'], df['close'], color='blue', linewidth=2)
        ax.set_xlabel("Date")
        ax.set_ylabel("Closing Price ($)")
        ax.set_title(f"Stock Prices for {selected_ticker}", fontsize=16)
        ax.grid(True)

        # Format dates on x-axis
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))

        # Rotate the labels on the x-axis
        plt.xticks(rotation=45)

        # Reduce the number of x-ticks to avoid overcrowding
        ax.xaxis.set_major_locator(MaxNLocator(integer=True, prune='both', nbins=6))

        fig.autofmt_xdate()

        st.pyplot(fig)

        # Show raw data
        with st.expander("📊 Show raw data"):
            st.dataframe(df)
    
    # Close the connection after use
    conn.close()
else:
    st.warning("Unable to connect to the database.")
