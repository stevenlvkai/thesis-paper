# -*- coding: utf-8 -*-
"""
Created on Wed Apr 11 20:40:36 2018

@author: 凯
"""

from random import expovariate
import matplotlib.pyplot as plt
from datetime import datetime
import pandas as pd
import numpy as np  
#import math  

from datetime import timedelta
#import xlrd

from mpl_toolkits.mplot3d import Axes3D

from matplotlib import cm

def birth(average_arrival_interval):
    
    #日期
    d1=[]
    arrivals = []
    bitcoinfork = []
    arrival = 0.0
    fork=0
    
    for i in range(300):
        
        #泊松过程的时间间隔为参数为λ的指数分布，假设每天发生一次参数为1
        a=expovariate(1.0 / average_arrival_interval)
        #平均每*天产生1次分叉
        arrival += a
        arrivals.append(arrival)
        
        fork += 1
        bitcoinfork.append(fork)
        
        t=datetime(2017, 8, 1, 0, 0, 0)+timedelta(days=arrival)
        t=datetime.strftime(t,'%Y-%m-%d')#去除小时、分钟、秒，只留下年月日，方便之后比较秒
        t=datetime.strptime(t,'%Y-%m-%d')
        d1.append(t)
    #只取每天最后一个数据作为每天的结果
    new_date = []
    #new_date1=[]
    new_num = []
    for i in range(len(d1)):
        if i == len(d1) - 1 or d1[i + 1] > d1[i]:  # change to m[i + 1, 0] > m[i, 0]
            new_num.append(bitcoinfork[i])
            new_date.append(d1[i])
            #new_date1.append(datetime.strftime(d1[i],'%Y-%m-%d'))
    
    #准备合并观测值和估计值，估计值缺失的数据用后一天的数据填充
    j=0
    s=[]
    for i in range(len(data['date'])):
        if data['date'][i] <= new_date[j]:
            s.append(new_num[j])
        else :   
            data['date'][i] > new_date[j]
            j=j+1
            s.append(new_num[j]) 
    
    return s
def death(average_arrival_interval):
    
    #日期
    d1=[]
    arrivals = []
    bitcoinfork = []
    arrival = 0.0
    fork=0
    
    for i in range(300):
        
        #泊松过程的时间间隔为参数为λ的指数分布，假设每天发生一次参数为1
        a=expovariate(1.0 / average_arrival_interval)
        #平均每*天产生1次分叉
        arrival += a
        arrivals.append(arrival)
        
        fork += -1
        bitcoinfork.append(fork)
        
        t=datetime(2017, 10, 1, 0, 0, 0)+timedelta(days=arrival)
        t=datetime.strftime(t,'%Y-%m-%d')#去除小时、分钟、秒，只留下年月日，方便之后比较秒
        t=datetime.strptime(t,'%Y-%m-%d')
        d1.append(t)
    #只取每天最后一个数据作为每天的结果
    new_date = []
    #new_date1=[]
    new_num = [0]
    for i in range(len(d1)):
        if i == len(d1) - 1 or d1[i + 1] > d1[i]:  # change to m[i + 1, 0] > m[i, 0]
            new_num.append(bitcoinfork[i])
            new_date.append(d1[i])
            #new_date1.append(datetime.strftime(d1[i],'%Y-%m-%d'))
    
    #准备合并观测值和估计值，估计值缺失的数据用后一天的数据填充
    j=0
    e=[]
    for i in range(len(data['date'])):
        if data['date'][i] <= new_date[j]:
            e.append(new_num[j])
        else :   
            data['date'][i] > new_date[j]
            j=j+1
            e.append(new_num[j]) 
    
    return e
    
if __name__=="__main__":
    import time
    start_time=time.time()#计时
    avg=0
    average=[]
    data=pd.DataFrame()
    date=pd.date_range(start='20170801',periods=1000,freq='1D') #生成日期序列作为index  
    data['date']=date
    
    for j in range(30):                
        for i in range(100):    
            b=birth(7)
            d=death(j+7)#指不同的服务率
            
            #data['birth']=b
            #data['death']=d
            #data['remain']=data['birth']+data['death']
            #last=data['remain'].iloc[-1]
            #太慢了
            
            b_array = np.array(b)
            d_array = np.array(d)
            remain = b_array + d_array
            last = remain[-1]
            avg=i*avg/(i+1)+last/(i+1)#每种服务率对应的2020年还存在的山寨币的平均数
        k='{s}'.format(s=j+7)
        data[k]=remain
        average.append(avg)
    data = data.set_index('date')
    end_time=time.time()
    time_elapsed=end_time-start_time #in seconds
    print(time_elapsed)
    print(average)
    
    fig = plt.figure()
    ax = fig.gca(projection='3d')
    coefficient=np.arange(7,37,1)
    time=np.arange(0,1000,1)
    time, coefficient = np.meshgrid(time, coefficient)
    Z=data.values
    Z=np.transpose(Z)
    surf = ax.plot_surface(time, coefficient, Z, cmap=cm.coolwarm,
                           linewidth=0, antialiased=False)
    
    xticks = range(0,1200,200)#更换坐标轴的刻度
    xticklabels = ['2017-08-01','2018-02-17','2018-09-05','2019-03-24','2019-10-10','2020-04-26']    
    ax.set_xticks(xticks)
    ax.set_xticklabels(xticklabels,rotation=15)
    
    fig.colorbar(surf, shrink=1, aspect=10)
    fig.set_size_inches(18.5,10.5)    
    fig.savefig('D:\吕凯\中央财经大学\毕业论文\生灭过程\power.png', dpi=150)