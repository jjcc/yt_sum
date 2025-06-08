from datetime import datetime
import yfinance as yf

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

