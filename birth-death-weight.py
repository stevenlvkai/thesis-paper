# -*- coding: utf-8 -*-
"""
Created on Thu Apr 19 11:15:59 2018

@author: 凯
利用山寨币与比特币的比值计算比特币的增发
"""

from random import expovariate
import matplotlib.pyplot as plt
from datetime import datetime
import pandas as pd
import numpy as np  

from datetime import timedelta

#到达过程
def birth(average_arrival_interval):
    
    #日期
    d1=[]
    birthnum = []
    arrival = 0.0
    
    for i in range(150):
        
        #泊松过程的时间间隔为参数为λ的指数分布，假设每天发生一次参数为1
        a=expovariate(1.0 / average_arrival_interval)
        #平均每*天产生1次分叉
        arrival += a
        
        birthnum.append(1)
        
        t=datetime(2017, 8, 1, 0, 0, 0)+timedelta(days=arrival)
        t=datetime.strftime(t,'%Y-%m-%d')#去除小时、分钟、秒，只留下年月日，方便之后比较秒
        t=datetime.strptime(t,'%Y-%m-%d')
        d1.append(t)
    return birthnum, d1
#离去过程
def death(average_leave_interval):
    
    #日期
    d2=[]
    deathnum = []
    arrival = 0.0
    
    for i in range(150):
        
        #泊松过程的时间间隔为参数为λ的指数分布，假设每天发生一次参数为1
        a=expovariate(1.0 / average_leave_interval)
        #平均每*天产生1次分叉
        arrival += a
        
        deathnum.append(-1)
        
        t=datetime(2017, 9, 1, 0, 0, 0)+timedelta(days=arrival)
        t=datetime.strftime(t,'%Y-%m-%d')#去除小时、分钟、秒，只留下年月日，方便之后比较秒
        t=datetime.strptime(t,'%Y-%m-%d')
        d2.append(t)    
    return deathnum, d2
#统一到达与离去过程
def birth_death(average_arrival_interval, average_leave_interval):
    birth1, date1 = birth(average_arrival_interval)
    death1, date2 = death(average_leave_interval)
    
    event= birth1 + death1
    date = date1 + date2
    
    data=pd.DataFrame()
    data['event']=event
    data['time'] = date
    data=data.sort_values(by = 'time',ascending = True)#排序，使得到达与离去按时间顺序排列
    data = data.set_index('time')
    '''
    num=[]
    for i in range(len(data['event'])):
        e=sum(data['event'].head(i))
        num.append(e)
    data['wait_num']=num#累加，计算每个时刻的山寨币数量
    '''    
    for m in range(len(data['event'])):#去除被排列到最后的大量离去事件
        if data['event'][-m-1] != data['event'][-m-2]:
            n=-m-1
            break
    data.drop(data.index[range(300+n,300)],inplace=True)
    
    num=[]
    for i in range(len(data['event'])):
        e=sum(data['event'].head(i))
        num.append(e)
    data['wait_num']=num
    
    #计算每个山寨币相对与比特币的价格    
    weight=[]
    for i in range(len(data['wait_num'])):
        if i==0:
            weight.append(-0.008*np.log(i+0.0001) + 0.0491)#价格公式
        elif i>0 and i<3:#延迟两次分叉的时间才迎来第二次分叉
            weight.append(0)
        else:
            if data['event'][i-2]>0:
                weight.append(-0.008*np.log(i-2+0.0001) + 0.0491)
            else:
                weight.append(0.008*np.log(i-2+0.0001) - 0.0491)
    data['weight']=weight
    #计算每个时刻累计的山寨币价格
    weight_sum=[]
    for i in range(len(data['event'])):
        w=sum(data['weight'].head(i+1))
        weight_sum.append(w)
    data['weight_sum']=weight_sum#现存的所有山寨币加起来的价值
    return data

if __name__=="__main__":
    import time
    start_time=time.time()#计时
    average1=[]
    average2=[]
    average3=[]
    #计算2017、2018、2019年年底的累计山寨币价格
    for j in range(100):                
        avg1=0
        avg2=0
        avg3=0
        for i in range(100):    
            data  = birth_death(7,j+7)
            a1=data['2017']['weight_sum'].tail(1).values[0]
            a2=data['2018']['weight_sum'].tail(1).values[0]
            a3=data['2019']['weight_sum'].tail(1).values[0]
            avg1=i*avg1/(i+1)+a1/(i+1)
            avg2=i*avg2/(i+1)+a2/(i+1)
            avg3=i*avg3/(i+1)+a3/(i+1)
        average1.append(avg1)
        average2.append(avg2)
        average3.append(avg3)
    inflation=pd.DataFrame()
    inflation['2017']=average1
    inflation['2018']=average2
    inflation['2019']=average3
    end_time=time.time()
    time_elapsed=end_time-start_time #in seconds
    print(time_elapsed)
    #画图
    t=range(7,107)
    a, =plt.plot(t,inflation['2017'])
    b, =plt.plot(t,inflation['2018'])
    c, =plt.plot(t,inflation['2019'])
    plt.legend(handles = [a, b, c], labels = ['2017', '2018', '2019'], loc = 'best')
    plt.show()
