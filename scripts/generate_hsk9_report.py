import json
from hsk.data_engine import DataEngine
from hsk.test_engine import HSKTestEngine

def generate_hsk9_audit_data():
    engine = DataEngine()
    # Ensure all high-band data is loaded
    for l in range(7, 10):
        engine.load_level_data(l)
    
    test_engine = HSKTestEngine(9, engine, num_questions=10)
    
    report = []
    for q in test_engine.questions:
        target_word = next((w for w in test_engine.words if w.hanzi == q.correct_answer), None)
        
        # Calculate kinship for each option
        options_meta = []
        for opt in q.options:
            opt_word = next((w for w in test_engine.words if w.hanzi == opt), None)
            shared = set(opt).intersection(set(q.correct_answer))
            options_meta.append({
                "hanzi": opt,
                "shared_chars": list(shared),
                "pos": opt_word.pos if opt_word else [],
                "level": opt_word.level if opt_word else 0,
                "meaning": opt_word.meaning if opt_word else ""
            })
            
        report.append({
            "id": q.id,
            "target": q.correct_answer,
            "prompt": q.prompt,
            "options": options_meta
        })
    
    print(json.dumps(report, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    generate_hsk9_audit_data()
