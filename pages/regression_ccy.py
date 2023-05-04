import streamlit as st
import altair as alt

import streamlit_pandas as sp
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import pickle
import statsmodels.api as sm


pd.set_option("display.max_columns", 10)
pd.set_option("display.width", 1000)

###############################


@st.cache_data
def load_csv(csv_name):
    df = pd.read_csv("data/" + csv_name + ".csv")
    return df


ccy_usage = load_csv("ccy_regression_03052023")


# Streamlit commands
create_data = {"arr_ind": "multiselect", "ccy_bins": "multiselect"}


# # Filter dataframe on vm arr < total arr
# arr_usage_true = arr_usage[arr_usage["arr_ind"] == True]
# ccy_usage_true = ccy_usage[ccy_usage["arr_ind"] == True]


# arr_usage_true_filter = arr_usage_true[
#     [
#         "org_name",
#         "org_uuid",
#         "arr_ind",
#         "current_vm_arr_total",
#         "vm_ccy_total",
#         "ccy_bins",
#         "mins_win_perc",
#         "mins_mac_perc",
#         "mins_android_perc",
#         "mins_ios_perc",
#     ]
# ]


# Create All Widgets for Streamlit
all_widgets = sp.create_widgets(
    ccy_usage[["org_name", "org_uuid", "arr_ind", "ccy_bins"]], create_data
)
res = sp.filter_df(ccy_usage, all_widgets)

st.title("Current Enterprise VM CCY Usage")
st.write(ccy_usage)


st.subheader("Total VM CCY vs Total VM ARR")

# Create the scatter plot
scatter_plot = (
    alt.Chart(ccy_usage).mark_point().encode(x="vm_ccy_total", y="current_vm_arr_total")
)

# Add a regression line
regression = scatter_plot.transform_regression(
    "vm_ccy_total", "current_vm_arr_total", method="linear"
).mark_line(color="red")


# Combine the scatter plot, regression line, and R-squared text
chart = (scatter_plot + regression).properties(width=600, height=400)

# Display the chart using Streamlit
st.altair_chart(chart, use_container_width=True)


st.subheader("CCY Type vs Total VM ARR")

# Create scatter plots
win_plot = (
    alt.Chart(ccy_usage)
    .mark_point()
    .encode(y="current_vm_arr_total", x="win_ccy")
    .properties(width=650, height=500)
)
win_reg = win_plot.transform_regression(
    "win_ccy", "current_vm_arr_total", method="linear"
).mark_line(color="red")

mac_plot = (
    alt.Chart(ccy_usage)
    .mark_point()
    .encode(y="current_vm_arr_total", x="mac_ccy")
    .properties(width=650, height=500)
)
mac_reg = mac_plot.transform_regression(
    "mac_ccy", "current_vm_arr_total", method="linear"
).mark_line(color="red")

android_plot = (
    alt.Chart(ccy_usage)
    .mark_point()
    .encode(y="current_vm_arr_total", x="android_ccy")
    .properties(width=650, height=500)
)
android_reg = android_plot.transform_regression(
    "android_ccy", "current_vm_arr_total", method="linear"
).mark_line(color="red")

ios_plot = (
    alt.Chart(ccy_usage)
    .mark_point()
    .encode(y="current_vm_arr_total", x="ios_ccy")
    .properties(width=650, height=500)
)
ios_reg = ios_plot.transform_regression(
    "ios_ccy", "current_vm_arr_total", method="linear"
).mark_line(color="red")


# Display charts in a 2x2 grid
row1 = alt.hconcat(win_plot + win_reg, mac_plot + mac_reg)
row2 = alt.hconcat(android_plot + android_reg, ios_plot + ios_reg)
chart = alt.vconcat(row1, row2)

# chart = (
#     alt.layer(win_chart, mac_chart, android_chart, ios_chart, data=ccy_usage)
#     .resolve_scale(x="independent", y="independent")
#     .properties(width="container", height=400)
# )

# Display the chart using Streamlit
st.altair_chart(chart, use_container_width=True)


# Load the pickled model
formula = "current_vm_arr_total ~ win_ccy + mac_ccy + android_ccy + ios_ccy + android_ccy*ios_ccy - 1"

# Instantiate a Gaussian family model with the identity link function
gaussian_model_arr_ccy = sm.GLM.from_formula(
    formula=formula, data=ccy_usage, family=sm.families.Gaussian()
)

# Fit the model
gaussian_results_arr_ccy = gaussian_model_arr_ccy.fit()

# Print the summary of the model
# print(gaussian_results_arr_ccy.summary())

# extract coefficients, std err, z-values, p-values
coef = gaussian_results_arr_ccy.params
std_err = gaussian_results_arr_ccy.bse
z_values = gaussian_results_arr_ccy.tvalues
p_values = gaussian_results_arr_ccy.pvalues

# compute range
range_min = coef - 2 * std_err
range_max = coef + 2 * std_err

# combine values into a dataframe
coef_df = pd.DataFrame(
    {
        "Price": coef,
        "Std. Error": std_err,
        "z-value": z_values,
        "P > |z|": p_values,
        "Price Range": [
            f"[{min_val:.2f}, {max_val:.2f}]"
            for min_val, max_val in zip(range_min, range_max)
        ],
    }
)

# print(coef_df[:4])

st.subheader("Linear Multivariate Model Results: v1")

# Display the coefficients
st.write(coef_df[:4])

# print(glm_linear.summary())
# coef = glm_linear.coef_

# # Display the coefficients in a table
# st.write("Model Coefficients")
# st.write(pd.DataFrame(coef, columns=["Coefficients"]))


# Get the predicted values from the model
ccy_usage["arr_pred"] = gaussian_results_arr_ccy.predict()


# # Create the Altair chart
# chart = (
#     alt.Chart(ccy_usage)
#     .mark_point(filled=True)
#     .encode(
#         x=alt.X("vm_ccy_total", title="Total CCY"),
#         y=alt.Y("current_vm_arr_total", title="VM ARR Total"),
#         color=alt.condition(
#             alt.datum.arr_pred,
#             alt.value("red"),  # Predicted values in red
#             alt.value("blue"),  # Actual values in blue
#         ),
#     )
#     .properties(width=600, height=400, title="Actual vs Predicted Values")
# )

# # Display the chart using Streamlit
# st.altair_chart(chart, use_container_width=True)


# Plot the actual values vs predicted values
fig, ax = plt.subplots(figsize=(8, 4))
ax.scatter(ccy_usage["vm_ccy_total"], ccy_usage["current_vm_arr_total"], label="Actual")
ax.scatter(ccy_usage["vm_ccy_total"], ccy_usage["arr_pred"], label="Predicted")
ax.set_xlabel("Total CCY")
ax.set_ylabel("VM ARR Total")
ax.set_title("Actual vs Predicted Values")
ax.legend()

# Display the plot in Streamlit
st.pyplot(fig)

# Create a scatter plot
# scatter_plot = (
#     alt.Chart(ccy_usage)
#     .mark_point()
#     .encode(
#         x="vm_ccy_total",
#         y=alt.Y("current_vm_arr_total", title="VM ARR Total"),
#         color=alt.Color(
#             "type",
#             legend=alt.Legend(title="Values"),
#             scale=alt.Scale(range=["red", "blue"]),
#         ),
#         shape=alt.Shape("type", scale=alt.Scale(range=["circle", "square"])),
#     )
# )

# # Add the predicted values as a regression line
# regression_line = scatter_plot.transform_regression(
#     "vm_ccy_total", "arr_pred"
# ).mark_line(color="green")

# # Combine the scatter plot and regression line
# chart = (scatter_plot + regression_line).properties(width=600, height=400)

# # Display the chart in Streamlit
# st.altair_chart(chart, use_container_width=True)
