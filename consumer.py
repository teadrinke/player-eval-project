import json
from kafka import KafkaConsumer

consumer = KafkaConsumer(
    "player-events",
    bootstrap_servers="localhost:9092",
    value_deserializer=lambda m: json.loads(m.decode("utf-8")),
    auto_offset_reset="earliest"
)

stats = {
    "player_id": None,
    "minutes_played": 90,
    "passes"  : 0,
    "completed_passes": 0,
    "shots" : 0,
    "goals" : 0,
    "tackles": 0,
    "tackles_won": 0,
    "interceptions" : 0,
}

def update_stats(event):
    stats["player_id"] = event["player_id"]

    if event["event_type"] == "Pass":
        stats["passes"] += 1
        if event["pass_outcome"] is None:
            stats["completed_passes"] += 1

    elif event["event_type"] == "Shot":
        stats["shots"] += 1
        if event["shot_outcome"] == "Goal":
            stats["goals"] += 1

    elif event["event_type"] == "Duel":
        stats["tackles"] += 1
        if event["duel_outcome"] in ["Won", "Success"]:
            stats["tackles_won"] += 1

    elif event["event_type"] == "Interception":
        stats["interceptions"] += 1

def get_current_snapshot() -> dict:
    passes = stats["passes"]
    pass_accuracy = round(stats["completed_passes"] / passes * 100, 1) if passes > 0 else 0

    return {
        "player_id": stats["player_id"],
        "minutes_played": stats["minutes_played"],
        "pass_accuracy": pass_accuracy,
        "shots": stats["shots"],
        "goals": stats["goals"],
        "tackles": stats["tackles"],
        "interceptions": stats["interceptions"],
        "duels_won": stats["tackles_won"],
    }

if __name__ == "__main__":
    print("Listening for events...\n")
    event_count = 0

    for message in consumer: 
        event = message.value
        update_stats(event)
        event_count += 1

        print(f"Event #{event_count}: {event['event_type']}")

        if event_count % 20 == 0:
            print("\n---Snaphot after", event_count, "events---")
            print(get_current_snapshot())
            print()
