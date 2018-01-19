# -*- coding: utf-8 -*-
"""
Created on Fri Jan 19 10:42:44 2018

@author: DELL
"""

import xlrd
import pandas as pd
from datetime import datetime
import matplotlib.pyplot as plt
import statsmodels.api as sm
import numpy as np
#数据读取
data = xlrd.open_workbook('D:\\中粮期货-吕凯\\毕业论文\\capratio.xlsx')
table = data.sheet_by_name(u'Sheet3')
capratio=pd.DataFrame()
capratio[0]=table.col_values(0)
capratio[1]=table.col_values(1)
capratio[2]=table.col_values(2)
capratio[3]=table.col_values(3)
capratio.columns=[table.col_values(0)[0],table.col_values(1)[0],table.col_values(2)[0],table.col_values(3)[0]]
capratio=capratio.drop([0])
#日期转换
nrows=capratio.shape[0]
timelist=[]
for i in range(nrows):
    x=xlrd.xldate_as_tuple(table.cell(i+1,0).value,0)
    date = datetime(*x)
    date=date.strftime('%Y/%m/%d')
    timelist.append(date)   
capratio[table.col_values(0)[0]]=timelist
capratio=capratio.set_index('Date')
capratio.index = pd.to_datetime(capratio.index)#日期索引
#相关系数
pct=capratio.pct_change()
month=['2017/08','2017/09','2017/10','2017/11','2017/12','2018/01']
n=len(month)
corr=pd.DataFrame()
corr.columes=['month','Bitcoincash','Cap Ratio']
b=[]
c=[]
for i in range(n):
    a=pct[month[i]].corr()
    b.append(a['Bitcoin'][0])
    c.append(a['Bitcoin'][2])
corr['month']=month
corr['Bitcoincash']=b
corr['Cap Ratio']=c
corr=corr.set_index('month')
plt.plot(corr.index,corr['Bitcoincash'],corr.index,corr['Cap Ratio'],'r')
#回归

