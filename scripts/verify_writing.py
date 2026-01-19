from hsk.test_engine import HSKTestEngine
from hsk.data_engine import DataEngine
from hsk.constants import HSK_EXAM_STRUCTURE

def verify_writing_prompts():
    data_engine = DataEngine()
    
    print("Verifying Writing Prompts Configuration...")
    
    levels_to_test = [5, 6, 9]
    
    for level in levels_to_test:
        print(f"\n--- Checking Level {level} ---")
        try:
            # Force high number of questions to ensure writing question is triggered?
            # Or just check the private method logic
            engine = HSKTestEngine(level, data_engine, num_questions=5) # 5 is min for writing trigger
            
            # Manually trigger creation to see the prompt text
            q = engine._create_writing_question()
            if q:
                print(f"✅ Generated Type: {q.type}")
                print(f"📝 Prompt: {q.prompt}")
                
                # Validation Logic
                if level == 5 and "using these words" in q.prompt:
                    print("--> Correct (Vocab Composition)")
                elif level == 6 and "narrative essay" in q.prompt:
                    print("--> Correct (Narrative)")
                elif level == 9 and "argumentative thesis" in q.prompt:
                    print("--> Correct (Thesis)")
                else:
                    print("❌ Incorrect Prompt Format")
            else:
                print("❌ No Writing Question Generated (Not enough data?)")
                
        except Exception as e:
            print(f"❌ Failed: {e}")

if __name__ == "__main__":
    verify_writing_prompts()
