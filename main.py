from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
import joblib
import sqlite3

def get_player_skills(cursor, player_id):
    cursor.execute("""
    select
        mu,
        sigma, 
        total_assists, 
        total_healing, 
        total_kills,
        total_deaths,          
        matches_played
    from player_skills
    where player_id = ?
    """, (player_id,)
    ) 
    return cursor.fetchone()

app = FastAPI()

pipeline = joblib.load("TF2_prediction.pkl")

# 1. Input validation ONLY
class MatchInput(BaseModel):
    blue_team: List[str]
    red_team: List[str]


# 2. Feature engineering (separate function)
def get_features(blue_players, red_players, cursor):
    blue_ts_score = 0
    red_ts_score = 0
    avg_blue_kills = 0
    avg_red_kills = 0
    avg_blue_deaths = 0
    avg_red_deaths = 0
    avg_blue_assists = 0
    avg_red_assists = 0

    if not blue_players:
        raise HTTPException(status_code=400, detail="Missing blue team")
    if not red_players:
        raise HTTPException(status_code=400, detail="Missing red team")

    for player_id in red_players:
        mu, sigma, assists, _, kills, deaths, matches = get_player_skills(cursor, player_id)

        if matches == 0:
            continue  # or handle differently

        red_ts_score += mu - 3 * sigma
        avg_red_kills += kills / matches
        avg_red_deaths += deaths / matches
        avg_red_assists += assists / matches

    for player_id in blue_players:
        mu, sigma, assists, _, kills, deaths, matches = get_player_skills(cursor, player_id)

        if matches == 0:
            continue

        blue_ts_score += mu - 3 * sigma
        avg_blue_kills += kills / matches
        avg_blue_deaths += deaths / matches
        avg_blue_assists += assists / matches

    n_red = len(red_players)
    n_blue = len(blue_players)

    return (
        red_ts_score/n_red - blue_ts_score/n_blue,
        avg_red_kills/n_red - avg_blue_kills/n_blue,
        avg_red_assists/n_red - avg_blue_assists/n_blue,
        avg_red_deaths/n_red - avg_blue_deaths/n_blue
    )


# 3. API route
@app.post("/predict")
def predict(data: MatchInput):
    conn = sqlite3.connect("tf2.db")
    cursor = conn.cursor()

    features = get_features(data.blue_team, data.red_team, cursor)

    conn.close()

    prediction = pipeline.predict([features])[0]

    return {"prediction": int(prediction)}