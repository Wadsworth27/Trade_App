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
st.subheader("All Picks in Range")
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
# Scatter Plot Start
scatter_data = (
    working_data[(~working_data["Pick Lost"]) & (working_data["Pick Round"] < 8)]
    .groupby(["Season", "Pick Round", "Pick Owner"])
    .count()
    .reset_index()
)
scatter_data.rename({"Original Owner": "# of Picks"}, axis=1, inplace=True)


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
st.plotly_chart(pie_fig, use_container_width=True)


print(options)
