# create a unit test
import json
import re
import unittest
from pathlib import Path
from dotenv import load_dotenv
import os
from service.helper import clean_vtt_to_script
import pandas as pd




class TestConvert(unittest.TestCase):
    def setUp(self):
        load_dotenv()

    def test_convert(self):
        with open("output/my_subs.en.vtt", "r", encoding="utf-8") as f:
            vtt_content = f.read()
        # sed '/^[0-9]*:[0-9]*:[0-9]*,[0-9]* --> [0-9]*:[0-9]*:[0-9]*,[0-9]*$/d
        #cleaned1 = re.sub(r'^\d{2}:\d{2}:\d{2}\.\d{3} --> \d{2}:\d{2}:\d{2}\.\d{3}.*$', '', vtt_content, flags=re.MULTILINE)
        cleaned2 = clean_vtt_to_script("output/my_subs.en.vtt")

        print(cleaned2[:1000])  # Preview first 1000 chars
        pass
    
    def test_shorten(self):
        df = pd.read_csv("output/video_metadata.csv", encoding='utf-8-sig')
        df['description'] = df['description'].apply(lambda x: x[71:160] if isinstance(x, str) else "")
        df.drop(columns=['tags'], inplace=True, errors='ignore')
        df.to_csv("output/video_metadata_short.csv", index=False, encoding='utf-8-sig')
    

    def test_revise_result(self):
        all = []
        for file in os.listdir("output/extracted"):
            if file.endswith(".json"):
                date_str = file.split("_")[0]
                file = os.path.join("output/extracted", file)
                with open(file, "r", encoding="utf-8") as f:
                    stock_list = json.load(f)
                    # remove duplicate stocks
                    stocks = [s['stock'] for s in stock_list if 'stock' in s]
                    stocks_unique = list(set(stocks))
                    for s in stocks_unique:
                        idx = next((i for i, d in enumerate(stock_list) if d['stock'] == s), None)
                        stock = stock_list[idx]
                        stock['date'] = date_str
                        all.append(stock)
                    #for stock in stock_list:
                    #    stock['date'] = date_str
                    #    all.append(stock)



        df = pd.DataFrame(all)
        # remove the rows that the date is smaller than 20240410
        df = df[df['date'] >= '20240406'] # remove 40
        # filter the rows with no 'stock_code'
        df_with_sc = df[df['stock_code'].notna()]
        df_with_sc.to_csv("output/with_sc.csv", index=False, encoding='utf-8-sig')
        df_missing_sc = df[df['stock_code'].isna()]
        print(f"Number of stocks with no stock_code: {len(df_missing_sc)}")

        # get the list of stock names with no 'stock_code'
        missing_stock_names = df_missing_sc['stock'].unique().tolist()
        assert 'PayPal' in missing_stock_names, "Paypal should be in the missing stock names"
        print(f"Missing stock codes for stocks: {missing_stock_names}")
        with open("output/extracted_missing_stock_codes.json", "w", encoding="utf-8") as f:
            json.dump(missing_stock_names, f, ensure_ascii=False, indent=4)



        #df.to_csv("output/extracted_all.csv", index=False, encoding='utf-8-sig')
        print(df.head(10))
    
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

        

