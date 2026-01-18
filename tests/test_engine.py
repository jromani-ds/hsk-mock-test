import pytest
from hsk.test_engine import HSKTestEngine, QuestionGenerator
from hsk.data_engine import DataEngine
from hsk.models import Word, GrammarRule, Question
from hsk.constants import QUESTION_TYPE_MC

@pytest.fixture
def mock_data_engine():
    engine = DataEngine(data_dir=None) # Use default/mock behavior or patch
    # Manually populate with test data to avoid file dependency in unit test logic
    engine.words[1] = [
        Word("A", "a", "meaning A", 1, []),
        Word("B", "b", "meaning B", 1, []),
        Word("C", "c", "meaning C", 1, []),
        Word("D", "d", "meaning D", 1, []),
    ]
    engine.grammar_rules[1] = [
        GrammarRule("Rule 1", "desc", "struct", 1, "ex")
    ]
    engine.radicals = {"A": "RadA"}
    
    # Mock methods to avoid disk access
    engine.load_level_data = lambda x: None
    engine.load_radicals = lambda: None
    
    return engine

def test_question_generation(mock_data_engine):
    gen = QuestionGenerator(mock_data_engine)
    word = mock_data_engine.words[1][0]
    distractors = mock_data_engine.words[1][1:]
    
    q = gen.generate_mc_question(word, distractors)
    assert q.type == "MC"
    assert q.correct_answer == "meaning A"
    assert len(q.options) == 4
    assert "meaning A" in q.options

def test_engine_flow(mock_data_engine):
    engine = HSKTestEngine(1, mock_data_engine)
    # Ensure questions were generated
    assert len(engine.questions) > 0
    
    # Test getting questions
    q1 = engine.get_next_question()
    assert q1 is not None
    
    # Test answering correctly
    is_correct = engine.submit_answer(q1, q1.correct_answer)
    assert is_correct is True
    assert engine.score == 1
    
    # Test answering incorrectly
    q2 = engine.get_next_question()
    if q2:
        is_correct = engine.submit_answer(q2, "Wrong Answer")
        assert is_correct is False
        assert len(engine.mistakes) == 1

def test_radical_hint(mock_data_engine):
    engine = HSKTestEngine(1, mock_data_engine)
    # Create a dummy question with a character known to have a radical
    q = Question("test", "MC", "Select for A", [], "ans")
    
    hint = engine.get_radical_hint(q)
    assert "Radical: RadA" in hint

def test_result_calculation(mock_data_engine):
    engine = HSKTestEngine(1, mock_data_engine)
    # Simulate a perfect score
    for q in engine.questions:
        engine.submit_answer(q, q.correct_answer)
        engine.get_next_question() # advance
        
    result = engine.calculate_result()
    assert result.score == 100
    assert result.passed is True
    assert result.details == "Exam Ready"
