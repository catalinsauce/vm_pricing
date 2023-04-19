import streamlit as st
import altair as alt


st.set_page_config(layout="wide")

import streamlit_pandas as sp
import configparser
import os
import snowflake.connector
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
import math
import pickle
from collections import defaultdict


import logging  # Used to display messages instead of jusy printing them
import snowflake.connector

logger = logging.getLogger()
logger.setLevel(logging.INFO)
pd.set_option("display.max_columns", None)
pd.set_option("display.width", 1000)

###############################

# config = configparser.ConfigParser()
# config.read("config.ini")

# # Get the current working directory
# cwd = os.getcwd()

# Print the current working directory
# print("Current working directory:", cwd)

# Import Data


@st.cache_data
def load_csv(csv_name):
    df = pd.read_csv("data/" + csv_name + ".csv")
    return df


arr = load_csv("arr_for_boxplot_170423")
actual_vs_expected = load_csv("current_arr_170423")


# Streamlit commands
create_data = {"arr_ind": "multiselect"}


# Create All Widgets for Streamlit
all_widgets = sp.create_widgets(arr.head(100), create_data)
res = sp.filter_df(arr.head(100), all_widgets)

st.title("Current Enterprise ARR to be used in Pricing")
st.write(res)

# sort the DataFrame by the Category column in ascending order
arr_sorted = arr.sort_values("vm_ccy_total")


# create a boxplot using altair
st.subheader("ARR per VM by ccy_bins: ")
chart = (
    alt.Chart(arr_sorted)
    .mark_boxplot()
    .encode(
        x=alt.X("ccy_bins:N", sort=alt.EncodingSortField("vm_ccy_total")),
        y="arr_per_vm:Q",
    )
)

# display the chart in Streamlit
st.altair_chart(chart, use_container_width=True)


# Show summary between actual and exected
st.subheader("Actual ARR vs Expected ARR by ccy_bins: ")
st.write(actual_vs_expected)

# Takeaways
st.subheader("Takeaways: ")

st.write(
    """
- The summary of actual ARR versus expected ARR highlights the percentage differences between the actual ARR and the expected ARR. What could be the reason for the significantly lower average prices in the 1-9 and 25-49 bins compared to the actual ARR?
    - 1-9 ccy_bin shows 20% less actual median ARR vs expected arr.
    - 25-49 ccy_bin shows 18% less actual median ARR vs expected arr.
    """
)

st.write(
    """
- The box plot reveals the presence of numerous outliers. Should these data points be interpreted as anomalies or as legitimate deviations from the median?
    - Certain data points appear to be errors, as they indicate that the total ARR for VM exceeds the combined total ARR for both VM and RDC. Logically, this discrepancy should not occur.
    """
)

# Filter our the clients with VM ARR > Total arr
arr_ind_false = arr[arr["arr_ind"] == False].sort_values(
    by=["arr_per_vm"], ascending=False
)

arr_ind_true = arr[arr["arr_ind"] == True].sort_values(
    by=["arr_per_vm"], ascending=False
)


# Comments for the filtered data
st.subheader("Clients with VM ARR > Total ARR:")
st.write(arr_ind_false)

st.write(
    """
- Based on total VM ARR, the highest arr_per_vm is over $27000.
    - 13 clients show arr_per_vm over $4000.
    """
)

st.write(
    """
- Once we remove these points the box plot looks like this:
    """
)

st.subheader("ARR per VM by ccy_bins when VM ARR < Total ARR: ")
chart_ind_true = (
    alt.Chart(arr_ind_true)
    .mark_boxplot()
    .encode(
        x=alt.X("ccy_bins:N", sort=alt.EncodingSortField("vm_ccy_total")),
        y="arr_per_vm:Q",
    )
)

# display the chart in Streamlit
st.altair_chart(chart_ind_true, use_container_width=True, theme="streamlit")

# Summarize arr by ccy_bins when arr_ind = True
actual_vs_expected_true = (
    arr_ind_true.groupby(["ccy_bins"])["arr_per_vm"]
    .agg(["count", "median", "mean", "min", "max"])
    .reset_index()
)
actual_vs_expected_true["vm_price_annual"] = [
    200 * 12,
    174 * 12,
    159 * 12,
    139 * 12,
    119 * 12,
    99 * 12,
    85 * 12,
]
actual_vs_expected_true["median_vs_vm_price"] = (
    actual_vs_expected_true["median"] / actual_vs_expected_true["vm_price_annual"]
)
actual_vs_expected_true["mean_vs_vm_price"] = (
    actual_vs_expected_true["mean"] / actual_vs_expected_true["vm_price_annual"]
)

st.subheader("Actual ARR vs Expected ARR by ccy_bins when VM ARR < Total ARR: ")
st.write(actual_vs_expected_true)
