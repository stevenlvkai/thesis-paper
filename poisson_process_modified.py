# -*- coding: utf-8 -*-
"""
Created on Sat Apr  7 16:43:37 2018

@author: 凯
"""

from random import expovariate
#import matplotlib.pyplot as plt
from datetime import datetime
import pandas as pd
import numpy as np  
#import math  
#import matplotlib.pyplot as plt  
from datetime import timedelta
import xlrd

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
    date=datetime.strptime(date,'%Y/%m/%d')
    timelist.append(date)
  
height[table.col_values(0)[0]]=timelist
height=height.set_index('date')

#进行poisson过程模拟
def poisson(first,second,third):
    #λ强度为1
    average_arrival_interval = 1
    
    #日期
    d1=[]
    
    num_waiting = 0
    
    arrivals = []
    bitcoinnum = []
    arrival = 0.0
    bitcoin=0
    
    for i in range(5000):
        num_waiting += 144
        
        #泊松过程的时间间隔为参数为λ的指数分布，假设每天发生一次参数为1
        a=expovariate(1.0 / average_arrival_interval)
        
        #平均每10分钟产生1个块，既每天144个
        arrival += a
        arrivals.append(arrival)
        
        #区块链每210000个产生的bitcoin奖励减半，从每块50个到25到12.5个，以此类推
        if num_waiting <=210000:
            bitcoin += 144*first
            bitcoinnum.append(bitcoin)
        elif num_waiting <=420000:
            bitcoin += 144*second
            bitcoinnum.append(bitcoin)
        else:
            bitcoin += 144*third
            bitcoinnum.append(bitcoin)
        
        t=datetime(2009, 1, 3, 0, 0, 0)+timedelta(days=arrival)
        t=datetime.strftime(t,'%Y-%m-%d')#去除小时、分钟、秒，只留下年月日，方便之后比较秒
        t=datetime.strptime(t,'%Y-%m-%d')
        d1.append(t)
        if t>=datetime(2018, 3, 13, 0, 0, 0):
            #n=i
            break
    #只取每天最后一个数据作为每天的结果
    new_date = []
    new_num = []
    for i in range(len(d1)):
        if i == len(d1) - 1 or d1[i + 1] > d1[i]:  # change to m[i + 1, 0] > m[i, 0]
            new_num.append(bitcoinnum[i])
            new_date.append(d1[i])
    data=pd.DataFrame()
    data['simulate']=new_num
    data['date']=new_date
    data = data.set_index('date')
    
    #准备合并观测值和估计值，估计值缺失的数据用后一天的数据填充
    j=0
    s=[]
    for i in range(len(height['actual'])):
        if height.index[i] <= data.index[j]:
            s.append(data['simulate'][j])
        else :
            j=j+1
            s.append(data['simulate'][j])
    
    height['simulate']=s    
    return height

#计算R-square
def computeRsquare(X, Y):  
    yBar = np.mean(Y)  
    '''SSE = 0  
    SST = 0  
    for i in range(0 , len(X)):  
        diffXyBar = X[i] - Y[i]  
        diffYyBar = Y[i] - yBar  
        SST +=  diffYyBar**2 
        SSE +=  diffXyBar**2  
        '''
    SSE=np.sum((X-Y)**2)
    SST=np.sum((Y-yBar)**2)
    return 1-SSE/SST

if __name__=="__main__":
    import time
    start_time=time.time()#计时
    rscore=[]
    for i in range(10):#观察哪个参数能得到最优的R-square
        rsq=[]
        for j in range(100):
            da=poisson(52,24.5+i/10,12.5)
            #rs=performance_metric(da['actual_number'],da['simulate_number'])
            rs=computeRsquare(da['simulate'],da['actual'])
            rsq.append(rs)
        rsc=sum(rsq)/len(rsq)
        rscore.append(rsc)
    end_time=time.time()
    time_elapsed=end_time-start_time #in seconds
    print(time_elapsed)
    print(rscore)
