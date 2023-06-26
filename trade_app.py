import pandas as pd
import requests
import json
import streamlit as st
import plotly.express as px
from framebuilder import FrameBuilder

import warnings

warnings.filterwarnings("ignore")

NAME_TO_PLAYER_IDS = {
    "Steve": 1335769,
    "Ryan": 1340595,
    "Jimmy": 1346341,
    "Sam": 1335806,
    "Jake B": 1344282,
    "Kooch": 1344276,
    "Ethan": 1335962,
    "Jake M": 1348551,
}
PLAYER_ID_TO_NAME = {v: k for k, v in NAME_TO_PLAYER_IDS.items()}
LEAGUE_ID = 199769
PICK_ENDPOINT = "https://www.fleaflicker.com/api/FetchTeamPicks"
future_pick_df = pd.read_csv("future_pick.csv")


@st.cache_data
def load_data():
    framebuilder = FrameBuilder(
        NAME_TO_PLAYER_IDS, LEAGUE_ID, PICK_ENDPOINT, future_pick_df
    )
    return framebuilder.return_user_facing_df()


data = load_data()

st.title("Chad's SOTH Trade App")


with st.sidebar:
    st.header("Player Select")
    options = st.multiselect(
        "# Player Select:",
        options=data["Original Owner"].unique(),
        default=data["Original Owner"].unique(),
    )
    st.header("Year Select")
    min_year_filter, max_year_filter = st.slider("Year", 2023, 2030, (2023, 2025))
st.subheader(f"Diplaying All Picks From {min_year_filter} to {max_year_filter}")
st.info(
    "Use the sidebar to change year range and players displayed. Click into any chart and return to original state with a double click."
)
working_data = data.loc[
    (data["Season"] >= min_year_filter)
    & (data["Season"] <= max_year_filter)
    & (data["Pick Owner"].isin(options))
]
# st.write(working_data)

# Display Bar Graph of picks in range
bar_data = (
    working_data[(~working_data["Pick Lost"]) & (working_data["Pick Round"] < 8)]
    .groupby(["Pick Round", "Pick Owner"])
    .count()
    .reset_index()
)
bar_data.rename({"Original Owner": "# of Picks"}, axis=1, inplace=True)
bar_fig = px.bar(
    bar_data,
    x="Pick Round",
    y="# of Picks",
    color="Pick Owner",
)
st.plotly_chart(bar_fig, use_container_width=True)
st.divider()
####Value Subburst####
st.header("Pick Values By Season")
st.info(
    "Picks are scored as 1000 for 1st, 350 for 2nd, 125 for 3rd etc. and adjusted for last years finishing position. Further out picks are discounted 10% a year."
)
sunburst_data = (
    working_data[(~working_data["Pick Lost"]) & (working_data["Pick Round"] < 8)]
    .groupby(["Season", "Pick Owner"])
    .sum()["Pick Value"]
    .reset_index()
)

sunburst_fig = px.sunburst(
    sunburst_data,
    path=["Pick Owner", "Season"],
    values="Pick Value",
    height=750,
    hover_data="Pick Value",
)
st.plotly_chart(sunburst_fig, use_container_width=True)
###### Value Scatter Plot Start ####

scatter_data = (
    working_data[(~working_data["Pick Lost"]) & (working_data["Pick Round"] < 8)]
    .groupby(["Season", "Pick Owner"])
    .sum()["Pick Value"]
    .reset_index()
)
scatter_data.rename({"Original Owner": "Sum Of Pick Values"}, axis=1, inplace=True)
scatter_fig = px.scatter(scatter_data, x="Season", y="Pick Owner", size="Pick Value")
scatter_fig.update_xaxes(tickvals=scatter_data["Season"].unique())
st.plotly_chart(scatter_fig)


#####Pie Chart Start ####

st.header("Picks By Round")
round_select = st.slider("Round", 1, 8, 1)
pie_data = (
    working_data[
        (~working_data["Pick Lost"]) & (working_data["Pick Round"] == round_select)
    ]
    .groupby(["Pick Round", "Pick Owner"])
    .count()
    .reset_index()
)

pie_data.rename({"Original Owner": "# of Picks"}, axis=1, inplace=True)
pie_fig = px.pie(data_frame=pie_data, values="# of Picks", names="Pick Owner")
pie_fig.update_traces(textinfo="value")
st.plotly_chart(pie_fig, use_container_width=True)


##### All pick view start ######

st.write("Full Pick View")
pick_owner = st.selectbox("Player Select", options=data["Original Owner"].unique())
pick_view_data = working_data.copy()
st.write("Owned Picks")
st.dataframe(
    working_data.query("`Pick Lost` == False and `Pick Owner` == @pick_owner")
    .sort_values(by=["Season", "Pick Round"])
    .reset_index(drop=True)
)
st.write("Lost Picks")
st.dataframe(
    working_data.query("`Pick Lost` == True and `Original Owner` == @pick_owner")
    .sort_values(by=["Season", "Pick Round"])
    .reset_index(drop=True)
)
