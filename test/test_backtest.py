# create a unit test
import json
from datetime import datetime
import unittest
import pandas as pd
import yfinance as yf
from dotenv import load_dotenv



def get_stock_info(stock_code_list, start_date=None, end_date=None):
    """
    use yfinance to get the stock information for a list of stock codes.
    Args:
        stock_code_list (list): A list of stock codes.
    Returns:
        dict: A dictionary with stock codes as keys and their information as values.
    """
    # spliet the stock_code_list into chunks of 20
    chunk_size = 20
    stock_code_list_ll = [stock_code_list[i:i + chunk_size] for i in range(0, len(stock_code_list), chunk_size)]
    # build a mapping for chuck and stock codes
    stock_code_map = {int(i/chunk_size): stock_code_list[i:i + chunk_size] for i in range(0, len(stock_code_list), chunk_size)}
    # build a reverse mapping for stock codes
    reverse_stock_code_map = {stock_code: i for i, stock_code_list in stock_code_map.items() for stock_code in stock_code_list}
    today = datetime.now().strftime('%Y_%m_%d_%H_%M_%S')
    if len(stock_code_list) > chunk_size:  
        # to chunk_size for yfinance API
        print(f"Limiting stock_code_list to {chunk_size} for yfinance API") 
        stock_code_list_ll = [stock_code_list[i:i + 20] for i in range(0, len(stock_code_list), 20)]
        print(f"Splitting stock codes into {len(stock_code_list_ll)} chunks of 20")
        interval = '1d'  # Set the interval for yfinance API
        for idx, stock_code_list in enumerate(stock_code_list_ll):
            print(f"Processing chunk of stock codes: {stock_code_list}")
            df_ml = yf.download(stock_code_list, 
                        start=start_date, 
                        end=end_date, 
                        interval=interval, 
                        rounding=True)
            df_ml.to_csv(f"data/downloaded/stock_group{idx}_{today}.csv", encoding='utf-8-sig')
            if idx == 3:
                print("pause after 4 chunks for testing purposes.")
                pass
    return reverse_stock_code_map
    # Uncomment the following lines if you want to use yfinance to get stock data


    #import yfinance as yf
    #stock_info = {}
    #df = yf.download(
    #    tickers=stock_code_list,
    #    start=start_date,
    #    end=end_date,
    #    group_by='ticker',
    #    auto_adjust=True,
    #    threads=True,
    #    progress=False
    #)
    #for stock_code in stock_code_list:


class TestBacktest(unittest.TestCase):
    """
    Unit tests for backtesting and data processing.
    """
    def setUp(self):
        load_dotenv()

    def test_backtest(self):
        df = pd.read_csv("output/extracted_all_filled2.csv", encoding='utf-8-sig')
        # filter the rows with no 'stock_code'
        df = df[df['stock_code'].notna()]
        # remove the rows that the date is smaller than 20240410
        df = df[df['date'] > 20240406]

        df = df[df['date'] < 20250521]  # filter 

        df = df[df['stock_code'] != "N/A"]  # filter out rows with 'N/A' in 'stock_code' 
        # now get all the stock codes 
        stock_codes = df['stock_code'].unique().tolist()
        reverse_lut = get_stock_info(stock_codes, start_date='2024-04-06', end_date='2025-05-21')
        with open("data/reverse_lut.json", "w", encoding="utf-8") as f:
            json.dump(reverse_lut, f, ensure_ascii=False, indent=4)

        #for index, row in df.iterrows():
        #    stock_code = row['stock_code']
        #    date = row['date']
        #    # Here you would call your backtest function with the stock_code and date
        #    # For example:
        #    # result = backtest(stock_code, date)
        #    # print(result)

    
    def test_fill_empty(self):
        case = 1
        if case == 0: # the first run
            input_file = "output/extracted_all.csv"
            output_file = "output/extracted_all_filled.csv"
            mapping_file = "output/stock_codes.json"
        else: # the second run
            input_file = "output/extracted_all_filled.csv"
            output_file = "output/extracted_all_filled2.csv"
            mapping_file = "output/left.json"
        
        with open(mapping_file, "r", encoding="utf-8") as f:
            stock_codes = json.load(f)

        s2c_map = {s['company']: s['ticker'] for s in stock_codes if 'company' in s and 'ticker' in s}
        df = pd.read_csv(input_file, encoding='utf-8-sig')
        # fill the empty stock_code with the stock_codes
        empty = []
        for idx, row in df.iterrows():
            if pd.isna(row['stock_code']):
                stock_name = row['stock']
                stock_code = s2c_map.get(stock_name)
                if stock_code == "N/A":
                    stock_code = None
                if stock_code:
                    df.at[idx, 'stock_code'] = stock_code
                    print(f"Filled {stock_name} with {stock_code}")
                else:
                    print(f"Could not find stock code for {stock_name}")
                    empty.append(stock_name)
        df.to_csv(output_file, index=False, encoding='utf-8-sig')
        print("Filled empty stock codes and saved to output/extracted_all_filled.csv")
        with open("output/empty_in_filled.json", "w", encoding="utf-8") as f:
            json.dump(empty, f, ensure_ascii=False, indent=4)


    def test_convert_left(self):
        with open("notes.txt", "r", encoding="utf-8-sig") as f:
            notes = f.read()
        left = []
        for line in notes.splitlines():
            sn, sc = line.split(":")
            sn = sn.strip()
            sc = sc.strip()
            left.append({
                "company": sn,
                "ticker": sc
            })
        with open("output/left.json", "w", encoding="utf-8") as f:
            json.dump(left, f, ensure_ascii=False, indent=4)

        

