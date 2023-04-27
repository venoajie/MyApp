from market_understanding.MP import MpFunctions
import requests
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import pandas as pd
import datetime as dt
import numpy as np
import warnings
from loguru import logger as log
warnings.filterwarnings('ignore')

app = dash.Dash(__name__)

def get_ticksize(data, freq=30):
    # data = dflive30
    numlen = int(len(data) / 2)
    # sample size for calculating ticksize = 50% of most recent data
    tztail = data.tail(numlen).copy()
    tztail['tz'] = tztail.Close.rolling(freq).std()  # std. dev of 30 period rolling
    tztail = tztail.dropna()
    ticksize = np.ceil(tztail['tz'].mean() * 0.25)  # 1/4 th of mean std. dev is our ticksize

    if ticksize < 0.2:
        ticksize = 0.2  # minimum ticksize limit

    return int(ticksize)

def get_data(url):
    """
    :param url: binance url
    :return: ohlcv dataframe
    """
    response = requests.get(url)
    data = response.json()
    df = pd.DataFrame(data)
    df = df.apply(pd.to_numeric)
    df[0] = pd.to_datetime(df[0], unit='ms')
    df = df[[0, 1, 2, 3, 4, 5]]
    df.columns = ['datetime', 'Open', 'High', 'Low', 'Close', 'volume']
    df = df.set_index('datetime', inplace=False, drop=False)
    return df

url_30m = "https://www.binance.com/api/v1/klines?symbol=ETHBUSD&interval=30m"  # 10 days history 30 min ohlcv
df = get_data(url_30m)
df.to_csv('ethusd30m.csv', index=False)

# params
context_days = len([group[1] for group in df.groupby(df.index.date)])  # Number of days used for context
freq = 2  # for 1 min bar use 30 min frequency for each TPO, here we fetch default 30 min bars server
avglen = context_days - 2  # num days to calculate average values
mode = 'tpo'  # for volume --> 'vol'
trading_hr = 24  # Default for BTC USD or Forex
day_back = 0  # -1 While testing sometimes maybe you don't want current days data then use -1
# ticksz = 28 # If you want to use manual tick size then uncomment this. Really small number means convoluted alphabets (TPO)
ticksz = (get_ticksize(df.copy(), freq=freq))*2  # Algorithm will calculate the optimal tick size based on volatility
textsize = 10

dfnflist = [group[1] for group in df.groupby(df.index.date)]  #

dates = []
for d in range(0, len(dfnflist)):
    dates.append(dfnflist[d].index[0])

date_time_close = dt.datetime.today().strftime('%Y-%m-%d') + ' ' + '23:59:59'
append_dt = pd.Timestamp(date_time_close)
dates.append(append_dt)
date_mark = {str(h): {'label': str(h), 'style': {'color': 'blue', 'fontsize': '4',
                                                 'text-orientation': 'upright'}} for h in range(0, len(dates))}

mp = MpFunctions(data=df.copy(), freq=freq, style=mode, avglen=avglen, ticksize=ticksz, session_hr=trading_hr)
mplist = mp.get_context()

app.layout = html.Div(
    html.Div([
        dcc.Location(id='url', refresh=False),
        html.Br(),
        dcc.Interval(
            id='interval-component',
            interval=5 * 1000,  # Reduce the time if you want frequent updates 5000 = 5 sec
            n_intervals=0
        ),
        html.P([
            html.Label("Time Period"),
            dcc.RangeSlider(id='slider',
                            pushable=1,
                            marks=date_mark,
                            min=0,
                            max=len(dates),
                            step=None,
                            value=[len(dates) - 2, len(dates) - 1])
        ], style={'width': '80%',
                  'fontSize': '14px',
                  'padding-left': '100px',
                  'display': 'inline-block'})
    ])
)

@app.callback(Output(component_id='beinghorizontal', component_property='figure'),
              [Input('interval-component', 'n_intervals'),
               Input('slider', 'value')
               ])
def update_graph(n, value):
    listmp_hist = mplist[0]
    distribution_hist = mplist[1]

    url_1m = "https://www.binance.com/api/v1/klines?symbol=ETHBUSD&interval=1m"

    df_live1 = get_data(url_1m)  # this line fetches new data for current day
    df_live1 = df_live1.dropna()

    dflive30 = df_live1.resample('30min').agg({'datetime': 'last', 'Open': 'first', 'High': 'max', 'Low': 'min',
                                               'Close': 'last', 'volume': 'sum'})
    df2 = pd.concat([df, dflive30])
    df2 = df2.drop_duplicates('datetime')

    ticksz_live = (get_ticksize(dflive30.copy(), freq=2))
    mplive = MpFunctions(data=dflive30.copy(), freq=freq, style=mode, avglen=avglen, ticksize=ticksz_live,
                         session_hr=trading_hr)

    mplist_live = mplive.get_context()

    listmp_live = mplist_live[0]  # it will be in list format so take [0] slice for current day MP data frame
    df_distribution_live = mplist_live[1]
    df_distribution_concat = pd.concat([distribution_hist, df_distribution_live], axis=0)
    df_distribution_concat = df_distribution_concat.reset_index(inplace=False, drop=True)

    df_updated_rank = mp.get_dayrank()
    ranking = df_updated_rank[0]
    breakdown = df_updated_rank[1]

    listmp = listmp_hist + listmp_live

    DFList = [group[1] for group in df2.groupby(df2.index.date)]
    
    for inc in range(value[1] - value[0]):
        i = value[0]
        # inc = 0 # for debug
        # i = value[0]

        i += inc
        df1 = DFList[i].copy()
        df_mp = listmp[i]
        irank = ranking.iloc[i]  # select single row from ranking df
        df_mp['i_date'] = df1['datetime'][0]
        # # @todo: background color for text
        df_mp['color'] = np.where(np.logical_and(
            df_mp['close'] > irank.vallist, df_mp['close'] < irank.vahlist), 'green', 'white')

        df_mp = df_mp.set_index('i_date', inplace=False)

        brk_f_list_maj = []
        #log. (f'breakdown.columns {breakdown.columns}')
        f = 0
        for f in range(len(breakdown.columns)):
            brk_f_list_min = []
            for index, rows in breakdown.iterrows():
                if rows[f] != 0:
                    brk_f_list_min.append(index + str(': ') + str(rows[f]) + '<br />')
            brk_f_list_maj.append(brk_f_list_min)

        log.debug (f' irank {irank}')

if __name__ == '__main__':
    app.run_server(port=8000, host='127.0.0.1',
                   debug=True)  # debug=False if executing from ipython(vscode/Pycharm/Spyder)
