import random
from typing import List, Optional, Tuple
from hsk.models import Question, TestResult, Word, GrammarRule
from hsk.data_engine import DataEngine
from hsk.constants import QUESTION_TYPE_MC, QUESTION_TYPE_FIB, PASSING_SCORE_PERCENTAGE


class QuestionGenerator:
    """Generates test questions based on HSK data."""

    def __init__(self, data_engine: DataEngine):
        self.data_engine = data_engine

    def generate_mc_question(self, word: Word, distractors: List[Word]) -> Question:
        """Generates a Multiple Choice question for a vocabulary word."""
        options = [d.meaning for d in distractors]
        options.append(word.meaning)
        random.shuffle(options)

        return Question(
            id=f"MC_{word.hanzi}",
            type=QUESTION_TYPE_MC,
            prompt=f"Select the correct meaning for: {word.hanzi} ({word.pinyin})",
            options=options,
            correct_answer=word.meaning,
            hint=None,  # Hint logic is handled at the engine level for character lookups
            level=word.level
        )

    def generate_fib_question(self, grammar: GrammarRule) -> Question:
        """Generates a Fill-in-the-Blank question for a grammar rule."""
        # Simple FIB: Ask to complete the structure or identify the rule name
        # For V1, we'll ask users to identify the correct structure for a description
        
        return Question(
            id=f"FIB_{grammar.name}",
            type=QUESTION_TYPE_FIB,
            prompt=f"Complete the pattern for '{grammar.name}': {grammar.description}. Example: {grammar.example}",
            options=[], # Free text or could be structured
            correct_answer=grammar.structure, 
            hint=f"Think about the structure: {grammar.structure.replace(' ', ' _ ')}", # partial hint
            grammar_focus=grammar.name,
            level=grammar.level
        )


class HSKTestEngine:
    """Manages the HSK test session."""

    def __init__(self, level: int, data_engine: DataEngine, num_questions: int = 10):
        self.level = level
        self.data_engine = data_engine
        self.questions: List[Question] = []
        self.current_question_index = 0
        self.score = 0
        self.mistakes: List[Question] = []
        
        # Load necessary data
        self.data_engine.load_level_data(level)
        self.data_engine.load_radicals()
        
        self.words = self.data_engine.get_words_for_level(self.level)
        self.grammar_rules = self.data_engine.get_grammar_for_level(self.level)
        
        self._generate_test(num_questions=num_questions)

    def _generate_test(self, num_questions: int):
        questions = []
        # Sample words from the level
        if not self.words:
            self.questions = []
            return
            
        # Try to pick words that HAVE sentences first for "Real" simulation
        words_with_sentences = [w for w in self.words if w.sentences]
        other_words = [w for w in self.words if not w.sentences]
        
        # Prioritize words with sentences
        pool = words_with_sentences + other_words
        selected_words = pool[:num_questions] if len(pool) >= num_questions else pool
        # Shuffle to mix them back up if we just took top N
        random.shuffle(selected_words)
        
        for word in selected_words:
            q = self._create_question_for_word(word)
            if q:
                questions.append(q)
                
        # Add grammar questions if available (1-2 per test) and we have space
        if self.grammar_rules and len(questions) < num_questions and len(questions) > 0:
             # Just add one for now to mix it in
             rule = random.choice(self.grammar_rules)
             q = QuestionGenerator(self.data_engine).generate_fib_question(rule)
             questions.append(q)
             
        random.shuffle(questions)
        # Trim to requested size if we added extra
        self.questions = questions[:num_questions]

    def _create_question_for_word(self, word: Word) -> Question:
        # Standard: Cloze (Fill-in-Blank) using Sentence
        if word.sentences:
            sentence = random.choice(word.sentences)
            # Mask the word in the sentence
            # Simple replace first occurrence? Or all?
            # "我 爱 爸爸" -> "我 [__] 爸爸"
            # We use a placeholder like "____"
            masked_sentence = sentence.replace(word.hanzi, "____", 1) 
            
            # Distractors: Random other words from same level
            distractors = self._get_distractors(word, 3, use_hanzi=True)
            options = distractors + [word.hanzi]
            random.shuffle(options)
            
            return Question(
                id=f"CLOZE_{word.hanzi}",
                prompt=f"Fill in the blank: {masked_sentence}",
                type=QUESTION_TYPE_MC, # Reuse MC structure
                correct_answer=word.hanzi,
                options=options,
                hint=self.data_engine.get_radical_hint(word.hanzi),
                level=word.level
            )
        else:
            # Fallback: Definition check if no sentence available (Legacy mode)
            # BUT user wants "No English".
            # Can we generate a "Select the Synonym" question? Or just Pinyin?
            # Or ask "Select the word for this definition" (English prompt)? NO.
            # "Select the Meaning" is English based.
            # Let's use Pinyin prompt: "Select the Hanzi for: {pinyin}" -> Options: [Hanzi]
            # This is monolingual-ish (Pinyin is standard).
            distractors = self._get_distractors(word, 3, use_hanzi=True)
            options = distractors + [word.hanzi]
            random.shuffle(options)
            
            return Question(
                id=f"PINYIN_{word.hanzi}",
                prompt=f"Select the Hanzi for: {word.pinyin}",
                type=QUESTION_TYPE_MC,
                correct_answer=word.hanzi,
                options=options,
                hint=self.data_engine.get_radical_hint(word.hanzi),
                level=word.level
            )

    def _get_distractors(self, target: Word, count: int, use_hanzi: bool = False) -> List[str]:
        """Get distractors. If use_hanzi=True, returns Chinese characters. Else returns meanings."""
        candidates = [w for w in self.words if w.hanzi != target.hanzi]
        if len(candidates) < count:
            # Fallback if not enough unique candidates
            if use_hanzi:
                return [f"Distractor{i}" for i in range(count)]
            else:
                return [f"Meaning{i}" for i in range(count)]
            
        selected = random.sample(candidates, count)
        if use_hanzi:
            return [w.hanzi for w in selected]
        else:
            return [w.meaning for w in selected]

    def _create_question_for_word(self, word: Word) -> Question:
        # Standard: Cloze (Fill-in-Blank) using Sentence
        if word.sentences:
            sentence = random.choice(word.sentences)
            # Mask the word in the sentence
            # Simple replace first occurrence? Or all?
            # "我 爱 爸爸" -> "我 [__] 爸爸"
            # We use a placeholder like "____"
            masked_sentence = sentence.replace(word.hanzi, "____", 1) 
            
            # Distractors: Random other words from same level
            distractors = self._get_distractors(word, 3, use_hanzi=True)
            options = distractors + [word.hanzi]
            random.shuffle(options)
            
            return Question(
                id=f"CLOZE_{word.hanzi}",
                prompt=f"Fill in the blank: {masked_sentence}",
                type=QUESTION_TYPE_MC, # Reuse MC structure
                correct_answer=word.hanzi,
                options=options,
                hint=self.data_engine.get_radical_hint(word.hanzi),
                level=word.level
            )
        else:
            # Fallback: Definition check if no sentence available (Legacy mode)
            # Use Chinese Hanzi as prompt, English meaning as answer (fallback)
            # OR better: "Select the pinyin" or similar to keep it "Chinese" focused?
            # User wants "Real Exam".
            distractors = self._get_distractors(word, 3, use_hanzi=False)
            options = distractors + [word.meaning]
            random.shuffle(options)
            
            return Question(
                id=f"MC_{word.hanzi}",
                prompt=f"Select the meaning for: {word.hanzi} ({word.pinyin})",
                type=QUESTION_TYPE_MC,
                correct_answer=word.meaning,
                options=options,
                hint=self.data_engine.get_radical_hint(word.hanzi),
                level=word.level
            )

    def _get_distractors(self, target: Word, count: int, use_hanzi: bool = False) -> List[str]:
        """Get distractors. If use_hanzi=True, returns Chinese characters. Else returns meanings."""
        candidates = [w for w in self.words if w.hanzi != target.hanzi]
        if len(candidates) < count:
            # Fallback if not enough unique candidates, should not happen with real data
            # For now, just return a list of placeholders or fewer distractors
            if use_hanzi:
                return [f"Distractor{i}" for i in range(count)]
            else:
                return [f"Meaning{i}" for i in range(count)]
            
        selected = random.sample(candidates, count)
        if use_hanzi:
            return [w.hanzi for w in selected]
        else:
            return [w.meaning for w in selected]     

    def get_next_question(self) -> Optional[Question]:
        if self.current_question_index < len(self.questions):
            q = self.questions[self.current_question_index]
            self.current_question_index += 1
            return q
        return None

    def submit_answer(self, question: Question, answer: str) -> bool:
        """Evaluates an answer."""
        is_correct = False
        if question.type == QUESTION_TYPE_MC:
            # For MC, user might enter index or text. 
            # CLI will handle mapping index to text, so assume 'answer' is the text option
            is_correct = (answer.strip() == question.correct_answer.strip())
        elif question.type == QUESTION_TYPE_FIB:
            # simple exact match for now, could be fuzzy later
            is_correct = (answer.strip().lower() == question.correct_answer.strip().lower())

        if is_correct:
            self.score += 1
        else:
            self.mistakes.append(question)
            
        return is_correct

    def get_radical_hint(self, question: Question) -> Optional[str]:
        """Provides a radical hint for the key character in the question."""
        # Simple extraction logic: find Chinese characters in prompt
        # For MC questions on words, extracting from the prompt "Select ... for: X" works
        # This is a heuristic for V1
        
        for char in question.prompt:
            hint = self.data_engine.get_radical_hint(char)
            if hint:
                return f"Character: {char}, Radical: {hint}"
        
        return "No specific radical hint available."

    def calculate_result(self) -> TestResult:
        percentage = int((self.score / len(self.questions)) * 100) if self.questions else 0
        passed = percentage >= PASSING_SCORE_PERCENTAGE
        
        grammar_issues = []
        for q in self.mistakes:
            if q.grammar_focus:
                grammar_issues.append(f"Review rule: {q.grammar_focus}")
            else:
                 # It was a vocab word
                 grammar_issues.append(f"Review vocabulary in: {q.prompt}")

        return TestResult(
            level=self.level,
            score=percentage,
            total_questions=len(self.questions),
            grammar_issues=list(set(grammar_issues)), # unique
            passed=passed,
            details="Exam Ready" if passed else "Targeted Practice Required"
        )
