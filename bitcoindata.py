# -*- coding: utf-8 -*-
"""
Created on Fri Dec 22 09:26:34 2017

@author: DELL
"""
import os 
import numpy as np 
import pandas as pd 
import pickle 
import quandl 
from datetime import datetime

#导入Plotly来启用离线模式
import plotly.offline as py 
import plotly.plotly
import plotly.graph_objs as go 
import plotly.figure_factory as ff 
from scipy import * 

py.init_notebook_mode(connected=True)

#用Quandl的免费比特币接口来获得比特币的价格数据
#编写一个函数来下载和同步来自Quandl（https://www.quandl.com/ 号称金融数据界的维基百科）的数据。
def get_quandl_data(quandl_id):     
    '''Download and cache Quandl dataseries'''     
    cache_path = '{}.pkl'.format(quandl_id).replace('/','-')     
    try:         
        f = open(cache_path, 'rb')         
        df = pickle.load(f)    #用pickle来序列化，把下载的数据存成文件，这样代码就不会在每次运行的时候重新下载同样的数据    
        print('Loaded {} from cache'.format(quandl_id))     
    except (OSError, IOError) as e:         
        print('Downloading {} from Quandl'.format(quandl_id))         
        df = quandl.get(quandl_id, returns="pandas")         
        df.to_pickle(cache_path)         
        print('Cached {} at {}'.format(quandl_id, cache_path))     
    return df
#这个函数将返回Pandas数据框（Dataframe）格式的数据。
    

# Pull Kraken BTC price exchange data 获取Kraken比特币交易所的历史比特币汇率
btc_usd_price_kraken = get_quandl_data('BCHARTS/KRAKENUSD')
#用head()方法来查看数据框的前五行
btc_usd_price_kraken.head()

# Chart the BTC pricing data 做一个简单的图表，以此来快速地通过可视化的方法验证数据基本正确
btc_trace = go.Scatter(x=btc_usd_price_kraken.index, y=btc_usd_price_kraken['Weighted Price']) 
py.iplot([btc_trace])
#用Plotly 来完成可视化部分。它可以调用D3.js的充分交互式图表。这些图表有非常漂亮的默认设置，易于探索，而且非常方便嵌入到网页中。

# Pull pricing data for 3 more BTC exchanges 把各个交易所的数据下载到到由字典类型的数据框中
exchanges=['COINBASE','BITSTAMP','ITBIT']
exchange_data={}
exchange_data['KRAKEN']=btc_usd_price_kraken 
for exchange in exchanges:
    exchange_code='BCHARTS/{}USD'.format(exchange)
    btc_exchange_df=get_quandl_data(exchange_code)
    exchange_data[exchange]=btc_exchange_df

#定义一个简单的函数，把各个数据框中共有的列合并为一个新的组合数据框。
def merge_dfs_on_column(dataframes, labels, col):
    '''Merge a single column of each dataframe into a new combined dataframe'''
    series_dict={} 
    for index in range(len(dataframes)):
        series_dict[labels[index]]=dataframes[index][col]
    return pd.DataFrame(series_dict)
# Merge the BTC price dataseries' into a single dataframe基于各个数据集的“加权价格”列，把所有的数据框整合到一起。
btc_usd_datasets=merge_dfs_on_column(list(exchange_data.values()), list(exchange_data.keys()),'Weighted Price')
#使用“tail()”方法，查看合并后数据的最后五行，以确保数据整合成功。
btc_usd_datasets.tail() 

#定义一个辅助函数，通过提供单行命令使用数据制作图表。
def df_scatter(df, title,seperate_y_axis=False,y_axis_label='', scale='linear',initial_hide=False):
    '''Generate a scatter plot of the entire dataframe'''
    label_arr= list(df)
    series_arr= list(map(lambda col:df[col],label_arr)) 
    layout =go.Layout(title=title, legend=dict(orientation="h"), xaxis=dict(type='date'), yaxis=dict(title=y_axis_label, showticklabels=not seperate_y_axis, type=scale))
    y_axis_config=dict(overlaying='y', showticklabels=False, type=scale ) 
    
    visibility ='visible'
    if initial_hide: 
        visibility ='legendonly'
    
    # Form Trace For Each Series
    trace_arr=[]
    for index, series in enumerate(series_arr): 
        trace =go.Scatter(x=series.index, y=series, name=label_arr[index], visible=visibility)
        # Add seperate axis for the series
        
        if seperate_y_axis: 
            trace['yaxis']='y{}'.format(index +1) 
            layout['yaxis{}'.format(index +1)]=y_axis_config
        
        trace_arr.append(trace) 
    fig =go.Figure(data=trace_arr, layout=layout)
    plotly.offline.plot(fig)

# Plot all of the BTC exchange prices
df_scatter(btc_usd_datasets,'Bitcoin Price (USD) By Exchange')

# Remove "0" values比特币的价格从来没有等于零的时候，所以先去除数据框中所有的零值。
btc_usd_datasets.replace(0,np.nan,inplace=True)

# Plot the revised dataframe
df_scatter(btc_usd_datasets,'Bitcoin Price (USD) By Exchange')

# Calculate the average BTC price as a new column计算一个新的列：所有交易所的比特币日平均价格。
btc_usd_datasets['avg_btc_price_usd']=btc_usd_datasets.mean(axis=1)

# Plot the average BTC price
btc_trace=go.Scatter(x=btc_usd_datasets.index, y=btc_usd_datasets['avg_btc_price_usd'])
plotly.offline.plot([btc_trace])

#使用Poloniex API来获取数字加密货币交易的数据信息。定义函数get_json_data，它将从给定的URL中下载和缓存JSON数据。
def get_json_data(json_url,cache_path):
    '''Download and cache JSON data, return as a dataframe.'''
    try:                 
        f = open(cache_path,'rb')
        df=pickle.load(f)
        print('Loaded {} from cache'.format(json_url))
    except(OSError,IOError) as e:
        print('Downloading {}'.format(json_url))
        df=pd.read_json(json_url)
        df.to_pickle(cache_path)
        print('Cached {} at {}'.format(json_url,cache_path))
    return df

#定义一个新的函数，该函数将产生Poloniex API的HTTP请求，并调用刚刚定义的get_json_data函数，以保存调用的数据结果。
base_polo_url='https://poloniex.com/public?command=returnChartData&currencyPair={}&start={}&end={}&period={}'

start_date=datetime.strptime('2015-01-01','%Y-%m-%d')
# get data from the start of 2015
end_date=datetime.now()
# up until today
pediod=86400
# pull daily data (86,400 seconds per day)
def get_crypto_data(poloniex_pair):
    '''Retrieve cryptocurrency data from poloniex'''
    json_url=base_polo_url.format(poloniex_pair,start_date.timestamp(),end_date.timestamp(),pediod)
    data_df=get_json_data(json_url,poloniex_pair)
    data_df=data_df.set_index('date')
    return data_df
#下载9种排名靠前的加密货币交易数据：Ethereum，Litecoin，Ripple，Ethereum Classic，Stellar，Dash，Siacoin，Monero，和NEM。
altcoins=['ETH','LTC','XRP','ETC','STR','DASH','SC','XMR','XEM']
altcoin_data={} 
for altcoin in altcoins:
    coinpair='BTC_{}'.format(altcoin)
    crypto_price_df=get_crypto_data(coinpair)
    altcoin_data[altcoin]=crypto_price_df
#上述函数将抽取加密货币配对字符代码（比如“BTC_ETH”），并返回包含两种货币历史兑换汇率的数据框。
altcoin_data['ETH'].tail()

# Calculate USD Price as a new column in each altcoin dataframe 
#将BTC-山寨币汇率数据与我们的比特币价格指数结合，来直接计算每一个山寨币的历史价格（单位：美元），为每一个山寨币的数据框新增一列存储其相应的美元价格。。
for altcoin in altcoin_data.keys():     
    altcoin_data[altcoin]['price_usd'] =  altcoin_data[altcoin]['weightedAverage'] *btc_usd_datasets['avg_btc_price_usd']

# Merge USD price of each altcoin into single dataframe 重新使用之前定义的函数merge_dfs_on_column，来建立一个合并的数据框，整合每种电子货币的美元价格。  
combined_df = merge_dfs_on_column(list(altcoin_data.values()), list(altcoin_data.keys()), 'price_usd')

# Add BTC price to the dataframe 把比特币价格作为最后一栏添加到合并后的数据框中。
combined_df['BTC'] = btc_usd_datasets['avg_btc_price_usd']

# Chart all of the altocoin prices 重新调用之前的函数df_scatter，以图表形式展现全部山寨币的相应价格。
df_scatter(combined_df, 'Cryptocurrency Prices (USD)', seperate_y_axis=False, y_axis_label='Coin Value (USD)', scale='log')
#使用了对数规格的y轴，在同一绘图上比较所有货币。可以尝试其他不同的参数值(例如scale='linear')

# Calculate the pearson correlation coefficients for cryptocurrencies in 2016 计算2016年的相关系数。 
combined_df_2016 = combined_df[combined_df.index.year == 2016] 
combined_df_2016.pct_change().corr(method='pearson')
#使用pct_change()方法，将数据框中的每一个的价格绝对值转化为相应的日回报率。

#创建一个新的可视化的帮助函数
def correlation_heatmap(df, title, absolute_bounds=True):     
    '''Plot a correlation heatmap for the entire dataframe'''     
    heatmap = go.Heatmap(z=df.corr(method='pearson').as_matrix(), x=df.columns, y=df.columns, colorbar=dict(title='Pearson Coefficient'), )          
    layout = go.Layout(title=title)          
    if absolute_bounds: 
        heatmap['zmax'] = 1.0         
        heatmap['zmin'] = -1.0              
        fig = go.Figure(data=[heatmap], layout=layout)     
        plotly.offline.plot(fig) 

correlation_heatmap(combined_df_2016.pct_change(), "Cryptocurrency Correlations in 2016")
#深红色的数值代表强相关性(每一种货币显然是与其自身高度相关的)，深蓝色的数值表示强逆相关性。
#所有介于中间的颜色-浅蓝/橙/灰/茶色-其数值代表不同程度的弱相关或不相关。

#使用从2017年开始的数据来重复同样的测试验证假设-电子货币在近几个月的相关性增强。
combined_df_2017 = combined_df[combined_df.index.year == 2017] 
combined_df_2017.pct_change().corr(method='pearson')

correlation_heatmap(combined_df_2017.pct_change(), "Cryptocurrency Correlations in 2017")
