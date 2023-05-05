# The steps to calculate max pain according to investopedia
# 1. Find the difference between stock price and strike price
# 2. Multiply the result by open interest at that strike
# 3. Add together the dollar value for the put and call at that strike
# 4. Repeat for each strike price
# 5. Find the highest value strike price. This price is equivalent to max pain price.

import yfinance as yf
import pandas as pd

symbol = input("Symbol: ")
ticker = yf.Ticker(symbol)
expiration_dates = ticker.options

keep_columns = ['strike','openInterest']
current_price = ticker.history(period="1m")['Close'][0]
print(f"Current price: ${round(current_price,2)}")

df_maxpain= pd.DataFrame(columns=('expiration', 'max_pain_strike', 'openInterest_calls', 'openInterest_puts'))

for expDate in expiration_dates:
    df = pd.DataFrame(ticker.option_chain(expDate).calls, columns=keep_columns)
    df.rename(columns={'openInterest': 'openInterest_calls'}, inplace=True)
    df_puts = pd.DataFrame(ticker.option_chain(expDate).puts, columns=keep_columns)
    df_puts.rename(columns={'openInterest': 'openInterest_puts'}, inplace=True)
    df = pd.merge(left = df, right = df_puts, left_on = 'strike', right_on = 'strike')

    # 1. Find the difference between stock price and strike price
    df['price-strike'] = current_price - df['strike']

    # 2. Multiply the result by open interest at each strike 
    df['call_value'] = df['price-strike'] * df['openInterest_calls']
    df['put_value'] = df['price-strike'] * df['openInterest_puts'] * -1

    # 3. Add together the dollar value for the put and call at that strike
    # 4. Repeat for each strike price
    df['total_value'] = df['call_value'] + df['put_value']
    
    # 5. Find the highest value strike price. This price is equivalent to max pain price.
    max_pain = df.iloc[df['total_value'].idxmax()]
    new_row = {'expiration': expDate, 'max_pain_strike': max_pain['strike'], 'openInterest_calls':max_pain['openInterest_calls'], 'openInterest_puts': max_pain['openInterest_puts']}
    df_temp = pd.DataFrame(new_row, index=[0])
    df_maxpain = pd.concat([df_maxpain, df_temp], ignore_index=True)

# Start index at 1 to make it more human readable
df_maxpain.index += 1
print(df_maxpain)