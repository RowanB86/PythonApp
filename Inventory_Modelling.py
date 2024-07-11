import streamlit as st
import numpy as np
from scipy import stats
import matplotlib.pyplot as plt
from matplotlib import rcParams
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

@profile
def generate_lt_data():
    try:
        LTMean = 10  # Hardcoded value for testing
        LTStDev = 2  # Hardcoded value for testing
        AvgLT = float(LTMean)
        LTStDev2 = float(LTStDev)
        data = np.random.normal(AvgLT, LTStDev2, 1000)
        st.session_state.AvgLT = AvgLT
        st.session_state.LTStDev2 = LTStDev2
        return data
    except Exception as e:
        st.write(f"Error generating lead time data: {e}")
        return None

@profile
def generate_usage_data():
    try:
        UsageMean = 20  # Hardcoded value for testing
        UsageStDev = 5  # Hardcoded value for testing
        AvgMean = float(UsageMean)
        UsageStDev2 = float(UsageStDev)
        data = np.random.normal(AvgMean, UsageStDev2, 1000)
        st.session_state.AvgMean = AvgMean
        st.session_state.UsageStDev2 = UsageStDev2
        return data
    except Exception as e:
        st.write(f"Error generating usage data: {e}")
        return None

@profile
def generate_ltd_chart():
    try:
        LTData = np.array(st.session_state.LTData)
        UsageData = np.array(st.session_state.UsageData)
        st.write("Generating Lead Time Demand data...")
        
        # Simplified data generation to identify the issue
        generated_data = []
        for LT in np.random.choice(LTData, size=1000, replace=True):
            generated_data.append(np.sum(np.random.choice(UsageData, size=int(LT), replace=True)))
        data = np.array(generated_data)
        
        st.write(f"Generated data: {data[:10]}...")

        kde = stats.gaussian_kde(data)
        X = KDEDist(kde)
        inc = 1
        x = np.arange(0, max(data) + 3 * np.std(data), inc)
        pdfVals = X.pdf(x)
        cdfVals = X.cdf(x)
        
        st.write(f"PDF values: {pdfVals[:10]}...")
        st.write(f"CDF values: {cdfVals[:10]}...")

        Quantile = 1 - 0.05  # Hardcoded value for testing

        min_val = min(i for i in cdfVals if i > Quantile)
        min_val_ind = cdfVals.tolist().index(min_val)
        UB1 = x[min_val_ind]
        LB1 = x[min_val_ind - 1]
        Rng1 = UB1 - LB1
        UB2 = cdfVals[min_val_ind]
        LB2 = cdfVals[min_val_ind - 1]
        Rng2 = UB2 - LB2
        Factor = (Quantile - LB2) / Rng2
        ROP = LB1 + (Factor * Rng1)
        ROQ = (365 / 12) * st.session_state.AvgUsage
        MSL = ROP + ROQ

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

        st.write('Re-Order Point: ' + str(round(ROP)))
        st.write('Max Stock Level: ' + str(round(MSL)))
    except Exception as e:
        st.write(f"Error generating Lead Time Demand chart: {e}")

# Main Code Execution
st.title('Max Stock Holding / Re-Order Point Estimation')

# Generate Lead Time Data
st.header('Lead Time Modelling')
lt_data = generate_lt_data()
st.session_state.LTData = lt_data if lt_data is not None else []

# Generate Usage Data
st.header('Usage Modelling')
usage_data = generate_usage_data()
st.session_state.UsageData = usage_data if usage_data is not None else []

# Generate Lead Time Demand Chart
st.header('Lead Time Demand Modelling')
LTDChart = st.selectbox('Select Chart Type', ['PDF', 'CDF'], key="LTDChart")
LTDChartButton = st.button("Generate Chart", key="LTDChartButton")

if LTDChartButton:
    generate_ltd_chart()
