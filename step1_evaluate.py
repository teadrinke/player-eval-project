import os 
from dotenv import load_dotenv
from typing import List, Literal
from langchain_anthropic import ChatAnthropic
from pydantic import BaseModel, Field

load_dotenv()

class PlayerEval(BaseModel):
    player_id: int
    overall_score: int = Field(description="Score out of 100")
    strengths: List[str]
    weaknesses: List[str]
    recommendation: Literal["advance", "reject"]
    risk_flag: bool

llm = ChatAnthropic(model = "claude-haiku-4-5-20251001")
structured_llm = llm.with_structured_output(PlayerEval)

def evaluate_player(stats: dict) -> PlayerEval:
    prompt = f'''
You are a football performance analyst.
Evaluate this player based on the stats below.

Stats:
{stats}

Give an overall_score (0-100), list strengths, list weaknesses,
a recommendation (advance/reject), and a risk_flag (true if this
player's performance is borderline/risky and needs human review).
'''
    result = structured_llm.invoke(prompt)
    return result

if __name__ == "__main__":
    fake_stats = {
        "player_id": 17,
        "minutes_played": 90,
        "pass_accuracy": 88.9,
        "shots": 4,
        "goals": 1,
        "tackles": 5,
        "interceptions": 3,
        "duels_won": 7
    }

    evaluation = evaluate_player(fake_stats)
    print(evaluation)
    print(evaluation.model_dump_json(indent=2))