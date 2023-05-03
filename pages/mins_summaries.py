import streamlit as st
import altair as alt

import streamlit_pandas as sp
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

pd.set_option("display.max_columns", 10)
pd.set_option("display.width", 1000)

###############################


@st.cache_data
def load_csv(csv_name):
    df = pd.read_csv("data/" + csv_name + ".csv")
    return df


arr_usage = load_csv("arr_usage_200423")
ccy_usage = load_csv("ccy_usage_030523")
arr_box_plots = load_csv("arr_for_boxplot_170423")


# Streamlit commands
create_data = {"arr_ind": "multiselect", "ccy_bins": "multiselect"}

# Filter dataframe on vm arr < total arr
arr_usage_true = arr_usage[arr_usage["arr_ind"] == True]
ccy_usage_true = ccy_usage[ccy_usage["arr_ind"] == True]


arr_usage_true_filter = arr_usage_true[
    [
        "org_name",
        "org_uuid",
        "arr_ind",
        "current_vm_arr_total",
        "vm_ccy_total",
        "ccy_bins",
        "mins_win_perc",
        "mins_mac_perc",
        "mins_android_perc",
        "mins_ios_perc",
    ]
]


# Create All Widgets for Streamlit
all_widgets = sp.create_widgets(
    arr_usage_true_filter[["org_name", "org_uuid", "arr_ind", "ccy_bins"]], create_data
)
res = sp.filter_df(arr_usage_true_filter, all_widgets)

st.title("Current Enterprise VM Usage to be used in Pricing")
st.write(arr_usage_true_filter)


# print(arr_usage_true.head())


# usage_distribution = (
#     arr_usage_true[
#         [
#             "mins_win_perc",
#             "mins_mac_perc",
#             "mins_android_perc",
#             "mins_ios_perc",
#             "win_arr",
#             "mac_arr",
#             "android_arr",
#             "ios_arr",
#             "current_vm_arr_total",
#         ]
#     ]
#     .describe([0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9])
#     .round(2)
# ).reset_index()


# df_cumulative_usage = usage_distribution.iloc[:, :5][3:]
# df_cumulative_usage = df_cumulative_usage.rename(
#     columns={"index": "percentiles"}
# ).reset_index()


st.subheader("Enterprise minutes distribution in terms of percentages")


# df_cumulative_arr = usage_distribution[
#     ["index", "win_arr", "mac_arr", "android_arr", "ios_arr"]
# ][3:]
# df_cumulative_arr = df_cumulative_arr.rename(columns={"index": "percentiles"})

# print(df_cumulative_arr)

# # plot the cumulative sums for each field
# ax = df_cumulative_usage.plot(kind="line", figsize=(10, 6))
# ax.set_xlabel("percentiles")
# ax.set_ylabel("Cumulative Usage %")
# plt.title("Cumulative Usage of Win, Mac, Android, iOS")
# plt.show()

# # plot the cumulative sums for each field
# ax = df_cumulative_arr.plot(kind="line", figsize=(10, 6))
# ax.set_xlabel("percentiles")
# ax.set_ylabel("Cumulative ARR $")
# plt.title("Cumulative ARR for Win, Mac, Android, iOS")
# plt.show()

# df_cumulative_usage_filter_1 = df_cumulative_usage[
#     ["index", "win_arr", "mac_arr", "android_arr", "ios_arr"]
# ]


# df_cumulative_usage_streamlit = df_cumulative_usage[
#     ["index", "win_arr", "mac_arr", "android_arr", "ios_arr"]
# ].melt(id_vars="index", var_name="vm_type", value_name="Value")

# df_cumulative_usage = df_cumulative_usage.rename(columns={"index": "percentile_index"})
# df_cumulative_usage_streamlit = df_cumulative_usage[
#     [
#         "percentiles",
#         "mins_win_perc",
#         "mins_mac_perc",
#         "mins_android_perc",
#         "mins_ios_perc",
#     ]
# ]

# df_cumulative_usage_streamlit = df_cumulative_usage_streamlit.melt(
#     id_vars="percentiles", var_name="vm_type", value_name="Value"
# )

# print(df_cumulative_usage_streamlit)

# print(df_cumulative_usage_streamlit)
# df_cumulative_usage_streamlit["Value"] = df_cumulative_usage_streamlit["Value"].astype(
#     float
# )
# print(df_cumulative_usage_streamlit.dtypes)


# print()


# Create histograms representing distribution of minutes by resources

mins_win = arr_usage_true[["mins_win_perc"]]
mins_mac = arr_usage_true[["mins_mac_perc"]]
mins_android = arr_usage_true[["mins_android_perc"]]
mins_ios = arr_usage_true[["mins_ios_perc"]]


chart1 = (
    alt.Chart(mins_win)
    .mark_bar()
    .encode(
        x=alt.X("mins_win_perc:Q", bin=True),
        y=alt.Y("count()", axis=alt.Axis(title="Orgs Count")),
    )
    .properties(width=500, height=350, title="Distribution of Annual % Windows Minutes")
)


chart2 = (
    alt.Chart(mins_mac)
    .mark_bar()
    .encode(
        x=alt.X("mins_mac_perc:Q", bin=True),
        y=alt.Y("count()", axis=alt.Axis(title="Orgs Count")),
    )
    .properties(width=500, height=350, title="Distribution of Annual % Mac Minutes")
)

chart3 = (
    alt.Chart(mins_android)
    .mark_bar()
    .encode(
        x=alt.X("mins_android_perc:Q", bin=True),
        y=alt.Y("count()", axis=alt.Axis(title="Orgs Count")),
    )
    .properties(width=500, height=350, title="Distribution of Annual % Android Minutes")
)

chart4 = (
    alt.Chart(mins_ios)
    .mark_bar()
    .encode(
        x=alt.X("mins_ios_perc:Q", bin=True),
        y=alt.Y("count()", axis=alt.Axis(title="Orgs Count")),
    )
    .properties(width=500, height=350, title="Distribution of Annual % iOS Minutes")
)

# combine the four charts into a grid
grid = alt.vconcat(
    alt.hconcat(chart1, chart2, spacing=200),
    alt.hconcat(chart3, chart4, spacing=200),
).resolve_scale(y="independent")

# display the grid
st.altair_chart(grid)

# # create the chart
# st.altair_chart(
#     alt.Chart(df_cumulative_usage_streamlit)
#     .mark_line()
#     .encode(
#         x=alt.X(
#             "percentiles:O",
#             axis=alt.Axis(title="Percentiles"),
#             sort=alt.EncodingSortField("index"),
#         ),
#         y=alt.Y("Value:Q", axis=alt.Axis(title="Cumulative % Usage")),
#         color=alt.Color(
#             "vm_type:O", scale=alt.Scale(range=["red", "blue", "black", "green"])
#         ),
#         tooltip=["percentiles", "vm_type", "Value"],
#     )
#     .properties(width=1200, height=400)
# )


st.subheader("Enterprise CCY distribution in terms of percentages")

# Create histograms representing distribution of minutes by resources

ccy_win = ccy_usage_true[["ccy_pc_perc"]]
ccy_mac = ccy_usage_true[["ccy_mac_perc"]]
ccy_android = ccy_usage_true[["ccy_android_perc"]]
ccy_ios = ccy_usage_true[["ccy_ios_perc"]]

chart1_ccy = (
    alt.Chart(ccy_win)
    .mark_bar()
    .encode(
        x=alt.X("ccy_pc_perc:Q", bin=True),
        y=alt.Y("count()", axis=alt.Axis(title="Orgs Count")),
    )
    .properties(width=500, height=350, title="Distribution of Annual Windows CCY % ")
)


chart2_ccy = (
    alt.Chart(ccy_mac)
    .mark_bar()
    .encode(
        x=alt.X("ccy_mac_perc:Q", bin=True),
        y=alt.Y("count()", axis=alt.Axis(title="Orgs Count")),
    )
    .properties(width=500, height=350, title="Distribution of Annual % Mac Minutes")
)

chart3_ccy = (
    alt.Chart(ccy_android)
    .mark_bar()
    .encode(
        x=alt.X("ccy_android_perc:Q", bin=True),
        y=alt.Y("count()", axis=alt.Axis(title="Orgs Count")),
    )
    .properties(width=500, height=350, title="Distribution of Annual % Android Minutes")
)

chart4_ccy = (
    alt.Chart(ccy_ios)
    .mark_bar()
    .encode(
        x=alt.X("ccy_ios_perc:Q", bin=True),
        y=alt.Y("count()", axis=alt.Axis(title="Orgs Count")),
    )
    .properties(width=500, height=350, title="Distribution of Annual % iOS Minutes")
)

# combine the four charts into a grid
grid_ccy = alt.vconcat(
    alt.hconcat(chart1_ccy, chart2_ccy, spacing=200),
    alt.hconcat(chart3_ccy, chart4_ccy, spacing=200),
).resolve_scale(y="independent")

# display the grid
st.altair_chart(grid_ccy)


# Takeaways
st.subheader("Takeaways: ")

st.write(
    """
- The summary above illustrates the resource usage of enterprise clients in their testing activities:
    - Among the top 50% of clients, 71% of their testing occurs on Windows, 7% on Mac, 1% on Android, and 0% on iOS.
    - Among the top 90% of clients, 100% of their testing occurs on Windows, 64% on Mac, 34% on Android, and 30% on iOS.
    """
)
