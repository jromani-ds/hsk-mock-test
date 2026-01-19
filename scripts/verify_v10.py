from hsk.data_engine import DataEngine
from hsk.test_engine import HSKTestEngine


def verify_v10_near_native():
    print("--- HSK v10.0 Near-Native Verification ---\n")
    engine = DataEngine()
    test_engine = HSKTestEngine(9, engine, num_questions=10)

    academic_markers = {
        "哲学",
        "政治",
        "经济",
        "体系",
        "范畴",
        "逻辑",
        "理论",
        "机制",
        "策略",
        "规律",
    }

    for i, q in enumerate(test_engine.questions):
        print(f"Question {i + 1}:")
        print(f"  Target:     {q.correct_answer}")

        # Check meaning keywords for academic weight
        target_word = next((w for w in test_engine.words if w.hanzi == q.correct_answer), None)
        is_academic = (
            any(
                k in target_word.meaning.lower() or k in target_word.hanzi for k in academic_markers
            )
            if target_word
            else False
        )

        print(f"  Register:   {'Academic/Formal' if is_academic else 'General Advanced'}")
        print(f"  Complexity: {len(q.prompt)} chars, {q.prompt.count('，')} clauses")
        print(f"  Traps:      {q.options}")

        # Check for semantic overlap in distractors
        if target_word:
            target_keywords = set(
                target_word.meaning.lower().replace(";", "").replace(",", "").split()
            )
            semantic_traps = []
            for opt in q.options:
                if opt == q.correct_answer:
                    continue
                opt_word = next((w for w in test_engine.words if w.hanzi == opt), None)
                if opt_word:
                    opt_keywords = set(
                        opt_word.meaning.lower().replace(";", "").replace(",", "").split()
                    )
                    if target_keywords.intersection(opt_keywords):
                        semantic_traps.append(opt)
            print(f"  Semantic Synonyms: {semantic_traps}")

        print("-" * 40)


if __name__ == "__main__":
    verify_v10_near_native()
