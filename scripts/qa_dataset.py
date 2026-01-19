import os
import json
import random
from hsk.data_engine import DataEngine
from hsk.test_engine import HSKTestEngine, Question

# Example script for User to QA dataset using an LLM API
# Requires an API key (e.g. OPENAI_API_KEY) set in environment.
# This script generates 20 questions and prompts the LLM to critique them.

def mock_llm_check(question: Question):
    """
    Placeholder for actual LLM call. 
    In production, replace this with a call to OpenAI/Gemini.
    """
    prompt = f"""
    You are an HSK Exam Expert. Evaluate this exam question for:
    1. Ambiguity (Are there other obvious correct answers?)
    2. Difficulty (Is it appropriate for HSK Level {question.level}?)
    3. Naturalness (Is the sentence natural Chinese?)
    
    Question Type: {question.type}
    Prompt: {question.prompt}
    Options: {question.options}
    Correct Answer: {question.correct_answer}
    
    Output JSON: {{ "ambiguous": bool, "correct_level": bool, "natural": bool, "comments": "..." }}
    """
    # print(f"--- Prompting LLM for Q: {question.id} ---")
    # print(prompt)
    return { "ambiguous": False, "correct_level": True, "natural": True, "comments": "Simulation Pass" }

def run_qa(level=6, count=10):
    print(f"Running QA/QC for {count} questions at Level {level}...")
    
    engine = DataEngine()
    test_engine = HSKTestEngine(level, engine, num_questions=count)
    
    results = []
    
    print(f"\n{'ID':<15} | {'Target':<10} | {'Ambiguous?':<10} | {'Comment'}")
    print("-" * 60)
    
    for q in test_engine.questions:
        # Check if multiple correct options exist in options?
        # The engine logic guarantees options are distinct words.
        # But are they synonyms?
        
        # Determine " Target Word" from ID or Answer
        target = q.correct_answer
        
        # LLM Check
        eval_result = mock_llm_check(q)
        
        ambiguous_flag = "YES" if eval_result["ambiguous"] else "No"
        print(f"{q.id:<15} | {target:<10} | {ambiguous_flag:<10} | {eval_result['comments']}")
        results.append(eval_result)
        
    print("\nNote: To enable real LLM checking, edit `scripts/qa_dataset.py` to add your API Key and endpoint.")

if __name__ == "__main__":
    run_qa(level=9, count=20)
