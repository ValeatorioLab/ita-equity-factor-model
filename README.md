# Italian Stock Market Quantitative Strategy 🇮🇹📈

**Author**: *Valerio Lapiello* | **LinkedIn:** [valerio-lapiello](https://www.linkedin.com/in/valerio-lapiello)

---

## Project Overview
This project aims to develop, validate, and backtest a quantitative investment strategy focused on the Italian Stock Market (FTSE MIB & Mid Cap). The goal is to build a robust "Smart Beta" portfolio that outperforms the benchmark by leveraging factor investing principles (Momentum, Low Volatility) and macroeconomic regime filtering.

**Current Status:** 🚧 *Work in Progress* - Phase 1 (Data Engineering) Completed.

## Key Features
* **Robust Data Pipeline:** An automated ETL process (`01_database_creation.ipynb`) that builds a comprehensive SQLite database.
* **High-Quality Data:**
    * **Universe:** 100+ constituents of FTSE MIB and FTSE Italia Mid Cap.
    * **Prices:** Daily OHLCV data cleaned and adjusted for dividends/splits (source: yfinance).
    * **Macro:** Key economic indicators (GDP, Inflation, Rates, Spreads) sourced from FRED and harmonized for frequency.
* **Automated Maintenance:** A standalone script (`update_database.py`) to keep the dataset current with incremental updates.

## Repository Structure
* `01_database_creation.ipynb`: The main notebook documenting the database architecture, data sourcing logic, and quality assurance checks.
* `update_database.py`: Python script for periodic database updates.
* `quant_strategy.db`: *Not included in repo*. Generated locally by running the notebook.

## Technologies Used
* **Python**: Pandas, NumPy, yfinance, pandas-datareader.
* **Database**: SQLite for efficient local storage.
* **Data Engineering**: Custom ETL pipelines with robust error handling and data validation.

## Next Steps
* [ ] **Phase 2:** Exploratory Data Analysis (EDA) and Feature Engineering.
* [ ] **Phase 3:** Alpha Model Development (Machine Learning / Factor Analysis).
* [ ] **Phase 4:** Portfolio Optimization and Backtesting.
