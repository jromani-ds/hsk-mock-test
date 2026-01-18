from hsk.test_engine import HSKTestEngine
from hsk.data_engine import DataEngine
from hsk.constants import HSK_EXAM_STRUCTURE

def verify_counts():
    data_engine = DataEngine()
    
    print("Verifying Exam Configuration...")
    
    for level, expected_count in HSK_EXAM_STRUCTURE.items():
        # Only verify a few levels to save time loading
        if level not in [1, 3, 9]: continue
            
        print(f"Checking Level {level} (Expected: {expected_count})...")
        try:
            engine = HSKTestEngine(level, data_engine, num_questions=expected_count)
            actual = len(engine.questions)
            
            if actual == expected_count:
                print(f"✅ Level {level}: Correctly generated {actual} questions.")
            else:
                # Note: Level 1 might have fewer than 40 words if my JSON is small?
                # But I have ~500 words for Level 1, so 40 should be fine.
                print(f"⚠️ Level {level}: Generated {actual} questions (Expected {expected_count}).")
                
        except Exception as e:
            print(f"❌ Level {level} Failed: {e}")

if __name__ == "__main__":
    verify_counts()
