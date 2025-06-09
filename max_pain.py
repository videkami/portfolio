import yfinance as yf
import pandas as pd

column_headers = ['expiration', 'max_pain_strike', 'openInterest_calls', 'openInterest_puts']
keep_columns = ['strike','openInterest','inTheMoney']

# symbol = input("Symbol: ")
symbol = "SPY"
ticker = yf.Ticker(symbol)
expiration_dates = ticker.options
current_price = ticker.fast_info.last_price
print(f"The current price for symbol '{symbol}' is ${round(current_price,2)}")

maxPain_list = []
for expDate in expiration_dates:
    df_calls = pd.DataFrame(ticker.option_chain(expDate).calls, columns=keep_columns)
    df_calls = df_calls[df_calls['inTheMoney']]
    df_calls.rename(columns={'openInterest': 'openInterest_calls'}, inplace=True)
    df_calls['price-strike'] = round(current_price - df_calls['strike'],2)

    df_puts = pd.DataFrame(ticker.option_chain(expDate).puts, columns=keep_columns)
    df_puts = df_puts[df_puts['inTheMoney']]
    df_puts.rename(columns={'openInterest': 'openInterest_puts'}, inplace=True)
    df_puts['price-strike'] = round(df_puts['strike'] - current_price,2)

    df = pd.concat([df_calls, df_puts])
    df.reset_index(drop=True, inplace=True)

    df['call_value'] = df['price-strike'] * df['openInterest_calls']
    df['put_value'] = df['price-strike'] * df['openInterest_puts']
    df = df.fillna(0)
    df['total_value'] = df['call_value'] + df['put_value']
    
    max_pain = df.iloc[df['total_value'].idxmax()]
    new_row = {'expiration': expDate, 'max_pain_strike': max_pain['strike'], 'openInterest_calls':max_pain['openInterest_calls'], 'openInterest_puts': max_pain['openInterest_puts']}
    maxPain_list.append(new_row)

# Start index at 1 to make it more human readable
df_allExpirations = pd.DataFrame(maxPain_list, columns= column_headers)
df_allExpirations[['max_pain_strike', 'openInterest_calls', 'openInterest_puts']] = df_allExpirations[['max_pain_strike', 'openInterest_calls', 'openInterest_puts']].astype('Int64')
df_allExpirations.index += 1
print(df_allExpirations)