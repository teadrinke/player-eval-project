import json
import random

random.seed(42)  # reproducible - same "random" cases every time this runs

def make_case(case_id: str) -> dict:
    pass_accuracy = round(random.uniform(30, 95), 1)
    shots = random.randint(0, 12)
    goals = random.randint(0, min(shots, 3))
    tackles = random.randint(0, 8)
    interceptions = random.randint(0, 5)
    duels_won = random.randint(0, 10)

    stats = {
        "player_id": int(case_id.split("_")[1]),
        "minutes_played": 90,
        "pass_accuracy": pass_accuracy,
        "shots": shots,
        "goals": goals,
        "tackles": tackles,
        "interceptions": interceptions,
        "duels_won": duels_won
    }

    # Simple, transparent proxy rule for "expected" - NOT ground truth,
    # just a consistent baseline to catch regressions against.
    contribution_score = (
        (pass_accuracy / 100) * 30
        + goals * 15
        + tackles * 3
        + interceptions * 3
        + duels_won * 2
    )
    expected_decision = "advance" if contribution_score >= 40 else "reject"

    return {
        "case_id": case_id,
        "stats": stats,
        "expected_decision": expected_decision
    }

if __name__ == "__main__":
    cases = [make_case(f"case_{i:03d}") for i in range(1, 101)]

    with open("benchmark_cases.json", "w") as f:
        json.dump(cases, f, indent=2)

    advance_count = sum(1 for c in cases if c["expected_decision"] == "advance")
    print(f"Generated 100 cases: {advance_count} advance, {100 - advance_count} reject")