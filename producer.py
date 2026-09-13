import time
import json
from kafka import KafkaProducer
from statsbombpy import sb

producer = KafkaProducer(
    bootstrap_servers="localhost:9092",
    value_serializer=lambda v: json.dumps(v).encode("utf-8")
)

def stream_match_events(match_id:int, player_name: str, delay: float = 0.1):
    events = sb.events(match_id=match_id)
    matching_names = events["player"].dropna().unique()
    full_name = [p for p in matching_names if player_name in p][0]
    player_events = events[events["player"] == full_name]

    for _, row in player_events.iterrows():
        message = {
            "match_id": match_id,
            "player_id": int(row["player_id"]),
            "player": row["player"],
            "event_type": row["type"],
            "pass_outcome": row.get("pass_outcome"),
            "shot_outcome": row.get("shot_outcome"),
            "duel_outcome": row.get("duel_outcome"),
        }

        producer.send("player-events", value=message)
        print("Sent:", message["event_type"])
        time.sleep(delay)

    producer.flush()
    print("\nAll events sent.")

if __name__ == "__main__":
    stream_match_events(match_id=7531, player_name="Messi", delay=0.1)