# create a unit test
import json
import ast
import unittest
import pandas as pd
from dotenv import load_dotenv
import os
from evaluator import check_missing, get_return_by_sticker, get_stock_info, get_stock_info_by_ticker, main2


class TestBacktest(unittest.TestCase):
    """
    Unit tests for backtesting and data processing.
    """
    def setUp(self):
        load_dotenv()

    def test_check_missing_stock_codes_by_log(self):
        """
        Check for missing stock codes by logging the stock codes in the extracted data.
        """
        with open("data/missing_download.txt", "r", encoding="utf-8-sig") as f:
            content = f.read().strip()
            missing_stock_codes_log = content.split("\n\n")
        missing_by_group = {}
        for idx, log in enumerate(missing_stock_codes_log):
            assert log.startswith("Processing "), "Missing stock codes should start with 'Processing '"
            lines = log.split("\n")
            stock_list = lines[0].split("codes:")[1].strip()
            #stock_list = json.loads(stock_list)
            stock_list =  ast.literal_eval(stock_list)
            count = lines[1].split(" ")[0]
            assert count.isdigit(), "The count of missing stock codes should be a number"
            list1 = lines[2].split(":")[0]
            if len(lines) > 3:
                list2 = lines[3].split(":")[0]
                listall = list1.replace("]",",") +  list2.replace("[","")
            else:
                listall = list1
            print(f"Log {idx + 1}: {count} missing stock codes, {listall}")

            missing_list =  ast.literal_eval(listall)
            missing_by_group[idx] = {
                "count": int(count),
                "stock_codes": missing_list,
                "list": listall
            }
        with open(f"data/missing_stock_codes_by_log.json", "w", encoding="utf-8") as f:
            json.dump(missing_by_group, f, ensure_ascii=False, indent=4)


    def test_check_missing_stock_codes(self):
        """
        Check for missing stock codes in the extracted data.
        """
        group_to_check = None # 7  # specify the group to check
        with open("data/missing_stock_codes_by_log.json", "r", encoding="utf-8") as f:
            missing_by_group_log = json.load(f)
        with open("data/reverse_lut.json", "r", encoding="utf-8") as f:
            reverse_lut = json.load(f)
        # build a mapping with group as key and stock codes list as values
        stock_list_by_group = {}
        for stock_code, group in reverse_lut.items():
            if group not in stock_list_by_group:
                stock_list_by_group[group] = []
            stock_list_by_group[group].append(stock_code)

        missing_stock_codes_by_group = {}
        for group, stock_codes in stock_list_by_group.items():
            print(f"Group: {group}, Stock Codes: {len(stock_codes)}")
            if group_to_check and group != group_to_check:
                continue

            # read the CSV file for the group
            date_str = "2025_06_08_00_47_58"  # example date, adjust as needed
            # df = pd.read_csv("your_file.csv", header=[0, 1], index_col=0)
            df = pd.read_csv(f"data/downloaded/stock_group{group}_{date_str}.csv", header=[0,1], index_col=0, encoding='utf-8-sig')
            # check if the stock codes in the CSV file match the stock codes in the group
            csv_stock_codes = df.columns.levels[1].tolist()
            for idx, code in enumerate(csv_stock_codes):

                stock_prices = df.xs(key=code, level=1, axis=1)
                # the first row of the stock prices
                values0 = stock_prices.iloc[0]
                values1 = stock_prices.iloc[2]
                values2 = stock_prices.iloc[3]

                if values0.isna().all() and values1.isna().all() and values2.isna().all():
                    #print(f"Stock code {code} has all NaN values in the first row.")
                    if group not in missing_stock_codes_by_group:
                        missing_stock_codes_by_group[group] = []
                    missing_stock_codes_by_group[group].append(code)




            print(f"CSV Stock Codes: {len(csv_stock_codes)}")

        print("Missing Stock Codes by Group:")
        missing_by_group = {}
        for group, missing_codes in missing_stock_codes_by_group.items():
            #csv_stock_codes = [code.replace('.XSHG', '').replace('.XSHE', '') for code in csv_stock_codes if code.startswith(('6', '0'))]
            #missing_stock_codes = set(stock_codes) - set(csv_stock_codes)

            missing_from_log = missing_by_group_log.get(str(group), {})           
            count_in_log = missing_from_log.get("count", 0)
            count_now = len(missing_codes)
            missed_in_log = missing_from_log.get("list")

            print(f"Group: {group}, Missing in log:{count_in_log}, code: {missed_in_log}")
            print(f"Group: {group}, Missing    now:{count_now}, code: {missing_codes}")
            if count_now - count_in_log != 0:
                print(f"###Group: {group}, Count in log: {count_in_log}, Count now: {count_now}")
            missing_by_group[group] = {
                "count": count_now,
                "missing_codes": missing_codes,
            }
        with open("data/missing_stock_codes_from_dnld.json", "w", encoding="utf-8") as f:
            json.dump(missing_by_group, f, ensure_ascii=False, indent=4)

    def test_download_missing(self):
        """
        Test the backtesting process by extracting stock codes and dates from a CSV file,
        """
        df = pd.read_csv("output/extracted_all_filled2.csv", encoding='utf-8-sig')
        df = df[df['stock_code'].notna()]
        df = df[df['date'] > 20240406]
        df = df[df['date'] < 20250521]  # filter 
        df = df[df['stock_code'] != "N/A"]  # filter out rows with 'N/A' in 'stock_code' 
        group = 7
        # now get all the stock codes 
        stock_codes = df['stock_code'].unique().tolist()
        reverse_lut = get_stock_info(stock_codes, start_date='2024-04-06', end_date='2025-05-21',missing_group=group)
        print("processed missing group:", group)






    def test_backtest(self):
        """
        Test the backtesting process by extracting stock codes and dates from a CSV file,
        """
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

        
    def test_check_a_stock_return(self):
        """
        Check the return of a stock in the backtesting process.
        """
        df = pd.read_csv("output/extracted_all_filled2.csv", encoding='utf-8-sig')

        for idx, row in df.iterrows():
            stock_code = row['stock_code']
            if pd.isna(stock_code) or stock_code == "N/A":
                print(f"Row {idx} has no stock code, skipping.")
                continue
            if not isinstance(stock_code, str):
                print(f"Row {idx} has invalid stock code type: {type(stock_code)}, skipping.")
                continue
            ticker = stock_code.strip().upper()
            date_mentioned = row['date']
            if ' ' in ticker or ticker == '':
                print(f"Row {idx} has invalid ticker: {ticker}, skipping.")
                continue

            # check if the ticker is missing in retrieve stock info
            is_in_missing_list = check_missing(ticker)
            if is_in_missing_list:
                print(f"Ticker {ticker} is in the missing stock codes list, skipping.")
                continue
            else:
                # get the stock info by ticker
                df_stock_info = get_stock_info_by_ticker(ticker)
                if df_stock_info is None:
                    print(f"No stock info found for ticker {ticker}, skipping.")
                    continue
                break

        # now we have date mentioned and the ticker
        # check the price on the date mentioned and ndays later
        ndays_list = [14, 30, 35, 60, 90]  # days to check later
        mentioned , price_list,extra_day_list = get_return_by_sticker(ticker, date_mentioned, df_stock_info, ndays_list)

        print(f"Ticker: {ticker}, Date mentioned: {date_mentioned},with price:{mentioned[2]} at extraday: {mentioned[1]} days")
        print(f"With ndays later:{ndays_list}, Price list: {price_list}, extra days: {extra_day_list}")



    def test_main1(self):
        """
        Main function to run the backtesting process.
        """
        from evaluator import main1

        df = pd.read_csv("output/extracted_all_filled2.csv", encoding='utf-8-sig')
        days_list = os.getenv("DAYS_LIST")
        later_days =  ast.literal_eval(days_list) if days_list else None
        return_info = main1(df_stock_info=df , ndays_list=later_days)
        with open("data/return_info.json", "w", encoding="utf-8") as f:
            json.dump(return_info, f, indent=4, ensure_ascii=False)
        df = pd.DataFrame(return_info)
        df.to_csv("data/return_info.csv", index=False, encoding='utf-8-sig')

    def test_main2(self):
        df = pd.read_csv("data/return_info.csv", encoding='utf-8-sig')
        main2(df, output_file="data/return_info_ex.csv")