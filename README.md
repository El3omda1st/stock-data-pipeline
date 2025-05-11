
# Stock Data Pipeline with Airflow, DBT, and Streamlit

This project demonstrates a complete data pipeline for stock data analysis, utilizing Airflow for orchestration, DBT for transformation, and Streamlit for visualization. The pipeline extracts stock data, processes it, and makes it available for analysis and reporting.

## Project Overview

This project involves the following components:
- **Data Ingestion**: Fetching stock price data using the `yfinance` Python library.
- **Data Transformation**: Cleaning and transforming the data using DBT, creating a staging area and a fact table.
- **Data Orchestration**: Automating the data pipeline using Apache Airflow with two primary Directed Acyclic Graphs (DAGs) for backfilling and daily updates.
- **Visualization**: A simple Streamlit dashboard for visualizing the stock data.

## Project Components

### 1. **Docker & Docker Compose**
   - The entire pipeline is containerized using Docker and Docker Compose, making it easy to deploy and manage dependencies in isolated environments.

### 2. **Airflow DAGs**
   - **Backfill DAG**: Used to fetch historical stock data and load it into the database.
   - **Daily Update DAG**: Automates the ingestion, cleaning, and transformation of daily stock data.

### 3. **DBT Models**
   - **Staging Area**: A model that cleans and standardizes the raw stock data.
   - **Fact Table**: A model that aggregates the stock data, ready for analysis and reporting.

### 4. **Streamlit Dashboard**
   - A simple dashboard that allows for the visualization of the stock data. It enables users to explore the trends and insights from the stock data.

## Technologies Used
- **Airflow**: Workflow orchestration tool for managing ETL tasks.
- **DBT**: Data Build Tool for transforming raw data into structured models.
- **Streamlit**: Used for creating a simple interactive dashboard for visualizing the stock data.
- **Docker**: For containerizing the entire project and its dependencies.
- **Python**: Used for data manipulation, ingestion (via `yfinance`), and processing.
- **PostgreSQL**: The database where the stock data is stored.

## Setup & Installation

### Prerequisites
Ensure you have the following installed:
- **Docker** & **Docker Compose** for containerization.
- **Python 3.x** for running the pipeline code.
- **PostgreSQL** for the database setup.

### 1. Clone the repository
```bash
git clone https://github.com/El3omda1st/stock-data-pipeline.git
cd stock-data-pipeline
```

### 2. Build and Run Docker Containers
Make sure Docker is installed and running on your machine. Then, build and start the containers using Docker Compose:
```bash
docker-compose up --build
```

### 3. Set Up the PostgreSQL Database
After the Docker containers are up and running, you can set up the PostgreSQL database. Ensure you have the correct database environment variables set in your `docker-compose.yml` file:
- **DB_HOST**: Hostname for the database (usually `db` when using Docker Compose).
- **DB_NAME**: Name of the database to store stock data.
- **DB_USER**: Database username.
- **DB_PASSWORD**: Database password.

To create the database, run the following command:
```bash
docker-compose exec db psql -U <your_db_user> -c "CREATE DATABASE stock_data;"
```

Make sure to replace `<your_db_user>` with the user you configured in the Docker Compose file.

### 4. Airflow DAGs
Once the containers are running, you can access the Airflow web interface at `http://localhost:8080`. Here you can trigger the two DAGs:
- **Backfill**: To load historical stock data into the database.
- **Daily Updates**: For regular daily updates of stock data.

DBT models will be automatically run as part of the Airflow DAGs.

### 5. Run the Streamlit Dashboard
After the pipeline has processed data, run the Streamlit dashboard:
```bash
streamlit run dashboard.py
```

### 6. Check the Results
You can view the output from the DBT models in your PostgreSQL database and visualize the stock data via the Streamlit dashboard.

## Project Structure
```
.
├── dags/                     # Airflow Directed Acyclic Graphs (DAGs)
├── dbt/                      # DBT models and configurations
├── dashboard.py              # Streamlit Dashboard for visualization
├── docker-compose.yml        # Docker Compose configuration
├── Dockerfile                # Docker configuration
├── requirements.txt          # Python dependencies
├── logs/                     # Airflow logs
└── README.md                 # Project documentation
```
