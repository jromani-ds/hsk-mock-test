import json
from hsk.data_engine import DataEngine
from hsk.test_engine import HSKTestEngine

def verify_v8_logic():
    print("--- HSK v8.0 Difficulty Verification ---\n")
    engine = DataEngine()
    test_engine = HSKTestEngine(9, engine, num_questions=10)
    
    for i, q in enumerate(test_engine.questions):
        print(f"Question {i+1}:")
        print(f"  Target:   {q.correct_answer}")
        print(f"  Sentence: {q.prompt}")
        print(f"  Length:   {len(q.prompt)}")
        print(f"  Options:  {q.options}")
        
        # Check if any distractor shares a radical with target (Visual Trap)
        target_word = next((w for w in test_engine.words if w.hanzi == q.correct_answer), None)
        if target_word:
            target_rads = set(target_word.radicals)
            traps = []
            for opt in q.options:
                if opt == q.correct_answer: continue
                opt_word = next((w for w in test_engine.words if w.hanzi == opt), None)
                if opt_word and set(opt_word.radicals).intersection(target_rads):
                    traps.append(opt)
            print(f"  Visual Traps Found: {traps}")
        print("-" * 40)

if __name__ == "__main__":
    verify_v8_logic()
