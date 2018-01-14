# -*- coding: utf-8 -*-
"""
Created on Sat Dec 23 13:22:07 2017
用于提取比特币及其他山寨币的价格、成交量等数据
@author: 凯
"""

import os 
import numpy as np 
import pandas as pd 
import pickle 
import quandl 
from datetime import datetime


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

btc_usd_volumes=merge_dfs_on_column(list(exchange_data.values()), list(exchange_data.keys()),'Volume (Currency)')


# Calculate the average BTC price as a new column计算一个新的列：所有交易所的比特币日平均价格。
btc_usd_datasets['avg_btc_price_usd']=btc_usd_datasets.mean(axis=1)

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

#提取bitcoincash的价格数据
cash=get_crypto_data('BTC_BCH')
cash['price_usd']=cash['weightedAverage'] *btc_usd_datasets['avg_btc_price_usd']
c=cash['price_usd']
writer = pd.ExcelWriter('D:\\output4.xlsx')
c.to_excel(writer,'Sheet1')
writer.save()

# Merge USD price of each altcoin into single dataframe 重新使用之前定义的函数merge_dfs_on_column，来建立一个合并的数据框，整合每种电子货币的美元价格。  
combined_df = merge_dfs_on_column(list(altcoin_data.values()), list(altcoin_data.keys()), 'price_usd')

# Add BTC price to the dataframe 把比特币价格作为最后一栏添加到合并后的数据框中。
combined_df['BTC'] = btc_usd_datasets['avg_btc_price_usd']

# Calculate the pearson correlation coefficients for cryptocurrencies in 2016 计算2016年的相关系数。 
combined_df_2016 = combined_df[combined_df.index.year == 2016] 
combined_df_2016.pct_change().corr(method='pearson')
#使用pct_change()方法，将数据框中的每一个的价格绝对值转化为相应的日回报率。

#使用从2017年开始的数据来重复同样的测试验证假设-电子货币在近几个月的相关性增强。
combined_df_2017 = combined_df[combined_df.index.year == 2017] 
combined_df_2017.pct_change().corr(method='pearson')

#输出bitcoin价格数据
writer = pd.ExcelWriter('D:\\output.xlsx')
btc_usd_datasets.to_excel(writer,'Sheet1')
writer.save()
b=pd.DataFrame()
#输出bitstamp交易所成交量数据
a=btc_usd_volumes['BITSTAMP']
writer = pd.ExcelWriter('D:\\output3.xlsx')
btc_usd_volumes.to_excel(writer,'Sheet1')
writer.save()
