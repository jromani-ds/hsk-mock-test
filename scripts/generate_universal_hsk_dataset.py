
import json
from hsk.data_engine import DataEngine
from hsk.test_engine import HSKTestEngine

def generate_dataset():
    data_engine = DataEngine()
    dataset = {}

    for level in range(1, 10):
        print(f"Generating Level {level}...")
        try:
            # Generate 10 questions for the level
            engine = HSKTestEngine(level=level, data_engine=data_engine, num_questions=10)
            
            level_questions = []
            for q in engine.questions:
                # Find the target word object to get the level and meaning context
                target_word = next((w for w in engine.words if w.hanzi == q.correct_answer), None)
                
                q_data = {
                    "question_id": q.id,
                    "prompt": q.prompt,
                    "correct_answer": q.correct_answer,
                    "options": q.options,
                    "metadata": {
                        "target_level": target_word.level if target_word else level,
                        "target_meaning": target_word.meaning if target_word else "",
                        "target_pos": target_word.pos if target_word else []
                    }
                }
                
                # Enrich options with meanings for the external LLM to audit discrimination
                enriched_options = []
                for opt in q.options:
                    opt_word = next((w for w in engine.words if w.hanzi == opt), None)
                    enriched_options.append({
                        "hanzi": opt,
                        "meaning": opt_word.meaning if opt_word else "N/A",
                        "pos": opt_word.pos if opt_word else []
                    })
                q_data["options_detail"] = enriched_options
                
                level_questions.append(q_data)
            
            dataset[f"HSK_Level_{level}"] = level_questions
        except Exception as e:
            print(f"Error generating Level {level}: {e}")
            dataset[f"HSK_Level_{level}"] = []

    output_path = "hsk_universal_dataset.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(dataset, f, ensure_ascii=False, indent=2)
    
    print(f"Dataset saved to {output_path}")

if __name__ == "__main__":
    generate_dataset()
