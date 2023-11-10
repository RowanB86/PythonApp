# -*- coding: utf-8 -*-
"""
Created on Thu Nov  9 09:13:27 2023

@author: RowanBarua
"""

import streamlit as st
import numpy as np
from scipy import stats
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib import rcParams
import random
rcParams.update({'figure.autolayout': True})

class KDEDist(stats.rv_continuous):
    
    def __init__(self, kde, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._kde = kde
    
    def _pdf(self, x):
        return self._kde.pdf(x)

st.title('Max Stock Holding / Re-Order Point Estimation')

Chart_Types = ['PDF','CDF']
Distributions = ['Poisson','Normal']

st.header('Lead Time Modelling')
LTDist = st.selectbox('Select Distribution',Distributions,key="LTDist")

if LTDist == 'Normal':
    try:
        LTMean = float(st.text_input("Enter Lead Time Mean:",key="LTMean"))
        LTStDev = float(st.text_input("Enter Lead Time Standard Deviation:",key="LTStDev"))
        data = np.random.normal(LTMean, LTStDev, 1000)
        st.session_state.LTMean = LTMean
        st.session_state.LTStDev = LTStDev
    except:
        pass
else:
    try:
        LTMean = float(st.text_input("Enter Lead Time Mean:",key="LTMean"))
        data = np.random.poisson(LTMean, 1000)
        st.session_state.LTMean = LTMean
    except:
        pass

LTChart = st.selectbox('Select Chart Type',Chart_Types,key="LTChart")
LTChartButton = st.button("Generate Chart",key="LTChartButton")

if LTChartButton:
    
    st.session_state.LTData = data
    kde = stats.gaussian_kde(data)
    X = KDEDist(kde)
    inc = 1
    x = np.arange(0, max(data), inc)
    fig, axe = plt.subplots() 
    fig.set_tight_layout(True)
    ax2 = axe.twinx() 
    pdfVals = X.pdf(x)
    cdfVals = X.cdf(x)
    
    
    if LTChart == 'PDF':
        ax2.plot(x, X.pdf(x),color='r',label='PDF')
        plt.title("PDF of Lead Time")
    else:
        ax2.plot(x, X.cdf(x),color='r',label='CDF')
        plt.title("CDF of Lead Time")
    
    st.plotly_chart(fig)
    


st.header('Usage Modelling')
UsageDist = st.selectbox('Select Distribution',Distributions,key="UsageDist")

if UsageDist == 'Normal':
    try:
        UsageMean = float(st.text_input("Enter Usage Mean:",key="UsageMean"))
        UsageStDev = float(st.text_input("Enter Usage Standard Deviation:",key="USageStDev"))
        data = np.random.normal(UsageMean, UsageStDev, 1000)
        st.session_state.UsageMean = UsageMean
        st.session_state.UsageStDev = UsageStDev
    except:
        pass
else:
    try:
        UsageMean = float(st.text_input("Enter Usage Mean:",key="UsageMean"))
        st.session_state.UsageMean = UsageMean
        data = np.random.poisson(UsageMean, 1000)
    except:
        pass

UsageChart = st.selectbox('Select Chart Type',Chart_Types,key="UsageChart")
UsageChartButton = st.button("Generate Chart",key="UsageChartButton")

if UsageChartButton:
    
    st.session_state.UsageData = data
    kde = stats.gaussian_kde(data)
    X = KDEDist(kde)
    inc = 1
    x = np.arange(0, max(data), inc)
    fig, axe = plt.subplots() 
    fig.set_tight_layout(True)
    ax2 = axe.twinx() 
    pdfVals = X.pdf(x)
    cdfVals = X.cdf(x)
    
    
    if UsageChart == 'PDF':
        ax2.plot(x, X.pdf(x),color='r',label='PDF')
        plt.title("PDF of Usage")
    else:
        ax2.plot(x, X.cdf(x),color='r',label='CDF')
        plt.title("CDF of Usage")
    
    st.plotly_chart(fig)

st.header('Lead Time Demand Modelling')

LTDChart = st.selectbox('Select Chart Type',Chart_Types,key="LTDChart")
try:
    ProbStockout = float(st.text_input("Enter Probability of Stockout:",key="StockoutProb"))
except:
    pass

LTDChartButton = st.button("Generate Chart",key="LTDChartButton")


if LTDChartButton:
    #data = np.multiply(st.session_state.LTData,st.session_state.UsageData)
    
    data = [None] * 1000
    
    for i in range(0,1000):
        LT = random.sample(list(st.session_state.LTData),1)
        data[i] = np.sum(random.sample(list(st.session_state.UsageData),LT[0]))
    
    kde = stats.gaussian_kde(data)
    X = KDEDist(kde)
    inc = 1
    x = np.arange(0, max(data), inc)
    fig, axe = plt.subplots() 
    fig.set_tight_layout(True)
    ax2 = axe.twinx() 
    pdfVals = X.pdf(x)
    cdfVals = X.cdf(x)    
    Quantile = 1 - ProbStockout
    
    min_val = min(i for i in cdfVals if i > (1-ProbStockout))
    

    min_val_ind = cdfVals.tolist().index(min_val)
    
    UB1 = x[min_val_ind]
    LB1 = x[min_val_ind-1]
    
    Rng1 = UB1 - LB1
    
    UB2 = cdfVals[min_val_ind]
    LB2 = cdfVals[min_val_ind-1]
    
    Rng2 = UB2 - LB2
    Factor = (Quantile-LB2) / Rng2
    SSL = LB1 + (Factor*Rng1)
    ROP = SSL + np.mean(data)
    ROQ = ROP-SSL
    MSL = ROP + ROQ

    if LTDChart == 'PDF':
        ax2.plot(x, X.pdf(x),color='r',label='PDF')
        plt.title("PDF of Lead Time Demand")
    else:
        ax2.plot(x, X.cdf(x),color='r',label='CDF')
        plt.title("CDF of Lead Time Demand")
    
    
    ax2.axvline(x=ROP,color='m',label='Re-Order Point')
    ax2.axvline(x=MSL,color='y',label='Max Stock Level')
    
    st.pyplot(fig)
