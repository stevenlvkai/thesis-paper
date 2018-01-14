# -*- coding: utf-8 -*-
"""
Created on Tue Jan  9 22:45:29 2018
用于读取比特币区块高度、奖励、难度等数据
@author: 凯
"""

import xlrd
import pandas as pd
from datetime import datetime
import matplotlib.pylab as plt
#读取数据
data = xlrd.open_workbook('D:\\吕凯\\中央财经大学\\毕业论文\\height.xlsx')
table = data.sheet_by_name(u'Sheet1')
height=pd.DataFrame()
height[0]=table.col_values(0)
height[1]=table.col_values(3)
#height[2]=table.col_values(4)
height[3]=table.col_values(5)
height.columns=[table.col_values(0)[0],table.col_values(3)[0],table.col_values(5)[0]]
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

#单位换算
a=[]
for i in range(nrows):
    a.append(height['output_total'][i]/100000000)
height['output_total1']=a

#每个间隔生产几个区块
block_produce=[0]
for i in range(nrows-1):
    number=height['id'][i+1]-height['id'][i]
    block_produce.append(number)

height['block_produce']=block_produce

#每个间隔生产几个比特币
bitcoin_produce=[0]
for i in range(nrows-1):
    number=height['output_total1'][i]*height['block_produce'][i+1]
    bitcoin_produce.append(number)

height['bitcoin_produce']=bitcoin_produce

#流通中的比特币数量
bitcoin_total=[0]
for i in range(nrows-1):
    number=bitcoin_total[i]+height['bitcoin_produce'][i+1]
    bitcoin_total.append(number)

height['bitcoin_total']=bitcoin_total

#输出难度数据
b=pd.DataFrame()
b['difficulty']=height['difficulty']
writer = pd.ExcelWriter('D:\\output1.xlsx')
b.to_excel(writer,'Sheet1')
writer.save()
