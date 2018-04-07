# -*- coding: utf-8 -*-
"""
Created on Wed Mar 28 11:17:19 2018

@author: 凯

通过泊松过程模拟比特币发行过程
假设数据从2009/1/3到2018/3/16
实际上泊松过程的模拟偷懒了
"""

from random import expovariate
import matplotlib.pyplot as plt
from datetime import datetime
import pandas as pd
import xlrd
import numpy as np  
from astropy.units import Ybarn  
import math  

#λ强度为1
average_arrival_interval = 1

#日期
d=pd.date_range('20090103','20180313')

num_waiting = 0

arrivals = []
bitcoinnum = []
arrival = 0.0
bitcoin=0

for i in range(3357):
    num_waiting += 1
    
    #泊松过程的时间间隔为参数为λ的指数分布，假设每天发生一次参数为1
    a=expovariate(1.0 / average_arrival_interval)
    
    #平均每10分钟产生1个块，既每天144个
    arrival += a*144
    arrivals.append(arrival)
    
    #区块链每210000个产生的bitcoin奖励减半，从每块50个到25到12.5个，以此类推
    if arrival <=210000:
        bitcoin += a*144*50
        bitcoinnum.append(bitcoin)
    elif arrival <=420000:
        bitcoin += a*144*25
        bitcoinnum.append(bitcoin)
    else:
        bitcoin += a*144*12.5
        bitcoinnum.append(bitcoin)

data=pd.DataFrame()
data['simulate_number']=bitcoinnum
data['date']=d
data = data.set_index('date')


#读取比特币区块数据
data1 = xlrd.open_workbook('D:\\吕凯\\中央财经大学\\毕业论文\\泊松过程\\actualdata.xlsx')
table = data1.sheets()[0] 
height=pd.DataFrame()
height[0]=table.col_values(0)
height[1]=table.col_values(1)
height.columns=[table.col_values(0)[0],table.col_values(1)[0]]
height=height.drop([0])
#转换日期格式
nrows=height.shape[0]
timelist=[]
for i in range(nrows):
    x=xlrd.xldate_as_tuple(table.cell(i+1,0).value,0)
    date = datetime(*x)
    date=date.strftime('%Y/%m/%d')
    timelist.append(date)
  
height[table.col_values(0)[0]]=timelist
height=height.set_index('date')
height.index = pd.to_datetime(height.index)#日期索引

#合并由泊松过程估计出来的数据和实际数据
data['actual_number']=height['actual']

'''
#输出bitcoin数量数据
writer = pd.ExcelWriter('D:\\吕凯\\中央财经大学\\毕业论文\\泊松过程\\data.xlsx')
data.to_excel(writer,'Sheet1')
m.to_excel(writer,'Sheet2')
writer.save()
'''
#计算R方，即残差平方和
def computeCorrelation(X, Y):  
    xBar = np.mean(X)  
    yBar = np.mean(Y)  
    SSR = 0  
    varX = 0  
    varY = 0  
    for i in range(0 , len(X)):  
        diffXXBar = X[i] - xBar  
        diffYYBar = Y[i] - yBar  
        SSR += (diffXXBar * diffYYBar)  
        varX +=  diffXXBar**2  
        varY += diffYYBar**2  

    SST = math.sqrt(varX * varY)  
    return SSR / SST

print(computeCorrelation(data['simulate_number'],data['actual_number']))

data.plot()

