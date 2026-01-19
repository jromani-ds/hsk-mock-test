import json
from hsk.data_engine import DataEngine
from hsk.test_engine import HSKTestEngine

def verify_v13_doctorate_standard():
    print("--- HSK v13.0 Doctorate Standard Verification ---\n")
    engine = DataEngine()
    test_engine = HSKTestEngine(9, engine, num_questions=10)
    
    for i, q in enumerate(test_engine.questions):
        print(f"Question {i+1}:")
        print(f"  Target:       {q.correct_answer}")
        
        target_word = next((w for w in test_engine.words if w.hanzi == q.correct_answer), None)
        if target_word:
            print(f"  Target Level: {target_word.level} {'[PASS]' if target_word.level == 9 else '[FAIL]'}")
        
        print(f"  Context:      {q.prompt}")
        print(f"  Options:      {q.options}")
        
        # Check Character Kinship
        target_chars = set(q.correct_answer)
        kinship_count = 0
        for opt in q.options:
            if opt == q.correct_answer: continue
            if set(opt).intersection(target_chars):
                kinship_count += 1
        
        print(f"  Kinship Density: {kinship_count}/3 distractors")
        
        # Check POS Symmetry
        if target_word:
            target_pos = set(target_word.pos) if target_word.pos else set()
            pos_matches = 0
            for opt in q.options:
                opt_word = next((w for w in test_engine.words if w.hanzi == opt), None)
                if opt_word and opt_word.pos:
                    if set(opt_word.pos).intersection(target_pos):
                        pos_matches += 1
            print(f"  POS Symmetry: {pos_matches}/4 options")
            
        print("-" * 40)

if __name__ == "__main__":
    verify_v13_doctorate_standard()
