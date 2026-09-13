from typing import TypedDict, Optional
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from langgraph.types import interrupt, Command

from step1_evaluate import evaluate_player, PlayerEval
from statsbomb_input import get_player_stats

class GraphState(TypedDict):
    stats: dict
    evaluation: Optional[PlayerEval]
    manager_decision: Optional[str]
    final_status: Optional[str]


def evaluate_node(state: GraphState) -> GraphState:
    result = evaluate_player(state["stats"])
    state['evaluation']=result
    return state

def check_flag_node(state: GraphState) -> GraphState:
    return state

def route_after_check(state: GraphState) -> str:
    if state["evaluation"].risk_flag:
        return "await_approval"
    else:
        state["final_status"]=state["evaluation"].recommendation
        return "end"

def await_approval_node(state: GraphState) -> GraphState:
    decision = interrupt({
        "message" : "Manager review needed",
        "evaluation" : state["evaluation"].model_dump()
    })
    state["manager_decision"] = decision
    return state

def apply_decision_node(state: GraphState) -> GraphState:
    state["final_status"] = state["manager_decision"]
    return state

builder = StateGraph(GraphState)
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
    real_stats = get_player_stats(match_id=7531, player_name="Messi")
    print("Fetched stats:", real_stats)
#     fake_stats = {
#     "player_id": 22, "minutes_played": 90, "pass_accuracy": 75.0,
#     "shots": 3, "goals": 1, "tackles": 2, "interceptions": 1, "duels_won": 4
# }

    config = {"configurable" : {"thread_id": f"player-{real_stats['player_id']}"}}
    result = graph.invoke({"stats" : real_stats}, config)
    print("First run result:", result)

    if "__interrupt__" in result:
        print("\n>>> Paused for manager approval <<<")
        print("Evaluation:", result["__interrupt__"])
        manager_input = input("Enter manager decision (advance/reject): ")
        # manager_input = "advance"
        result = graph.invoke(Command(resume=manager_input), config)
        print("After manager decision:", result)