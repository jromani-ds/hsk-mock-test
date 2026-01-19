import random
from typing import Optional

from hsk.constants import (
    PASSING_SCORE_PERCENTAGE,
    QUESTION_TYPE_FIB,
    QUESTION_TYPE_MC,
    QUESTION_TYPE_WRITING,
)
from hsk.data_engine import DataEngine
from hsk.models import GrammarRule, Question, TestResult, Word


class QuestionGenerator:
    """Generates test questions based on HSK data."""

    def __init__(self, data_engine: DataEngine):
        self.data_engine = data_engine

    def generate_mc_question(self, word: Word, distractors: list[Word]) -> Question:
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
            level=word.level,
        )

    def generate_fib_question(self, grammar: GrammarRule) -> Question:
        """Generates a Fill-in-the-Blank question for a grammar rule."""
        # Simple FIB: Ask to complete the structure or identify the rule name
        # For V1, we'll ask users to identify the correct structure for a description

        prompt = (
            f"Complete the pattern for '{grammar.name}': {grammar.description}. "
            f"Example: {grammar.example}"
        )
        hint = f"Think about the structure: {grammar.structure.replace(' ', ' _ ')}"

        return Question(
            id=f"FIB_{grammar.name}",
            type=QUESTION_TYPE_FIB,
            prompt=prompt,
            options=[],  # Free text or could be structured
            correct_answer=grammar.structure,
            hint=hint,  # partial hint
            grammar_focus=grammar.name,
            level=grammar.level,
        )


class HSKTestEngine:
    """Manages the HSK test session."""

    def __init__(self, level: int, data_engine: DataEngine, num_questions: int = 10):
        self.level = level
        self.data_engine = data_engine
        self.questions: list[Question] = []
        self.current_question_index = 0
        self.score = 0
        self.mistakes: list[Question] = []

        # v17.0 TIERED POOL LOADING
        # T1 & T2: Load strictly the target level for intra-level homogeneity
        # T3: Load the entire band 7-9
        if self.level >= 7:
            for level_id in range(7, 10):
                self.data_engine.load_level_data(level_id)
        else:
            self.data_engine.load_level_data(level)

        self.data_engine.load_radicals()

        # Aggregate words for the test engine pool (Target selection pool)
        # We also need a distractor pool which might be the same or larger
        if self.level >= 7:
            word_map = {}
            for level_id in range(7, 10):
                for w in self.data_engine.get_words_for_level(level_id):
                    word_map[w.hanzi] = w
            self.words = list(word_map.values())
        else:
            self.words = self.data_engine.get_words_for_level(self.level)

        self.grammar_rules = self.data_engine.get_grammar_for_level(self.level)

        self._generate_test(num_questions=num_questions)

    def _generate_test(self, num_questions: int) -> None:
        questions = []
        if not self.words:
            self.questions = []
            return

        # v17.0 TARGET FILTERING: Strictly Level L words for the current test
        target_words = [w for w in self.words if w.level == self.level]

        if self.level >= 7:
            # ACADEMIC/FORMAL KEYWORDS for C2 Selection
            academic_keywords = {
                "哲学",
                "政治",
                "经济",
                "体系",
                "范畴",
                "逻辑",
                "理论",
                "机制",
                "策略",
                "规律",
                "固然",
                "诚然",
            }

            filtered_pool = []
            for w in target_words:
                # BLACKLIST INTERJECTIONS/COLLOQUIALISM
                if w.pos and any(p in ["e", "y", "o"] for p in w.pos):
                    continue
                # FILTER: L9 should prefer high-register concepts and compounds
                filtered_pool.append(w)

            # WEIGHTED SELECTION: Prioritize valid word depth & complexity
            filtered_pool.sort(
                key=lambda w: (
                    len(w.sentences) > 0,
                    any(k in w.meaning.lower() or k in w.hanzi for k in academic_keywords),
                    len(w.hanzi) >= 2,  # Prioritize compound words for C2
                    -w.frequency,
                ),
                reverse=True,
            )

            selection_pool = filtered_pool[: num_questions * 5]
            selected_words = random.sample(selection_pool, min(len(selection_pool), num_questions))
        else:
            # Standard Levels (1-6) - Homogeneity selection
            words_with_sentences = [w for w in target_words if w.sentences]
            if len(words_with_sentences) >= num_questions:
                random.shuffle(words_with_sentences)
                selected_words = words_with_sentences[:num_questions]
            else:
                # Merge with words that don't have sentences if needed
                other_words = [w for w in target_words if not w.sentences]
                pool = words_with_sentences + other_words
                random.shuffle(pool)
                selected_words = pool[:num_questions]

        # Ensure Unique Target Hanzi
        seen_hanzi = set()
        final_selection = []
        for w in selected_words:
            if w.hanzi not in seen_hanzi:
                final_selection.append(w)
                seen_hanzi.add(w.hanzi)

        for word in final_selection:
            q = self._create_question_for_word(word)
            if q:
                questions.append(q)

        # Fill if needed
        if len(questions) < num_questions and self.grammar_rules:
            rule = random.choice(self.grammar_rules)
            q = QuestionGenerator(self.data_engine).generate_fib_question(rule)
            questions.append(q)

        random.shuffle(questions)
        self.questions = questions[:num_questions]

    def _create_writing_question(self) -> Optional[Question]:
        """Generates a writing prompt based on Level standards."""
        if len(self.words) < 5 and self.level == 5:
            return None

        # Level 5: Vocab Composition (80 chars) - Use 3-5 words
        if self.level == 5:
            target_words = random.sample(self.words, 5)
            words_str = "，".join([w.hanzi for w in target_words])
            prompt = (
                "Writing Task (写作): Write a short paragraph "
                f"(~80 characters) using these words:\n{words_str}"
            )
            return Question(
                id="WRITING_L5",
                prompt=prompt,
                type=QUESTION_TYPE_WRITING,
                correct_answer="[Self-Graded]",
                options=[],
                hint="Ensure all words are used coherently.",
                level=self.level,
            )

        # Level 6: Narrative/Summarization (400 chars)
        # Since we don't have articles to summarize,
        # we fallback to Narrative Writing based on a Topic Word
        elif self.level == 6:
            if not self.words:
                return None
            topic_word = random.choice(self.words)
            prompt = (
                "Writing Task (写作): Write a narrative essay "
                f"(~400 characters) surrounding the theme: 「{topic_word.hanzi}」"
            )
            return Question(
                id="WRITING_L6",
                prompt=prompt,
                type=QUESTION_TYPE_WRITING,
                correct_answer="[Self-Graded]",
                options=[],
                hint="Structure: Introduction, Development, Conclusion.",
                level=self.level,
            )

        # Level 7-9: Argument/Thesis (600+ chars)
        elif self.level >= 7:
            if not self.words:
                return None
            topic_word = random.choice(self.words)
            prompt = (
                "Writing Task (写作): Write an argumentative thesis "
                f"(~600 characters) analyzing: 「{topic_word.hanzi}」"
            )
            return Question(
                id="WRITING_L79",
                prompt=prompt,
                type=QUESTION_TYPE_WRITING,
                correct_answer="[Self-Graded]",
                options=[],
                hint="State your position clearly and support it with logic.",
                level=self.level,
            )

        return None

    def _create_question_for_word(self, word: Word) -> Question:
        # Standard: Cloze (Fill-in-Blank) using Sentence
        if word.sentences:
            # RHETORICAL COMPLEXITY MARKERS (C2 Level)
            rhetorical_markers = [
                "与其",
                "毋宁",
                "甚至",
                "即便",
                "既然",
                "不仅",
                "岂",
                "何必",
                "固然",
                "何况",
                "所谓",
                "诚然",
            ]

            # REGISTER TRIGGER KEYWORDS (For Discrimination)
            register_triggers = [
                "政治",
                "理论",
                "学术",
                "机构",
                "规则",
                "逻辑",
                "范畴",
                "哲学",
                "利益",
                "关系",
            ]

            # FACTOID BLACKLIST (Biology, Chemistry, Basic Physics)
            factoid_keywords = {
                "二氧化碳",
                "氧气",
                "光合作用",
                "肺",
                "太阳系",
                "原子",
                "分子",
                "科学发现",
                "排出",
                "吸收",
            }

            # PRIORITIZE COMPLEXITY & CONTEXT
            min_len = 8
            if self.level >= 7:
                min_len = 45  # C2 Level Prose

            # Filter for sentences that have enough depth
            valid_sentences = []
            for s in word.sentences:
                if len(s) < min_len:
                    continue
                # ANTI-LEAK: Word cannot appear more than once
                if s.count(word.hanzi) > 1:
                    continue
                # ANTI-FACTOID: Deprioritize simple scientific facts
                if any(k in s for k in factoid_keywords):
                    continue

                valid_sentences.append(s)

            if not valid_sentences:
                valid_sentences = [s for s in word.sentences if s.count(word.hanzi) == 1]
                valid_sentences = sorted(valid_sentences, key=len, reverse=True)[:5]

            if not valid_sentences:
                valid_sentences = word.sentences[:1]

            # v13 Scorer: Rhetoric + Register + Dept + Colon/Semicolon
            def c2_score(s: str) -> int:
                score = len(s)
                score += s.count("，") * 15
                score += (s.count("：") + s.count("；")) * 25
                score += sum(50 for m in rhetorical_markers if m in s)
                score += sum(30 for t in register_triggers if t in s)  # Bonus for academic context
                return score

            valid_sentences.sort(key=c2_score, reverse=True)

            # Pick from top candidates
            candidate_pool = valid_sentences[:3]
            sentence = random.choice(candidate_pool)

            # Mask the word
            masked_sentence = sentence.replace(word.hanzi, "____", 1)

            # Distractors: C2 Quality (Semantic Domain Alignment)
            distractors = self._get_distractors(word, 3, use_hanzi=True)
            options = distractors + [word.hanzi]
            random.shuffle(options)

            return Question(
                id=f"CLOZE_{word.hanzi}",
                prompt=f"Fill in the blank: {masked_sentence}",
                type=QUESTION_TYPE_MC,
                correct_answer=word.hanzi,
                options=options,
                hint=self.data_engine.get_radical_hint(word.hanzi),
                level=word.level,
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
                level=word.level,
            )

    def _get_distractors(self, target: Word, count: int, use_hanzi: bool = False) -> list[str]:
        """
        v17.0 UNIVERSAL DISTRACTION ENGINE
        Ensures absolute parallelism (POS + Length) and Tier-specific discrimination.
        """
        # 1. PARALLELISM POOL: Same Level, Same Length, Same POS
        # For High-Band (7-9), pool is level-locked (Strictly L9 for L9 test)
        # unless pool is too small, then Band-locked.
        candidates = [w for w in self.words if w.hanzi != target.hanzi]

        # Filter by POS (Strict Parallelism)
        target_pos = set(target.pos) if target.pos else set()
        if target_pos:
            candidates = [w for w in candidates if w.pos and set(w.pos).intersection(target_pos)]

        # Filter by Length (Visual Parallelism)
        candidates = [w for w in candidates if len(w.hanzi) == len(target.hanzi)]

        # 2. TIER-SPECIFIC DISCRIMINATION
        if self.level >= 7:
            return self._get_t3_distractors(target, candidates, count)
        elif 4 <= self.level <= 6:
            return self._get_t2_distractors(target, candidates, count)
        else:
            return self._get_t1_distractors(target, candidates, count)

    def _get_t1_distractors(self, target: Word, candidates: list[Word], count: int) -> list[str]:
        """Tier 1: Foundation (1-3) - Semantic Categories + Visual Traps."""
        # Simple clustering based on meaning keywords (Category Lock)
        target_keywords = set(target.meaning.lower().replace(";", " ").split())

        scored = []
        for w in candidates:
            # Category Score (Shared keywords like "color", "time", "action")
            w_keywords = set(w.meaning.lower().replace(";", " ").split())
            category_score = len(target_keywords.intersection(w_keywords)) * 100
            # Visual Trap (Shared radical)
            visual_score = 50 if set(w.radicals).intersection(set(target.radicals)) else 0
            scored.append((w, category_score + visual_score))

        scored.sort(key=lambda x: x[1], reverse=True)
        return [w[0].hanzi for w in scored[:count]]

    def _get_t2_distractors(self, target: Word, candidates: list[Word], count: int) -> list[str]:
        """Tier 2: Proficiency (4-6) - Near-Synonyms + Usage scenarios."""
        target_keywords = set(target.meaning.lower().replace(";", " ").split())

        scored = []
        for w in candidates:
            # Synonymy Score (High keyword overlap)
            w_keywords = set(w.meaning.lower().replace(";", " ").split())
            synonym_score = len(target_keywords.intersection(w_keywords)) * 150
            # Sibling Check (shared character)
            shared_char = len(set(w.hanzi).intersection(set(target.hanzi)))
            kinship_bonus = 80 if shared_char > 0 else 0
            scored.append((w, synonym_score + kinship_bonus))

        scored.sort(key=lambda x: x[1], reverse=True)
        return [w[0].hanzi for w in scored[:count]]

    def _get_t3_distractors(self, target: Word, candidates: list[Word], count: int) -> list[str]:
        """Tier 3: Doctorate (7-9) - Morphological Siblings + Register."""
        # Force Morphological Siblings (Character Kinship)
        target_chars = set(target.hanzi)
        target_keywords = set(target.meaning.lower().replace(";", " ").split())

        scored = []
        for w in candidates:
            # Sibling Bonus (ROOT CHARACTER MATCH)
            shared_chars = len(set(w.hanzi).intersection(target_chars))
            kinship_score = shared_chars * 250
            # Semantic Domain (Technical overlapping)
            w_keywords = set(w.meaning.lower().replace(";", " ").split())
            domain_score = len(target_keywords.intersection(w_keywords)) * 100
            # Band Purity Bonus
            level_bonus = 50 if w.level == self.level else 0

            scored.append((w, kinship_score + domain_score + level_bonus))

        scored.sort(key=lambda x: x[1], reverse=True)

        # Ensure we don't just pick based on level if kinship is high
        # Sample for variability among top tier
        top_candidates = [x[0] for x in scored if x[1] >= scored[0][1] - 50]
        if len(top_candidates) >= count:
            return [w.hanzi for w in random.sample(top_candidates, count)]
        return [w[0].hanzi for w in scored[:count]]

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
            is_correct = answer.strip() == question.correct_answer.strip()
        elif question.type == QUESTION_TYPE_FIB:
            # simple exact match for now, could be fuzzy later
            is_correct = answer.strip().lower() == question.correct_answer.strip().lower()

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
            grammar_issues=list(set(grammar_issues)),  # unique
            passed=passed,
            details="Exam Ready" if passed else "Targeted Practice Required",
        )
