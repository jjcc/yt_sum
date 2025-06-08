import ast
import json
from datetime import datetime
import yfinance as yf
import pandas as pd

def get_stock_info(stock_code_list, start_date=None, end_date=None, missing_group=None):
    """
    use yfinance to get the stock information for a list of stock codes.
    Args:
        stock_code_list (list): A list of stock codes.
    Returns:
        dict: A dictionary with stock codes as keys and their information as values.
    """
    if missing_group is None:
        missing_only = False
    else:
        missing_only = True
        print(f"Missing group: {missing_group}")
    # spliet the stock_code_list into chunks of 20
    chunk_size = 20
    stock_code_list_ll = [stock_code_list[i:i + chunk_size] for i in range(0, len(stock_code_list), chunk_size)]
    print(f"Splitting stock codes into {len(stock_code_list_ll)} chunks of {chunk_size} each.")
    # build a mapping for chuck and stock codes
    stock_code_map = {int(i/chunk_size): stock_code_list[i:i + chunk_size] for i in range(0, len(stock_code_list), chunk_size)}
    # build a reverse mapping for stock codes
    reverse_stock_code_map = {stock_code: i for i, stock_code_list in stock_code_map.items() for stock_code in stock_code_list}
    today = datetime.now().strftime('%Y_%m_%d_%H_%M_%S')



    if len(stock_code_list) > chunk_size:  
        if missing_only:
            print(f"Processing missing stock codes in group {missing_group}")
            stock_code_list_ll = [stock_code_list_ll[missing_group]]

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


def check_missing(ticker):
    '''
    check if the ticker is in the missing stock codes list.
    Args:
        ticker (str): The stock ticker to check.
    Returns:
        bool: True if the ticker is in the missing stock codes list, False otherwise.
    '''
    with open("data/missing_stock_codes_from_dnld.json", "r", encoding="utf-8") as f:
        missing_stock_codes = json.load(f)

    all_missign_codes = []
    for g, missing in missing_stock_codes.items():
        missing_in_group = missing.get("missing_codes", [])
        all_missign_codes.extend(missing_in_group)
    if ticker in all_missign_codes:
        print(f"Ticker {ticker} is in the missing stock codes list.")
        return True
    return False





def get_stock_info_by_ticker(ticker):
    """
    Get stock information by ticker from the downloaded CSV files.
    Args:
        ticker (str): The stock ticker to get information for.
    Returns:

        pd.DataFrame: A DataFrame containing the stock information for the given ticker.
    """
    with open("data/reverse_lut.json", "r", encoding="utf-8") as f:
        reverse_lut = json.load(f)
    if ticker not in reverse_lut:
        print(f"Ticker {ticker} not found in reverse_lut.")
        return None
    group = reverse_lut[ticker]
    df = pd.read_csv(f"data/downloaded/stock_group{group}_2025_06_08_00_47_58.csv", header=[0, 1], index_col=0, encoding='utf-8-sig')
    df_ticker = df.xs(key=ticker, level=1, axis=1)
    return df_ticker

def get_next_validate_date(df_stock_info, date_mentioned_as_date):
    """
    Get the next valid date from the stock info DataFrame after the date mentioned.
    Args:
        df_stock_info (pd.DataFrame): The DataFrame containing stock information.
        date_mentioned_as_date (pd.Timestamp): The date mentioned in the transcript.
        Returns:
        tuple: A tuple containing the date as index , the next valid date as pd.Timestamp and extra days.
    """
    extra_days = 1
    next_date = date_mentioned_as_date + pd.Timedelta(days=1)
    date_as_index = next_date.strftime('%Y-%m-%d')
    while date_as_index not in df_stock_info.index:
        try:
           next_date = next_date + pd.Timedelta(days=1)
        except Exception as e:
            print(f"Error while getting next date: {e}")
            return None, None, 0
        date_as_index = next_date.strftime('%Y-%m-%d')
        extra_days += 1
        if extra_days > 100:
            print(f"Too many extra days ({extra_days}) for ticker, breaking the loop.")
            return None, None, 0
    return date_as_index,next_date, extra_days

def get_return_by_sticker(ticker, date_mentioned, df_stock_info, ndays_list):
    """
    Get the return of a stock by ticker and date mentioned.
    Args:
        
        ticker (str): The stock ticker.
        date_mentioned (int): The date mentioned in the transcript in YYYYMMDD format.
        df_stock_info (pd.DataFrame): The DataFrame containing stock information.
        ndays_list (list): A list of days to check later.
    Returns:
        tuple: A tuple containing the date as index, extra days, and the price on the mentioned date.
    """
    date_mentioned_as_date = pd.to_datetime(str(date_mentioned), format='%Y%m%d', errors='coerce')

    if date_mentioned_as_date is pd.NaT:
        print(f"Invalid date format for {date_mentioned}, skipping.")
        return []

    # check if the date is in the index of the stock info DataFrame, if not, go next date
    date_as_index = date_mentioned_as_date.strftime('%Y-%m-%d')
    if df_stock_info is not None and date_as_index in df_stock_info.index:
        price_on_mentioned_date = df_stock_info.loc[date_as_index, 'Close']
        #print(f"Price of {ticker} on {date_mentioned_as_date.strftime('%Y-%m-%d')} is {price_on_mentioned_date}")
        mentioned = (date_as_index, 0, price_on_mentioned_date)
        next_date = date_mentioned_as_date
    else:
        # try the next date and so on until we find a date that exists in the index
        date_as_index, next_date, extra_days = get_next_validate_date(df_stock_info, date_mentioned_as_date)
        if date_as_index is None:
            print(f"No valid date found for {ticker} after {date_mentioned}, skipping.")
            return [], [], []
        price_on_next_date = df_stock_info.loc[date_as_index, 'Close']
        #print(f"Price of {ticker}, mentioned at {date_mentioned} on {next_date.strftime('%Y-%m-%d')} is {price_on_next_date}, extra days: {extra_days}")
        mentioned = (date_as_index, extra_days, price_on_next_date)

    # calculate the prices for the next ndays_list
    price_list, extra_day_list = get_prices_by_daylist(ticker, df_stock_info, next_date, ndays_list)

    return mentioned, price_list, extra_day_list


def get_prices_by_daylist(ticker, df_stock_info, next_date, ndays_list):
    """
    Get the prices of a stock for a list of days later from the next date.
    Args:
        ticker (str): The stock ticker.
        df_stock_info (pd.DataFrame): The DataFrame containing stock information.
        next_date (pd.Timestamp): The next date to start checking from.
        ndays_list (list): A list of days to check later.
    Returns:
        list: A list of prices for the specified days later.
        """
    prices_in_ndays = []
    extra_days_list = []
    for ndays in ndays_list:

        ndays_later = next_date + pd.Timedelta(days=ndays)
        ndays_later_as_index = ndays_later.strftime('%Y-%m-%d')
        extra_days = 0
        if ndays_later_as_index not in df_stock_info.index:
            ndays_later_as_index, ndays_later, extra_days = get_next_validate_date(df_stock_info, ndays_later)
        if ndays_later_as_index is None:
            print(f"No valid date found for {ticker} after {ndays} days,maybe it's in future day. skipping.")
            prices_in_ndays.append(None)
            extra_days_list.append(0)
            continue
        price_ndays_later = df_stock_info.loc[ndays_later_as_index, 'Close']
        if price_ndays_later is pd.NA or pd.isna(price_ndays_later):
            prices_in_ndays.append(None)
            extra_days_list.append(0)
            print(f"Price for {ticker} on {ndays_later.strftime('%Y-%m-%d')} is not available, skipping.")
        else:
            #print(f"Price of {ticker} , {ndays+extra_days} later on {ndays_later.strftime('%Y-%m-%d')} is {price_ndays_later}")
            prices_in_ndays.append(float(price_ndays_later))
            extra_days_list.append(extra_days)
        
    return prices_in_ndays, extra_days_list

        
def main1(df_stock_info, ndays_list):
    """
    Check the return of a stock in the backtesting process.
    """
    return_info = []

    for idx, row in df_stock_info.iterrows():
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

            # now we have date mentioned and the ticker
            # check the price on the date mentioned and ndays later
            mentioned , price_list,extra_day_list = get_return_by_sticker(ticker, date_mentioned, df_stock_info, ndays_list)
            if len(mentioned) == 0:
                print(f"No valid data found for ticker {ticker} on date {date_mentioned}, skipping.")
                continue
            return_info.append(
                {"ticker":ticker,
                'date_mentioned': mentioned[0],
                'extra_days': mentioned[1],
                'price_on_mentioned': mentioned[2],
                'ndays_list': ndays_list,
                'price_list': price_list,
                'extra_day_list': extra_day_list
            })

        
            print(f">>row{idx},1.Ticker: {ticker}, Date mentioned: {date_mentioned},with price:{mentioned[2]} at extraday: {mentioned[1]} days")
            print(f">>row{idx},2.With ndays later:{ndays_list}, Price list: {price_list}, extra days: {extra_day_list}")
    # save the return info to a json file
    return return_info

def main2(return_info, output_file):
    """
    Save the return info to a JSON file.
    Args:
        return_info (list): The list of return info to save.
        output_file (str): The file path to save the return info.
    """
    df = return_info.copy()
    df['price_list'] = df['price_list'].apply(ast.literal_eval)
    df['return_list'] = df['price_list'].apply(lambda x: [round((x[i] - x[0]) / x[0] * 100, 2) if (x[i] and x[0] and x[0] != 0) else None for i in range(len(x))])

    extra_col_length = max(df['ndays_list'].apply(len))
    for i in range(extra_col_length):
        df[f'nday_{i+1}_r'] = df['return_list'].apply(lambda x: x[i] if i < len(x) else None)


    with open(output_file, "w", encoding="utf-8") as f:
        df.to_csv(f, index=False, encoding='utf-8-sig')
    print(f"Return info saved to {output_file}")

if __name__ == "__main__":
    
    # 1. collect data part
    #df = pd.read_csv("output/extracted_all_filled2.csv", encoding='utf-8-sig')
    #later_days = [14, 30, 35, 60, 90]  # days to check later
    #return_info = main1(df_stock_info=df , ndays_list=later_days)
    #df = pd.DataFrame(return_info)
    #df.to_csv("data/return_info.csv", index=False, encoding='utf-8-sig')

    # 2. analyze the data part
    df = pd.read_csv("data/return_info.csv", encoding='utf-8-sig')
    main2(df, output_file="data2/return_info2.json")


