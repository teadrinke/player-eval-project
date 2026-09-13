from statsbombpy import sb
import pandas as pd

def get_player_stats(match_id: int, player_name: str) -> dict:
    events = sb.events(match_id=match_id)

    matching_names = events["player"].dropna().unique()
    full_name = [p for p in matching_names if player_name in p][0]

    player_events = events[events["player"] == full_name]

    passes = player_events[player_events["type"] == "Pass"]
    completed_passes = passes[passes["pass_outcome"].isna()] # NaN outcome = completed

    shots = player_events[player_events["type"] == "Shot"]
    goals = shots[shots["shot_outcome"] == "Goal"]

    tackles = player_events[player_events["type"] == "Duel"]
    tackles_won = tackles[tackles["duel_outcome"].isin(["Won", "Success"])]

    interceptions = player_events[player_events["type"]=="Interception"]

    stats = {
        "player_id" : int(player_events["player_id"].iloc[0]),
        "minutes_played": 90,
        "pass_accuracy": round(len(completed_passes)/len(passes) * 100, 1) if len(passes) > 0 else 0,
        "shots" : len(shots),
        "goals" : len(goals),
        "tackles": len(tackles),
        "interceptions" : len(interceptions),
        "duels_won" : len(tackles_won)
    }

    return stats

if __name__ == "__main__":
    stats = get_player_stats(match_id=7531, player_name="Messi")
    print(stats)

# from statsbombpy import sb

# events = sb.events(match_id=7531)
# players = events["player"].dropna().unique()
# messi_matches = [p for p in players if "Messi" in p]
# print(messi_matches)