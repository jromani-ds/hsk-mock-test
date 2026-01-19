import json
from hsk.data_engine import DataEngine
from hsk.test_engine import HSKTestEngine

def verify_v11_c2_standard():
    print("--- HSK v11.0 C2 Standard Verification ---\n")
    engine = DataEngine()
    test_engine = HSKTestEngine(9, engine, num_questions=10)
    
    rhetorical_markers = ["与其", "毋宁", "甚至", "即便", "既然", "不仅", "岂", "何必", "固然", "何况"]
    
    for i, q in enumerate(test_engine.questions):
        print(f"Question {i+1}:")
        print(f"  Target:     {q.correct_answer}")
        
        # Check for Rhetorical Marker
        found_markers = [m for m in rhetorical_markers if m in q.prompt]
        print(f"  Rhetoric:   {found_markers if found_markers else 'Structural'}")
        print(f"  Complexity: {len(q.prompt)} chars")
        
        # Check for Information Leak (Answer appearing in prompt)
        clean_prompt = q.prompt.replace("____", "")
        if q.correct_answer in clean_prompt:
             print("  [ALERT] Information Leak Detected!")
        
        # Check distractor semantic similarity
        target_word = next((w for w in test_engine.words if w.hanzi == q.correct_answer), None)
        if target_word:
            target_keywords = set(target_word.meaning.lower().replace(";", "").replace(",", "").replace("to ", "").split())
            synonym_traps = []
            for opt in q.options:
                if opt == q.correct_answer: continue
                opt_word = next((w for w in test_engine.words if w.hanzi == opt), None)
                if opt_word:
                    opt_keywords = set(opt_word.meaning.lower().replace(";", "").replace(",", "").replace("to ", "").split())
                    if target_keywords.intersection(opt_keywords):
                        synonym_traps.append(opt)
            print(f"  Synonym Traps: {synonym_traps}")
            
        print("-" * 40)

if __name__ == "__main__":
    verify_v11_c2_standard()
