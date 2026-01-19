import json
from hsk.data_engine import DataEngine
from hsk.test_engine import HSKTestEngine

def verify_v12_precision_engine():
    print("--- HSK v12.0 Precision Engine Verification ---\n")
    engine = DataEngine()
    test_engine = HSKTestEngine(9, engine, num_questions=10)
    
    factoid_keywords = {"二氧化碳", "氧气", "光合作用", "肺", "太阳系", "原子", "分子", "科学发现"}
    
    for i, q in enumerate(test_engine.questions):
        print(f"Question {i+1}:")
        print(f"  Target:       {q.correct_answer}")
        
        target_word = next((w for w in test_engine.words if w.hanzi == q.correct_answer), None)
        if target_word:
            print(f"  Target Level: {target_word.level} {'[PASS]' if target_word.level >= 7 else '[FAIL]'}")
        
        # Check for Factoids
        is_factoid = any(k in q.prompt for k in factoid_keywords)
        print(f"  Is Factoid?   {'YES [FAIL]' if is_factoid else 'NO [PASS]'}")
        
        print(f"  Distractors:  {q.options}")
        
        # Check Semantic Domain Overlap
        if target_word:
            target_keywords = set(target_word.meaning.lower().replace(";", "").replace(",", "").replace("to ", "").split())
            domain_traps = []
            for opt in q.options:
                if opt == q.correct_answer: continue
                opt_word = next((w for w in test_engine.words if w.hanzi == opt), None)
                if opt_word:
                    opt_keywords = set(opt_word.meaning.lower().replace(";", "").replace(",", "").replace("to ", "").split())
                    if target_keywords.intersection(opt_keywords):
                        domain_traps.append(opt)
            print(f"  Domain Traps: {domain_traps}")
            
        print("-" * 40)

if __name__ == "__main__":
    verify_v12_precision_engine()
