import pandas as pd
import requests
import json
import streamlit as st
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

st.title("SOTH Trade App")

st.subheader("Raw data")
st.write(data)
