# -*- coding: utf-8 -*-
"""
Created on Tue Jan  9 22:45:29 2018

@author: 凯
"""

import xlrd
import pandas as pd
from datetime import datetime
import matplotlib.pylab as plt
#读取数据
data = xlrd.open_workbook('D:\\中粮期货-吕凯\\毕业论文\\height.xlsx')
table = data.sheet_by_name(u'Sheet1')
height=pd.DataFrame()
height[0]=table.col_values(0)
height[2]=table.col_values(5)
height.columns=[table.col_values(0)[0],table.col_values(5)[0]]
height=height.drop([0])

#转换日期格式
nrows=height.shape[0]
timelist=[]
for i in range(nrows):
    x=xlrd.xldate_as_tuple(table.cell(i+1,2).value,0)
    date = datetime(*x)
    date=date.strftime('%Y/%m/%d %H:%M:%S')
    timelist.append(date)
    
height[table.col_values(2)[0]]=timelist
height=height.set_index('time')
height.index = pd.to_datetime(height.index)#日期索引

height=height.sort_index(axis=0, by=None, ascending=True)#升序排列

#每个间隔生产几个区块
block_produce=[0]
for i in range(nrows-1):
    number=height['id'][i+1]-height['id'][i]
    block_produce.append(number)

height['block_produce']=block_produce

#每个间隔生产几个比特币
bitcoin_produce=[]
for i in range(nrows):
    number=height['output_total'][i]*height['block_produce'][i+1]
    bitcoin_produce.append(number)

height['bitcoin_produce']=bitcoin_produce

#流通中的比特币数量
bitcoin_total=[0]
for i in range(nrows-1):
    number=bitcoin_total[i]+height['bitcoin_produce'][i+1]
    bitcoin_total.append(number)

height['bitcoin_total']=bitcoin_total
