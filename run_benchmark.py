import json
from step1_evaluate import evaluate_player

def load_benchmark_cases(path: str = "benchmark_cases.json") -> list[dict]:
    with open(path) as f:
        return json.load(f)

def run_benchmark():
    cases = load_benchmark_cases()
    results = []

    for case in cases:
        evaluation = evaluate_player(case["stats"])
        passed = evaluation.recommendation == case["expected_decision"]

        results.append({
            "case_id": case["case_id"],
            "expected": case["expected_decision"],
            "actual": evaluation.recommendation,
            "passed": passed
        })

    return results

if __name__ == "__main__":
    results = run_benchmark()

    for r in results:
        status = "PASS" if r["passed"] else "FAIL"
        print(f"[{status}] {r['case_id']}: expected={r['expected']}, actual={r['actual']}")

    total = len(results)
    passed_count = sum(1 for r in results if r["passed"])
    print(f"\n{passed_count}/{total} passed")