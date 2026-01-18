from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class Word:
    """Represents an HSK vocabulary word."""
    hanzi: str
    pinyin: str
    meaning: str
    level: int
    radicals: List[str] = field(default_factory=list)
    sentences: List[str] = field(default_factory=list)


@dataclass
class GrammarRule:
    """Represents an HSK grammar point."""
    name: str
    description: str
    structure: str
    level: int
    example: str


@dataclass
class Question:
    """Represents a generated test question."""
    id: str  # Unique identifier for tracking
    type: str  # 'MC' (Multiple Choice) or 'FIB' (Fill-in-the-Blank)
    prompt: str
    options: List[str]  # For MC
    correct_answer: str
    hint: Optional[str] = None
    grammar_focus: Optional[str] = None # Name of the grammar rule if applicable
    level: int = 0


@dataclass
class TestResult:
    """Represents the result of a single test session."""
    level: int
    score: int
    total_questions: int
    grammar_issues: List[str] = field(default_factory=list)
    passed: bool = False
    details: str = ""
