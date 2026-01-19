from hsk.constants import QUESTION_TYPE_MC
from hsk.data_engine import DataEngine
from hsk.test_engine import HSKTestEngine


def simulate_level(level: int):
    print(f"\n{'=' * 40}")
    print(f"SIMULATING EXAM - LEVEL {level}")
    print(f"{'=' * 40}")

    try:
        data_engine = DataEngine()
        engine = HSKTestEngine(level, data_engine)
    except Exception as e:
        print(f"Failed to load level {level}: {e}")
        return

    question_count = 0
    while True:
        q = engine.get_next_question()
        if not q:
            break

        question_count += 1
        print(f"\n[Q{question_count}] Type: {q.type}")
        print(f"Prompt: {q.prompt}")

        if q.type == QUESTION_TYPE_MC:
            print("Options:")
            for opt in q.options:
                print(f" - {opt}")

        # Simulate answering
        # 50% chance to be correct to test pass/fail borderline or varied results
        # actually let's force a mixture:
        # For Q1-3 Correct, Q4-5 Incorrect
        should_be_correct = question_count <= 3
        answer = q.correct_answer if should_be_correct else "WRONG ANSWER"

        engine.submit_answer(q, answer)
        print(
            f"Action: Answered '{answer[:20]}...' -> {'Correct' if should_be_correct else 'Incorrect'}"
        )

    # Results
    result = engine.calculate_result()
    print("\n--- RESULTS ---")
    print(f"Score: {result.score}%")
    print(f"Passed: {result.passed}")
    print(f"Details: {result.details}")
    if result.grammar_issues:
        print("Grammar Audit issues found.")


if __name__ == "__main__":
    for level in [1, 4, 9]:
        simulate_level(level)
