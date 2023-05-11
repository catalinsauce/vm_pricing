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

# Set the fixed x-axis, y-axis limit value
y_limit = 2600000
x_limit = 2000

# Create scatter plots
win_plot = (
    alt.Chart(ccy_usage)
    .mark_point()
    .transform_filter(alt.datum.win_ccy)
    .encode(
        y=alt.Y("current_vm_arr_total", scale=alt.Scale(domain=[0, y_limit])),
        x=alt.X("win_ccy", scale=alt.Scale(domain=[0, x_limit])),
    )
    .properties(width=500, height=300)
)

win_reg = win_plot.transform_regression(
    "win_ccy", "current_vm_arr_total", method="linear"
).mark_line(color="red")


mac_plot = (
    alt.Chart(ccy_usage)
    .mark_point()
    .transform_filter(alt.datum.mac_ccy <= x_limit)
    .encode(
        y=alt.Y("current_vm_arr_total", scale=alt.Scale(domain=[0, y_limit])),
        x=alt.X("mac_ccy", scale=alt.Scale(domain=[0, x_limit])),
    )
    .properties(width=500, height=300)
)

mac_reg = mac_plot.transform_regression(
    "mac_ccy", "current_vm_arr_total", method="linear"
).mark_line(color="red", interpolate="basis")


android_plot = (
    alt.Chart(ccy_usage)
    .mark_point()
    .encode(
        y=alt.Y("current_vm_arr_total", scale=alt.Scale(domain=[0, y_limit])),
        x=alt.X("android_ccy", scale=alt.Scale(domain=[0, x_limit])),
    )
    .properties(width=500, height=300)
)
android_reg = android_plot.transform_regression(
    "android_ccy", "current_vm_arr_total", method="linear"
).mark_line(color="red")

ios_plot = (
    alt.Chart(ccy_usage)
    .mark_point()
    .encode(
        y=alt.Y("current_vm_arr_total", scale=alt.Scale(domain=[0, y_limit])),
        x=alt.X("ios_ccy", scale=alt.Scale(domain=[0, x_limit])),
    )
    .properties(width=500, height=300)
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

st.markdown(
    """
    <h2 style="text-align: center;">Linear Multivariate Model Results: v1</h2>
    """,
    unsafe_allow_html=True,
)

# Add some space between the subheader and the chart
st.write("")
st.write("")
st.write("")


# Display the coefficients
# st.write(coef_df[:4])

# Extract the coefficients and confidence intervals
coef = gaussian_results_arr_ccy.params[:4]
ci_low = gaussian_results_arr_ccy.conf_int(alpha=0.05)[0][:4]
ci_high = gaussian_results_arr_ccy.conf_int(alpha=0.05)[1][:4]

# Combine the coefficients and confidence intervals into a DataFrame
forest_data = pd.DataFrame(
    {
        "Variable": coef.index,
        "Coefficient": coef.values,
        "CI Low": ci_low.values,
        "CI High": ci_high.values,
    }
)

# Sort the DataFrame by coefficient value
forest_data = forest_data.sort_values(by="Coefficient", ascending=True)

# Create the forest plot
chart_forest = (
    alt.Chart(forest_data)
    .mark_rule(size=2)
    .encode(
        y=alt.Y("Variable:N", sort="-x", title=None),
        x=alt.X("CI Low:Q", title=None),
        x2="CI High:Q",
        color=alt.condition(
            alt.datum.Coefficient > 0, alt.value("green"), alt.value("red")
        ),
    )
    .properties(height=300, width=500, title="Price Ranges")
)

# Add text labels for the coefficients
chart_text = (
    alt.Chart(forest_data)
    .mark_text(dx=20, color="black")
    .encode(
        y=alt.Y("Variable:N", sort="-x", title=None),
        x=alt.X("CI High:Q", title=None, scale=alt.Scale(domain=[0, 3200])),
        text=alt.Text("Coefficient:Q", format=".2f"),
    )
)

# Combine the forest plot and text labels
chart_forest_text = chart_forest + chart_text

# Create a two-column layout with custom width ratios
col1, col2 = st.columns([5, 5])

# # Create a two-column layout
# col1, col2 = st.columns(2)

# Display the coefficients table in the first column
col1.markdown("###### Coefficient Results")
col1.write(coef_df[:4], width=500, height=300)

# Display the forest plot with text labels in the second column
col2.altair_chart(chart_forest_text, use_container_width=True)


# print(glm_linear.summary())
# coef = glm_linear.coef_

# # Display the coefficients in a table
# st.write("Model Coefficients")
# st.write(pd.DataFrame(coef, columns=["Coefficients"]))


# Get the predicted values from the model
ccy_usage["arr_pred"] = gaussian_results_arr_ccy.predict()


scatter_actual = (
    alt.Chart(ccy_usage)
    .mark_point(opacity=0.7, shape="circle")
    .encode(
        x=alt.X("vm_ccy_total", title="Total CCY"),
        y=alt.Y("current_vm_arr_total", title="VM ARR Total"),
        color=alt.value("blue"),
        tooltip=["vm_ccy_total", "current_vm_arr_total"],
    )
)

scatter_predicted = (
    alt.Chart(ccy_usage)
    .mark_point(opacity=0.7, shape="triangle")
    .encode(
        x=alt.X("vm_ccy_total", title="Total CCY"),
        y=alt.Y("arr_pred", title="VM ARR Predicted"),
        color=alt.value("red"),
        tooltip=["vm_ccy_total", "arr_pred"],
    )
)

# Combine the scatter plots
combined_scatter = scatter_actual + scatter_predicted

st.markdown("###### Predicted ARR vs Actual ARR")

# Display the combined scatter plots
st.altair_chart(combined_scatter, use_container_width=True)


# Calculate the differences between actual and predicted values
ccy_usage["Difference"] = ccy_usage["arr_pred"] - ccy_usage["current_vm_arr_total"]
# st.write(ccy_usage)

# Calculate the count values
histogram_data = ccy_usage["Difference"].value_counts().reset_index()
histogram_data.columns = ["Difference", "Count"]

# Create the histogram
histogram = (
    alt.Chart(histogram_data)
    .mark_bar()
    .encode(
        x=alt.X("Difference:Q", bin=alt.Bin(maxbins=100), title="Difference"),
        y=alt.Y("Count:Q", title="Count"),
        tooltip=["Difference", "Count"],
    )
    .properties(
        width=500,
        height=300,
        title="Histogram of Differences: Predicted vs Actual",
    )
)

# Display the histogram
st.altair_chart(histogram, use_container_width=True)

# Calculate the sum of the differences and the count
sum_of_differences = ccy_usage["Difference"].sum()


# Format the sum as a dollar amount
sum_of_differences_formatted = "${:,.2f}".format(sum_of_differences)


# Takeaways
st.subheader("Takeaways: ")

# Print the result
st.write("Sum of Predicted vs Actual:", sum_of_differences_formatted)

# Calculate the average of the differences
average_difference = ccy_usage["Difference"].mean()

# Format the average as a dollar amount
average_difference_formatted = "${:,.2f}".format(average_difference)

# Print the result
st.write("Average Predicted vs Actual per Organization:", average_difference_formatted)


# Add some space between the subheader and the chart
st.write("")
st.write("")
st.write("")

# Takeaways
st.subheader("Final Results Table: ")

st.write(ccy_usage)


# # Create the histogram
# histogram = (
#     alt.Chart(ccy_usage)
#     .mark_bar()
#     .encode(
#         x=alt.X("Difference:Q", bin=alt.Bin(maxbins=20), title="Difference"),
#         y=alt.Y("count():Q", title="Count"),
#         tooltip=["Difference"],
#     )
#     .properties(
#         width=500,
#         height=300,
#         title="Histogram of Differences: Actual vs Predicted",
#     )
# )

# # Display the histogram
# st.altair_chart(histogram, use_container_width=True)
