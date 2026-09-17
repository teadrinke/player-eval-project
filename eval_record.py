from pydantic import BaseModel
from typing import Optional
from step1_evaluate import PlayerEval
import uuid

class EvalRecord(BaseModel):
    trace_id: str
    player_id: int
    stats: dict
    evaluation: Optional[PlayerEval] = None
    manager_decision: Optional[str] = None
    final_status: Optional[str] = None

def create_eval_record(player_id: int, stats: dict) -> EvalRecord:
    return EvalRecord(
        trace_id=str(uuid.uuid4()),
        player_id=player_id,
        stats=stats
    )

if __name__ == "__main__":
    record = create_eval_record(player_id=17, stats={"pass_accuracy": 88.90})
    print(record)