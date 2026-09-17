import json
from datetime import datetime, timezone

TRACK_FILE = "traces.jsonl"

def log_step(trace_id: str, player_id: int, step: str, **extra):
    entry = {
        "trace_id": trace_id,
        "player_id": player_id,
        "step": step,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        **extra
    }

    with open(TRACK_FILE, "a") as f:
        f.write(json.dumps(entry) + "\n")
