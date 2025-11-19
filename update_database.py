# Importiamo tutte le librerie necessarie all'inizio
import sqlite3
import yfinance as yf
import pandas as pd
import pandas_datareader.data as pdr
import datetime
from tqdm import tqdm

# --- COSTANTI GLOBALI ---
DB_NAME = 'ita100_stock_and_macro.db'
fred_series_map = {
    'btp_10y_yield': 'IRLTLT01ITM156N', 'bund_10y_yield': 'IRLTLT01DEM156N',
    'eu_inflation_index': 'CP0000EZ19M086NEST', 'eu_gdp_value': 'CLVMEURSCAB1GQEA19',
    'ecb_deposit_rate': 'ECBDFR', 'eu_pmi_manufacturing': 'BSCICP02EZM460S',
    'brent_oil_price': 'DCOILBRENTEU', 'eur_usd_exchange_rate': 'DEXUSEU',
    'vix_close': 'VIXCLS', 'it_inflation_index': 'CP0000ITM086NEST',
    'it_gdp_value': 'CLVMNACSCAB1GQIT', 'it_pmi_manufacturing': 'BSCICP02ITM460S'
}

# --- FUNZIONE 1: AGGIORNAMENTO PREZZI GIORNALIERI ---
def update_daily_prices():
    """
    Scarica e aggiunge solo i nuovi dati di prezzo per ogni azione.
    """
    print("\n--- Inizio aggiornamento Tabella: daily_prices ---")
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    try:
        cursor.execute("SELECT id, ticker FROM securities_master")
        securities = cursor.fetchall()
        
        for security in tqdm(securities, desc="Aggiornamento Prezzi"):
            security_id, ticker_symbol = security
            
            cursor.execute("SELECT MAX(price_date) FROM daily_prices WHERE security_id = ?", (security_id,))
            last_date_str = cursor.fetchone()[0]
            
            if last_date_str is None:
                start_date_prices = "2002-01-01"
            else:
                last_date = datetime.datetime.strptime(last_date_str, '%Y-%m-%d')
                start_date_prices = (last_date + datetime.timedelta(days=1)).strftime('%Y-%m-%d')

            if start_date_prices >= datetime.date.today().strftime('%Y-%m-%d'):
                continue
            
            price_data = yf.download(ticker_symbol, start=start_date_prices, auto_adjust=True, progress=False)
            
            if price_data.empty:
                continue

            price_data = price_data[price_data['Close'] > 0]
            price_data = price_data[(price_data['High'] >= price_data['Open']) & (price_data['High'] >= price_data['Close'])]
            
            price_data.reset_index(inplace=True)
            price_data.rename(columns={'Date': 'price_date', 'Open': 'open', 'High': 'high', 'Low': 'low', 'Close': 'close', 'Volume': 'volume'}, inplace=True)
            price_data['security_id'] = security_id
            price_data['price_date'] = price_data['price_date'].dt.strftime('%Y-%m-%d')
            columns_to_insert = ['security_id', 'price_date', 'open', 'high', 'low', 'close', 'volume']
            data_to_insert = price_data[columns_to_insert]

            insert_query = "INSERT OR IGNORE INTO daily_prices (security_id, price_date, open, high, low, close, volume) VALUES (?, ?, ?, ?, ?, ?, ?);"
            cursor.executemany(insert_query, data_to_insert.values.tolist())
            conn.commit()

    except Exception as e:
        print(f"  - ERRORE CRITICO durante l'aggiornamento dei prezzi: {e}")
    finally:
        if conn:
            conn.close()
        print("--- Aggiornamento 'daily_prices' completato. ---")

# --- FUNZIONE 2: AGGIORNAMENTO DATI MACRO ---
def update_macro_data():
    """
    Ricrea completamente la tabella dei dati macro per garantire coerenza.
    """
    print("\n--- Inizio aggiornamento Tabella: macro_data ---")
    try:
        start_date = "2002-01-01"
        end_date = datetime.datetime.now()
        
        all_series = []
        for col_name, series_id in fred_series_map.items():
            series = pdr.get_data_fred(series_id, start=start_date, end=end_date)
            series.rename(columns={series_id: col_name}, inplace=True)
            all_series.append(series)
        
        macro_df = pd.concat(all_series, axis=1)
        macro_df.sort_index(inplace=True)
        macro_df.ffill(inplace=True)
        
        macro_df['eu_inflation_rate'] = macro_df['eu_inflation_index'].pct_change(periods=365) * 100
        macro_df['it_inflation_rate'] = macro_df['it_inflation_index'].pct_change(periods=365) * 100
        macro_df['eu_gdp_growth'] = macro_df['eu_gdp_value'].pct_change(periods=365) * 100
        macro_df['it_gdp_growth'] = macro_df['it_gdp_value'].pct_change(periods=365) * 100
        macro_df['btp_bund_spread'] = macro_df['btp_10y_yield'] - macro_df['bund_10y_yield']
        
        columns_to_drop = ['eu_inflation_index', 'it_inflation_index', 'eu_gdp_value', 'it_gdp_value', 'bund_10y_yield']
        macro_df.drop(columns=columns_to_drop, inplace=True)
        macro_df.dropna(inplace=True)
        
        conn = sqlite3.connect(DB_NAME)
        df_to_insert = macro_df.reset_index()
        df_to_insert.rename(columns={'index': 'data_date'}, inplace=True)
        df_to_insert['data_date'] = pd.to_datetime(df_to_insert['data_date']).dt.strftime('%Y-%m-%d')
        df_to_insert.to_sql('macro_data', conn, if_exists='replace', index=False)
        
        print(f"Tabella 'macro_data' ricreata con successo con {len(df_to_insert)} righe.")

    except Exception as e:
        print(f"  - ERRORE CRITICO durante l'aggiornamento dei dati macro: {e}")
    finally:
        if 'conn' in locals() and conn:
            conn.close()
        print("--- Aggiornamento 'macro_data' completato. ---")

# --- FUNZIONE PRINCIPALE (MAIN) ---
def main():
    """
    Funzione principale che esegue tutti gli aggiornamenti in sequenza.
    """
    print("===== INIZIO SCRIPT DI AGGIORNAMENTO DATABASE =====")
    update_daily_prices()
    update_macro_data()
    print("\n===== SCRIPT DI AGGIORNAMENTO COMPLETATO =====")

# Questo blocco di codice viene eseguito solo quando si avvia lo script direttamente.
if __name__ == "__main__":
    main()
