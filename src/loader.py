import pandas as pd

def load_stock_data():
    """
    Загрузка данных по акциям (S&P 500 stock data)
    Колонки: Date, Open, High, Low, Close, Volume, Name
    """
    url = "https://finance.yahoo.com/quote/..."
    df = pd.read_csv(url)
    return df

if __name__ == "__main__":
    data = load_stock_data()
    print("Data loaded successfully")