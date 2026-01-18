import sys
from hsk.data_engine import DataEngine
from hsk.test_engine import HSKTestEngine
from hsk.constants import (
    LEVEL_DESCRIPTIONS, MSG_CORRECT, MSG_INCORRECT, 
    MSG_PASS, MSG_FAIL, MSG_GRAMMAR_AUDIT, MSG_CHALLENGE, 
    QUESTION_TYPE_MC, HSK_EXAM_STRUCTURE
)

def print_separator():
    print("-" * 40)

def main():
    print("-" * 40)
    print("HSK Mock Test (HSK 3.0 Standard)")
    print("-" * 40)

    # 1. Level Selection
    while True:
        try:
            level_input = input("Select HSK Level (1-9): ").strip()
            if not level_input: continue
            level = int(level_input)
            if 1 <= level <= 9:
                break
            print("Please enter a number between 1 and 9.")
        except ValueError:
            print("Invalid input.")

    # Select Mode
    print("\nSelect Mode:")
    print("1. Practice (10 Questions)")
    print(f"2. Real Exam ({HSK_EXAM_STRUCTURE.get(level, 40)} Questions)")
    
    num_questions = 10
    while True:
        mode_input = input("Choice (1/2): ").strip()
        if mode_input == "1":
            num_questions = 10
            break
        elif mode_input == "2":
            num_questions = HSK_EXAM_STRUCTURE.get(level, 40)
            break
        else:
            print("Invalid choice. Please enter '1' or '2'.")

    print(f"\nInitializing Level {level} Test ({num_questions} Questions)...")
    print(f"Standard: {LEVEL_DESCRIPTIONS.get(level, 'Unknown')}")
    print("-" * 40)

    # Initialize Engine
    try:
        data_engine = DataEngine()
        engine = HSKTestEngine(level, data_engine, num_questions=num_questions)
    except FileNotFoundError as e:
        print(f"Error: {e}")
        print("Required data files not found. Please ensure data is installed.")
        sys.exit(1)
    except Exception as e:
        print(f"Initialization Error: {e}")
        sys.exit(1)

    # 2. Test Loop
    question_count = 0
    while True:
        question = engine.get_next_question()
        if not question:
            break
        
        question_count += 1
        print(f"\nQuestion {question_count}: {question.prompt}")
        
        if question.type == QUESTION_TYPE_MC:
            for idx, option in enumerate(question.options):
                print(f"{idx + 1}. {option}")
        
        # User Answer Loop (handling hint requests)
        while True:
            user_input = input("\nYour Answer (or type 'hint'): ").strip()
            
            if user_input.lower() == "hint":
                print(f"Hint: {question.hint or engine.get_radical_hint(question)}")
                continue
            
            # Process Answer
            answer_to_submit = user_input
            if question.type == QUESTION_TYPE_MC and user_input.isdigit():
                # Map select index to text
                idx = int(user_input) - 1
                if 0 <= idx < len(question.options):
                    answer_to_submit = question.options[idx]
            
            is_correct = engine.submit_answer(question, answer_to_submit)
            if is_correct:
                print(MSG_CORRECT)
            else:
                print(MSG_INCORRECT.format(answer=question.correct_answer))
            break

    # 3. Generating Results
    result = engine.calculate_result()
    
    print_separator()
    print("Test Results")
    print_separator()
    print(f"Score: {result.score}% ({result.score}/{100})")
    print(f"Status: {result.details}")
    
    if result.grammar_issues:
        audit_msg = "\n".join([f"- {issue}" for issue in result.grammar_issues])
        print(MSG_GRAMMAR_AUDIT.format(audit=audit_msg))
    
    # 4. Challenge Question
    print(MSG_CHALLENGE.format(level=level + 1))
    print("(This feature checks your readiness for the next level - Logic TBD in next version)")
    print_separator()

if __name__ == "__main__":
    main()
