# -*- coding: utf-8 -*-
"""
Created on Thu Nov  9 09:13:27 2023

@author: RowanBarua
"""

import streamlit as st
import numpy as np
from scipy import stats
from scipy.stats import poisson
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
        LTMean = st.text_input("Enter Lead Time Mean:",key="LTMean")
        LTStDev = st.text_input("Enter Lead Time Standard Deviation:",key="LTStDev")
        AvgLT = float(LTMean)
        LTStDev2 = float(LTStDev)
        data = np.random.normal(AvgLT, LTStDev2, 1000)
        st.session_state.AvgLT = AvgLT
        st.session_state.LTStDev2 = LTStDev2
    except:
        pass
else:
    try:
        LTMean = st.text_input("Enter Lead Time Mean:",key="LTMean")
        AvgLT = float(LTMean)
        data = np.random.poisson(AvgLT,  1000)
        st.session_state.x = np.arange(0,AvgLT + ((AvgLT**0.5)*3))
        st.session_state.pmf = poisson.pmf(st.session_state.x, AvgLT)
        st.session_state.AvgLT = AvgLT
    except:
        pass

LTChart = st.selectbox('Select Chart Type',Chart_Types,key="LTChart")
LTChartButton = st.button("Generate Chart",key="LTChartButton")

if LTChartButton:
    if LTDist == 'Normal':
        st.session_state.LTData = data
        kde = stats.gaussian_kde(data)
        X = KDEDist(kde)
        inc = 1
        x = np.arange(0, max(data), inc)
        fig, axe = plt.subplots() 
        fig.set_tight_layout(True)
        #ax2 = axe.twinx() 
        pdfVals = X.pdf(x)
        cdfVals = X.cdf(x)
        
        
        if LTChart == 'PDF':
            axe.plot(x, X.pdf(x),color='r',label='PDF')
            plt.title("PDF of Lead Time")
        else:
            axe.plot(x, X.cdf(x),color='r',label='CDF')
            plt.title("CDF of Lead Time")
        
        st.plotly_chart(fig)
    else:
        
        st.session_state.LTData = data
        x = st.session_state.x
        pmf = st.session_state.pmf
        AvgLT = st.session_state.AvgLT
        fig, axe = plt.subplots() 
        fig.set_tight_layout(True)
        #ax2 = axe.twinx() 
        
        if LTChart == 'PDF':
            axe.plot(x, pmf,'o-',color='r',label='PDF')

            plt.title("Probability Mass Function of Lead Time")
        else:
            cdf_vals = poisson.cdf(x, AvgLT)
            axe.plot(x, cdf_vals,'o-',color='r',label='CDF')
            plt.title("Cumulative Distribution Function of Lead Time")
            
        plt.xlabel('Lead Time (Days)', fontsize=14)
        plt.ylabel('Probability', fontsize=14)
        
        st.plotly_chart(fig)        


st.header('Usage Modelling')
UsageDist = st.selectbox('Select Distribution',Distributions,key="UsageDist")

if UsageDist == 'Normal':
    try:
        UsageMean = st.text_input("Enter Usage Mean:",key="UsageMean")
        UsageStDev = st.text_input("Enter Usage Standard Deviation:",key="USageStDev")
        AvgMean = float(UsageMean)
        UsageStDev2 = float(UsageStDev)
        data = np.random.normal(AvgMean, UsageStDev2, 1000)
        st.session_state.AvgMean = AvgMean
        st.session_state.UsageStDev2 = UsageStDev2
    except:
        pass
else:
    try:
        UsageMean = st.text_input("Enter Usage Mean:",key="UsageMean")
        AvgUsage = float(UsageMean)
        data = np.random.poisson(AvgUsage, 1000)
        st.session_state.x = np.arange(0,AvgUsage + ((AvgUsage**0.5)*3))
        st.session_state.pmf = poisson.pmf(st.session_state.x, AvgUsage)
        st.session_state.AvgUsage = AvgUsage
        
    except:
        pass

UsageChart = st.selectbox('Select Chart Type',Chart_Types,key="UsageChart")
UsageChartButton = st.button("Generate Chart",key="UsageChartButton")

if UsageChartButton:
    
    if UsageDist == 'Normal':
        st.session_state.UsageData = data
        kde = stats.gaussian_kde(data)
        X = KDEDist(kde)
        inc = 1
        x = np.arange(0, max(data), inc)
        fig, axe = plt.subplots() 
        fig.set_tight_layout(True)
        #ax2 = axe.twinx() 
        pdfVals = X.pdf(x)
        cdfVals = X.cdf(x)
        
        
        if UsageChart == 'PDF':
            axe.plot(x, X.pdf(x),color='r',label='PDF')
            plt.title("PDF of Daily Usage")
        else:
            axe.plot(x, X.cdf(x),color='r',label='CDF')
            plt.title("CDF of Daily Usage")
    else:
        st.session_state.UsageData = data
        x = st.session_state.x
        pmf = st.session_state.pmf
        AvgUsage = st.session_state.AvgUsage

        fig, axe = plt.subplots() 
        fig.set_tight_layout(True)
        #ax2 = axe.twinx() 
        
        if UsageChart == 'PDF':
            axe.plot(x, pmf,'o-',color='r',label='PDF')

            plt.title("Probability Mass Function of Usage")
        else:
            cdf_vals = poisson.cdf(x,AvgUsage)
            axe.plot(x, cdf_vals,'o-',color='r',label='CDF')
            plt.title("Cumulative Distribution Function of Usage")
            
        plt.xlabel('Usage (Volume of Items Consumed in a Day)', fontsize=14)
        plt.ylabel('Probability', fontsize=14)
        
        st.plotly_chart(fig)    

st.header('Lead Time Demand Modelling')

try:
    ROF = int(st.text_input("Enter Re-Order Frequency (orders / year):",key="ROF"))
except:
    pass

try:
    ProbStockout = float(st.text_input("Enter Probability of Stockout:",key="StockoutProb"))
except:
    pass

LTDChart = st.selectbox('Select Chart Type',Chart_Types,key="LTDChart")
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
    x = np.arange(0, max(data)+ 3*np.std(data), inc)
    fig, axe = plt.subplots(figsize=(10, 6)) 
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
    ROP = LB1 + (Factor*Rng1)
    ROQ = (365 / ROF) * st.session_state.AvgUsage
    MSL = ROP + ROQ

    if LTDChart == 'PDF':
        axe.plot(x, pdfVals,color='r',label='PDF')
        plt.title("PDF of Lead Time Demand")
    else:
        axe.plot(x, cdfVals,color='r',label='CDF')
        plt.title("CDF of Lead Time Demand")
    
    ax2.axvline(x=ROP,color='m',label='Re-Order Point')
    ax2.axvline(x=MSL,color='y',label='Max Stock Level')
    # Adjust the subplot parameters to make room for the legend
    #plt.subplots_adjust(right=0.3)  # Adjust this value as needed to fit your legend
    plt.draw()
    # Add the legend outside the plot
    ax2.legend(loc='upper left')
    
    # Apply tight layout with a pad to fit the legend
    plt.savefig('adjusted_plot.png')

    st.pyplot(fig)
    
    st.write('Re-Order Point: ' + str(round(ROP)))
    st.write('Max Stock Level: ' + str(round(MSL)))
