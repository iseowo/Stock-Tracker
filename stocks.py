import yfinance as yf
import streamlit as st
import pandas as pd
from datetime import timedelta
import datetime
import plotly.graph_objects as go 
import plotly.figure_factory as ff

st.write("""
# Stock Tracker
""")

st.markdown('''
* **Python libraries:** yfinance, pandas, streamlit, plotly
* **Data souce:** [Yahoo Finance](https://ca.finance.yahoo.com/)
''')

# Date information
today = datetime.date.today()
#yesterday = today - timedelta(days=3)
yesterday = today - timedelta(days=1)

# Ticker input 
st.subheader('Please your favourite tickers')
user_input = st.text_area('Tickers', height = 10, value = 'TSLA')


ticker_symbols = user_input.upper()
ticker_symbols = ticker_symbols.replace(","," ")
ticker_symbols = ticker_symbols.split()

# Drop down menu for tickers
ticker_symbol = st.selectbox('Stock to Display', [i for i in ticker_symbols])


# Header for the side bar
st.sidebar.header('Filters')

# Ticker information
tickerData = yf.Ticker(ticker_symbol)
origin = tickerData.history(period = 'max')
origin_listing = origin.index[0]
buy = st.sidebar.date_input('Purchase Date', min_value = origin_listing, max_value = today, value = yesterday)
tickerDf = tickerData.history(period = '1d', start = buy, end = today)

# Purchase day's range
purchase_information = tickerDf.loc[tickerDf.index == str(buy)]
st.sidebar.write(' ** Purchase Day\'s Low:**', purchase_information.Low[0])
st.sidebar.write(' ** Purchase Day\'s High:**', purchase_information.High[0])


# Purchase price slider
individual_current = round(tickerDf.Close.iloc[-1],2)
price_df = tickerData.history(period = '1d', start = buy , end = today)
maximum = round(origin.High.max(),2)
minimum = round(origin.Low.min(),2)
individual_purchase = st.sidebar.slider('Select Purchase Price', float(minimum) , maximum)
quantity = st.sidebar.selectbox('Number of Shares', list(range(0,100)))

# Stock price information
total_purchase = round(individual_purchase * int(quantity),2)
total_current = round(tickerDf.Close.iloc[-1] * int(quantity),2)

# Providing information regarding stock performance 
st.write("Purchase Price:",individual_purchase)
st.write("Current Price:",individual_current)

# Function to calculate returns over time 
def investment_return(current, purchase):
    percent_return = round((current - purchase)/purchase * 100, 2)
    dollar_return = round(current - purchase,2)
    if current > purchase:
        st.write('Percentage Gain:', percent_return, '%')
    else:
        st.write('Percentage Loss:', percent_return, '%')
    st.write('Dollar Return: $', dollar_return)

investment_return(total_current,total_purchase)

# Plotting line graph of closing price
st.write('''### **Closing Price**''')
st.line_chart(tickerDf.Close)

# Plotting line graph of trading volume
st.write('''### **Trading Volume**''')
st.line_chart(tickerDf.Volume)

# Plotting candle stick charts
st.write('''### **Candle Stick Chart**''')

# Formatting our data for the candle stick
candle_df = tickerDf.reset_index()
for i in ['Open', 'High', 'Close', 'Low']:
    candle_df[i] = candle_df[i].astype('float64')

# Plotting our candle stick chart
candle = go.Figure(data = [go.Candlestick( x = candle_df['Date'], 
open = candle_df['Open'],
high = candle_df['High'],
low = candle_df['Low'],
close = candle_df['Close'])])

candle.update_layout(
    xaxis_title="Date",
    yaxis_title="Price ($)"
    )

st.plotly_chart(candle, use_container_width = True)

# Plotting line graph of dividends
st.write('''### **Dividends**''')
st.line_chart(tickerDf.Dividends)

# Displaying analysts' ratings 
st.write(''' ### **Analyst Ratings** ''')
st.write(tickerData.get_recommendations(proxy=None, as_dict=False)[::-1])

# Upcoming earnings calls
st.write(''' ### **Upcoming Dates** ''')
st.write(tickerData.calendar.transpose())

# Displaying next five option contracts
st.write('''### **Options**''')

# Filters for contracts
contract_type = st.selectbox('Contract Type', ['Call', 'Put'])
contract_filter = [0 if contract_type == 'Call' else 1][0]
expiration = st.selectbox('Expiration Date', list(i for i in tickerData.options))
in_the_money = st.selectbox( 'Filter ', ['In the Money', 'Out the Money'])
itm_filter = [True if in_the_money == 'In the Money' else False][0]

# Displaying options 
if st.button('Display'):
    df = tickerData.option_chain(expiration)[contract_filter]
    filters = (df['inTheMoney'] == itm_filter)
    df = df.loc[filters]
    df.drop(['inTheMoney', 'contractSize', 'currency'], axis = 1, inplace = True)
    st.dataframe(df)

