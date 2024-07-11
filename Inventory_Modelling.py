import streamlit as st
import numpy as np
from scipy import stats
from scipy.stats import poisson
import matplotlib.pyplot as plt
from matplotlib import rcParams
import random
import time

rcParams.update({'figure.autolayout': True})

class KDEDist(stats.rv_continuous):
    def __init__(self, kde, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._kde = kde

    def _pdf(self, x):
        return self._kde.pdf(x)

def profile(func):
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        st.write(f"Execution Time for {func.__name__}: {end_time - start_time} seconds")
        return result
    return wrapper

st.title('Max Stock Holding / Re-Order Point Estimation')

Chart_Types = ['PDF','CDF']
Distributions = ['Poisson','Normal']

st.header('Lead Time Modelling')
LTDist = st.selectbox('Select Distribution',Distributions,key="LTDist")

@profile
def generate_lt_data():
    if LTDist == 'Normal':
        try:
            LTMean = 10  # Hardcoded value for testing
            LTStDev = 2  # Hardcoded value for testing
            AvgLT = float(LTMean)
            LTStDev2 = float(LTStDev)
            data = np.random.normal(AvgLT, LTStDev2, 1000)
            st.session_state.AvgLT = AvgLT
            st.session_state.LTStDev2 = LTStDev2
            return data
        except:
            return None
    else:
        try:
            LTMean = 10  # Hardcoded value for testing
            AvgLT = float(LTMean)
            data = np.random.poisson(AvgLT,  1000)
            st.session_state.x = np.arange(0, AvgLT + ((AvgLT**0.5)*3))
            st.session_state.pmf = poisson.pmf(st.session_state.x, AvgLT)
            st.session_state.AvgLT = AvgLT
            return data
        except:
            return None

lt_data = generate_lt_data()

LTChart = st.selectbox('Select Chart Type',Chart_Types,key="LTChart")
LTChartButton = st.button("Generate Chart",key="LTChartButton")

if LTChartButton and lt_data is not None:
    if LTDist == 'Normal':
        st.session_state.LTData = lt_data
        kde = stats.gaussian_kde(lt_data)
        X = KDEDist(kde)
        inc = 1
        x = np.arange(0, max(lt_data), inc)
        fig, axe = plt.subplots() 
        fig.set_tight_layout(True)
        pdfVals = X.pdf(x)
        cdfVals = X.cdf(x)
        
        if LTChart == 'PDF':
            axe.plot(x, pdfVals, color='r', label='PDF')
            plt.title("PDF of Lead Time")
        else:
            axe.plot(x, cdfVals, color='r', label='CDF')
            plt.title("CDF of Lead Time")
        
        st.pyplot(fig)
    else:
        st.session_state.LTData = lt_data
        x = st.session_state.x
        pmf = st.session_state.pmf
        AvgLT = st.session_state.AvgLT
        fig, axe = plt.subplots() 
        fig.set_tight_layout(True)
        
        if LTChart == 'PDF':
            axe.plot(x, pmf, 'o-', color='r', label='PDF')
            plt.title("Probability Mass Function of Lead Time")
        else:
            cdf_vals = poisson.cdf(x, AvgLT)
            axe.plot(x, cdf_vals, 'o-', color='r', label='CDF')
            plt.title("Cumulative Distribution Function of Lead Time")
            
        plt.xlabel('Lead Time (Days)', fontsize=14)
        plt.ylabel('Probability', fontsize=14)
        
        st.pyplot(fig)

st.header('Usage Modelling')
UsageDist = st.selectbox('Select Distribution',Distributions,key="UsageDist")

@profile
def generate_usage_data():
    if UsageDist == 'Normal':
        try:
            UsageMean = 20  # Hardcoded value for testing
            UsageStDev = 5  # Hardcoded value for testing
            AvgMean = float(UsageMean)
            UsageStDev2 = float(UsageStDev)
            data = np.random.normal(AvgMean, UsageStDev2, 1000)
            st.session_state.AvgMean = AvgMean
            st.session_state.UsageStDev2 = UsageStDev2
            return data
        except:
            return None
    else:
        try:
            UsageMean = 20  # Hardcoded value for testing
            AvgUsage = float(UsageMean)
            data = np.random.poisson(AvgUsage, 1000)
            st.session_state.x = np.arange(0, AvgUsage + ((AvgUsage**0.5)*3))
            st.session_state.pmf = poisson.pmf(st.session_state.x, AvgUsage)
            st.session_state.AvgUsage = AvgUsage
            return data
        except:
            return None

usage_data = generate_usage_data()

UsageChart = st.selectbox('Select Chart Type',Chart_Types,key="UsageChart")
UsageChartButton = st.button("Generate Chart",key="UsageChartButton")

if UsageChartButton and usage_data is not None:
    if UsageDist == 'Normal':
        st.session_state.UsageData = usage_data
        kde = stats.gaussian_kde(usage_data)
        X = KDEDist(kde)
        inc = 1
        x = np.arange(0, max(usage_data), inc)
        fig, axe = plt.subplots() 
        fig.set_tight_layout(True)
        pdfVals = X.pdf(x)
        cdfVals = X.cdf(x)
        
        if UsageChart == 'PDF':
            axe.plot(x, pdfVals, color='r', label='PDF')
            plt.title("PDF of Daily Usage")
        else:
            axe.plot(x, cdfVals, color='r', label='CDF')
            plt.title("CDF of Daily Usage")
    else:
        st.session_state.UsageData = usage_data
        x = st.session_state.x
        pmf = st.session_state.pmf
        AvgUsage = st.session_state.AvgUsage

        fig, axe = plt.subplots() 
        fig.set_tight_layout(True)
        
        if UsageChart == 'PDF':
            axe.plot(x, pmf, 'o-', color='r', label='PDF')
            plt.title("Probability Mass Function of Usage")
        else:
            cdf_vals = poisson.cdf(x, AvgUsage)
            axe.plot(x, cdf_vals, 'o-', color='r', label='CDF')
            plt.title("Cumulative Distribution Function of Usage")
            
        plt.xlabel('Usage (Volume of Items Consumed in a Day)', fontsize=14)
        plt.ylabel('Probability', fontsize=14)
        
        st.pyplot(fig)

st.header('Lead Time Demand Modelling')

try:
    ROF = 12  # Hardcoded value for testing
except:
    ROF = None

try:
    ProbStockout = 0.05  # Hardcoded value for testing
except:
    ProbStockout = None

LTDChart = st.selectbox('Select Chart Type',Chart_Types,key="LTDChart")
LTDChartButton = st.button("Generate Chart",key="LTDChartButton")

@profile
def generate_ltd_chart():
    LTData = np.array(st.session_state.LTData)
    UsageData = np.array(st.session_state.UsageData)
    
    @profile
    def generate_data():
        return np.array([np.sum(np.random.choice(UsageData, size=int(LT), replace=True)) for LT in np.random.choice(LTData, size=1000, replace=True)])
    
    data = generate_data()

    @profile
    def calculate_kde():
        kde = stats.gaussian_kde(data)
        return KDEDist(kde)
    
    X = calculate_kde()

    @profile
    def generate_plot_data():
        inc = 1
        x = np.arange(0, max(data) + 3 * np.std(data), inc)
        pdfVals = X.pdf(x)
        cdfVals = X.cdf(x)
        return x, pdfVals, cdfVals
    
    x, pdfVals, cdfVals = generate_plot_data()
    
    Quantile = 1 - ProbStockout

    @profile
    def calculate_reorder_point():
        st.write("Calculating reorder point...")
        st.write(f"x: {x}")
        st.write(f"cdfVals: {cdfVals}")
        
        min_val = min(i for i in cdfVals if i > Quantile)
        st.write(f"min_val: {min_val}")
        
        min_val_ind = cdfVals.tolist().index(min_val)
        st.write(f"min_val_ind: {min_val_ind}")
        
        UB1 = x[min_val_ind]
        LB1 = x[min_val_ind-1]
        st.write(f"UB1: {UB1}, LB1: {LB1}")
        
        Rng1 = UB1 - LB1
        st.write(f"Rng1: {Rng1}")
        
        UB2 = cdfVals[min_val_ind]
        LB2 = cdfVals[min_val_ind-1]
        st.write(f"UB2: {UB2}, LB2: {LB2}")

        Rng2 = UB2 - LB2
        st.write(f"Rng2: {Rng2}")
        
        Factor = (Quantile - LB2) / Rng2
        st.write(f"Factor: {Factor}")
        
        ROP = LB1 + (Factor * Rng1)
        ROQ = (365 / ROF) * st.session_state.AvgUsage
        MSL = ROP + ROQ
        return ROP, MSL
    
    ROP, MSL = calculate_reorder_point()

    @profile
    def generate_plots():
        fig, axe = plt.subplots(figsize=(10, 6)) 
        fig.set_tight_layout(True)
        ax2 = axe.twinx()

        if LTDChart == 'PDF':
            axe.plot(x, pdfVals, color='r', label='PDF')
            plt.title("PDF of Lead Time Demand")
        else:
            axe.plot(x, cdfVals, color='r', label='CDF')
            plt.title("CDF of Lead Time Demand")
        
        ax2.axvline(x=ROP, color='m', label='Re-Order Point')
        ax2.axvline(x=MSL, color='y', label='Max Stock Level')
        plt.draw()
        ax2.legend(loc='upper left')
        
        st.pyplot(fig)

    generate_plots()
    
    st.write('Re-Order Point: ' + str(round(ROP)))
    st.write('Max Stock Level: ' + str(round(MSL)))

if LTDChartButton and ROF is not None and ProbStockout is not None:
    generate_ltd_chart()
