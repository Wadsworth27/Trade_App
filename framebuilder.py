import pandas as pd
import requests
import json
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


class FrameBuilder:
    def __init__(
        self, name_to_player_ids, league_id, pick_endpoint, future_picks_df=None
    ):
        # Ititalize variables
        self.name_to_player_ids = name_to_player_ids
        self.league_id = league_id
        self.pick_endpoint = pick_endpoint
        self.player_id_to_name = {v: k for k, v in self.name_to_player_ids.items()}
        # Get Picks from Fleaflicker
        self.get_current_picks()
        # Get csv of updated future picks if existing
        self.future_picks_df = future_pick_df
        if self.future_picks_df is not None:
            max_round = max(self.current_pick_df["season"])
            self.future_picks_df = self.future_picks_df[
                self.future_picks_df["season"] > max_round
            ].copy()
        # Create final Dataframe
        self.create_all_picks_df()

    def build_future_df(self, start_year, end_year):
        frame = pd.DataFrame()
        for player, player_id in self.name_to_player_ids.items():
            for i in range(start_year, end_year):
                for j in range(1, 21):
                    frame = pd.concat(
                        [
                            frame,
                            pd.DataFrame(
                                {
                                    "traded": False,
                                    "season": i,
                                    "lost": False,
                                    "ownedBy.id": player_id,
                                    "ownedBy.name": player,
                                    "originalOwner.id": player_id,
                                    "originalOwner.name": player,
                                    "slot.round": j,
                                },
                                index=[0],
                            ),
                        ]
                    )
        return frame

    def convert_id_to_name(self, player_id):
        return self.player_id_to_name[player_id]

    def format_dataframe(self, df):
        df = df[
            [
                "traded",
                "season",
                "lost",
                "ownedBy.id",
                "ownedBy.name",
                "originalOwner.id",
                "originalOwner.name",
                "slot.round",
            ]
        ].copy()
        df = df.query("`slot.round` <11")
        df["originalOwner.id"].fillna(df["ownedBy.id"], inplace=True)
        df["originalOwner.name"] = df["originalOwner.id"].apply(self.convert_id_to_name)
        df["ownedBy.name"] = df["ownedBy.id"].apply(self.convert_id_to_name)
        df["originalOwner.id"] = df["originalOwner.id"].astype(int)
        df["lost"] = df["lost"].apply(lambda x: x == "True" or x == True)

        return df

    def update_pick(self, year, pick_round, traded_from, traded_to):
        # update to full df
        self.future_picks_df.loc[
            (self.future_picks_df["originalOwner.id"] == traded_from)
            & (self.future_picks_df["season"] == year)
            & (self.future_picks_df["slot.round"] == pick_round),
            "ownedBy.id",
        ] = traded_to
        self.future_picks_df.loc[
            (self.future_picks_df["originalOwner.id"] == traded_from)
            & (self.future_picks_df["season"] == year)
            & (self.future_picks_df["slot.round"] == pick_round),
            "ownedBy.name",
        ] = self.player_id_to_name[traded_to]
        self.future_picks_df.loc[
            (self.future_picks_df["originalOwner.id"] == traded_from)
            & (self.future_picks_df["season"] == year)
            & (self.future_picks_df["slot.round"] == pick_round),
            "traded",
        ] = True
        new_row = self.future_picks_df.loc[
            (self.future_picks_df["originalOwner.id"] == traded_from)
            & (self.future_picks_df["season"] == year)
            & (self.future_picks_df["slot.round"] == pick_round),
            :,
        ].copy()
        self.future_picks_df.loc[
            (self.future_picks_df["originalOwner.id"] == traded_from)
            & (self.future_picks_df["season"] == year)
            & (self.future_picks_df["slot.round"] == pick_round),
            "lost",
        ] = True
        self.future_picks_df = pd.concat([new_row, self.future_picks_df])
        self.future_picks_df = self.format_dataframe(self.future_picks_df)

        # Save the changes -- implement later
        self.create_all_picks_df()
        print("pick_updated")

    def get_current_picks(self):
        self.current_pick_df = pd.DataFrame()
        for team_id in self.player_id_to_name.keys():
            response = requests.get(
                PICK_ENDPOINT, params={"league_id": LEAGUE_ID, "team_id": team_id}
            )
            json_response = response.json()["picks"]
            df = pd.json_normalize(json_response)
            df = self.format_dataframe(df)
            self.current_pick_df = pd.concat([self.current_pick_df, df])

    def create_all_picks_df(self):
        self.all_picks_df = self.format_dataframe(
            pd.concat([self.current_pick_df, self.future_picks_df])
        )

    def return_user_facing_df(self):
        user_df = self.all_picks_df.copy()
        user_df.rename(
            {
                "traded": "Pick Traded",
                "season": "Season",
                "lost": "Pick Lost",
                "ownedBy.name": "Pick Owner",
                "originalOwner.name": "Original Owner",
                "slot.round": "Pick Round",
            },
            axis=1,
            inplace=True,
        )

        return user_df[
            [
                "Season",
                "Pick Round",
                "Pick Owner",
                "Original Owner",
                "Pick Traded",
                "Pick Lost",
            ]
        ]
