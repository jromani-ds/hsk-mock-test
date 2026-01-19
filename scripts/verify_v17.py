from hsk.data_engine import DataEngine
from hsk.test_engine import HSKTestEngine


def audit_level(level: int):
    print(f"\n--- AUDITING LEVEL {level} ---")
    data_engine = DataEngine()
    engine = HSKTestEngine(level=level, data_engine=data_engine, num_questions=5)

    questions = engine.questions
    pos_parallelism = 0
    len_parallelism = 0
    total = len(questions)

    if total == 0:
        print("No questions generated.")
        return

    for q in questions:
        # Get target POS and length
        target_hanzi = q.correct_answer
        # Finding the target word object
        target_word = next((w for w in engine.words if w.hanzi == target_hanzi), None)

        print(f"Q: {q.prompt[:50]}...")
        print(
            f"Target: {target_hanzi} (POS: {target_word.pos if target_word else '?'}, Level: {target_word.level if target_word else '?'})"
        )
        print(f"Options: {q.options}")

        # Audit options
        match_pos = True
        match_len = True
        target_len = len(target_hanzi)
        target_pos_set = set(target_word.pos) if target_word and target_word.pos else set()

        for opt in q.options:
            opt_word = next((w for w in engine.words if w.hanzi == opt), None)
            if not opt_word:
                continue

            if len(opt) != target_len:
                match_len = False
            if target_pos_set and opt_word.pos:
                if not set(opt_word.pos).intersection(target_pos_set):
                    match_pos = False

        if match_pos:
            pos_parallelism += 1
        if match_len:
            len_parallelism += 1

    print(f"POS Parallelism: {pos_parallelism}/{total}")
    print(f"Length Parallelism: {len_parallelism}/{total}")


if __name__ == "__main__":
    for l in [1, 4, 9]:
        audit_level(l)
