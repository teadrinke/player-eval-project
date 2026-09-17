from typing import TypedDict, Optional
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from langgraph.types import interrupt, Command

from step1_evaluate import evaluate_player, PlayerEval
from eval_record import create_eval_record, EvalRecord
from statsbomb_input import get_player_stats
from tracer import log_step


def evaluate_node(record: EvalRecord) -> EvalRecord:
    result = evaluate_player(record.stats)
    record.evaluation = result
    log_step(record.trace_id, record.player_id, "evaluation_complete",
              evaluation=result.model_dump())
    return record

def check_flag_node(record: EvalRecord) -> EvalRecord:
    return record

def route_after_check(record: EvalRecord) -> str:
    if record.evaluation.risk_flag:
        log_step(record.trace_id, record.player_id, "awaiting_approval")
        return "await_approval"
    else:
        record.final_status = record.evaluation.recommendation
        log_step(record.trace_id, record.player_id, "auto passed",
                  final_status=record.final_status)
        return "end"

def await_approval_node(record: EvalRecord) -> EvalRecord:
    decision = interrupt({
        "trace_id": record.trace_id,
        "message" : "Manager review needed",
        "evaluation" : record.evaluation.model_dump()
    })
    record.manager_decision = decision
    log_step(record.trace_id, record.player_id, "manager_decided",
              decision=decision)
    return record

def apply_decision_node(record: EvalRecord) -> EvalRecord:
    record.final_status = record.manager_decision
    log_step(record.trace_id, record.player_id, "final_result",
              final_status=record.final_status)
    return record

builder = StateGraph(EvalRecord)
builder.add_node("evaluate", evaluate_node)
builder.add_node("check_flag", check_flag_node)
builder.add_node("await_approval", await_approval_node)
builder.add_node("apply_decision", apply_decision_node)

builder.set_entry_point("evaluate")
builder.add_edge("evaluate", "check_flag")
builder.add_conditional_edges("check_flag", route_after_check, {
    "await_approval" : "await_approval",
    "end" : END
})
builder.add_edge("await_approval", "apply_decision")
builder.add_edge("apply_decision", END)

checkpointer = MemorySaver()
graph = builder.compile(checkpointer=checkpointer)

if __name__ == "__main__":
    fake_stats = {
        "player_id": 17, "minutes_played": 90, "pass_accuracy": 61.2,
        "shots": 1, "goals": 0, "tackles": 1, "interceptions": 0, "duels_won": 2
    }

    record = create_eval_record(player_id=17, stats=fake_stats)
    config = {"configurable": {"thread_id": record.trace_id}}

    result = graph.invoke(record, config)
    print("First run result:", result)

    if "__interrupt__" in result:
        print("\n>>> Paused for manager approval <<<")
        manager_input = input("Enter manager decision (advance/reject): ")
        result = graph.invoke(Command(resume=manager_input), config)
        print("After manager decision:", result)