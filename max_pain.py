import yfinance as yf
import pandas as pd

column_headers = ['expiration', 'max_pain_strike', 'openInterest_calls', 'openInterest_puts', 'total_value']
keep_columns = ['contractSymbol', 'lastTradeDate', 'strike', 'lastPrice', 'bid', 'ask',
       'change', 'percentChange', 'volume', 'openInterest', 'impliedVolatility']

# symbol = input("Symbol: ")
symbol = "SPY"
ticker = yf.Ticker(symbol)
expiration_dates = ticker.options
current_price = ticker.fast_info.last_price
print(f"The current price for symbol '{symbol}' is ${round(current_price,2)}")

maxPain_list = []
for expDate in expiration_dates:
    df_calls = pd.DataFrame(ticker.option_chain(expDate).calls, columns=keep_columns)
    df_calls.rename(columns={'openInterest': 'openInterest_calls'}, inplace=True)
    df_calls['calls_value'] = round(df_calls['openInterest_calls'] * ((df_calls['bid'] * df_calls['ask'])/2),2)
    df_calls['calls_value_cumulativeSum'] = df_calls['calls_value'].cumsum()

    df_puts = pd.DataFrame(ticker.option_chain(expDate).puts, columns=keep_columns)
    df_puts.rename(columns={'openInterest': 'openInterest_puts'}, inplace=True)
    df_puts['puts_value'] = round(df_puts['openInterest_puts'] * ((df_puts['bid'] * df_puts['ask'])/2),2)
    df_puts['puts_value_cumulativeSum'] = df_puts.loc[::-1, 'puts_value'].cumsum()[::-1]

    df = df_calls.merge(df_puts, on='strike', how='outer')

    df = df.fillna(0)
    df['total_value'] = df['calls_value_cumulativeSum'] + df['puts_value_cumulativeSum']
    
    max_pain = df.iloc[df['total_value'].idxmax()]
    
    new_row = {
        'expiration': expDate, 
        'max_pain_strike': max_pain['strike'], 
        'openInterest_calls':max_pain['openInterest_calls'], 
        'openInterest_puts': max_pain['openInterest_puts'],
        'total_value': max_pain['total_value']}
    maxPain_list.append(new_row)

df_allExpirations = pd.DataFrame(maxPain_list, columns= column_headers)
conversion_list = ['max_pain_strike', 'openInterest_calls', 'openInterest_puts']
df_allExpirations[conversion_list] = df_allExpirations[conversion_list].astype('Int64')
df_allExpirations.index += 1
df_allExpirations['total_value'] = df_allExpirations['total_value'].apply(lambda x: "${:.1f}k".format((x/1000)))

print(df_allExpirations)