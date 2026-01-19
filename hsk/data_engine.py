import json
import os
from typing import List, Dict, Optional
from hsk.models import Word, GrammarRule
from pathlib import Path


class DataEngine:
    """Handles loading and accessing HSK data."""

    def __init__(self, data_dir: Optional[str] = None):
        if data_dir:
            self.data_path = Path(data_dir)
        else:
            # Default to 'data' directory relative to this file
            self.data_path = Path(__file__).parent / "data"
        
        self.words: Dict[int, List[Word]] = {}  # Level -> List[Word]
        self.grammar_rules: Dict[int, List[GrammarRule]] = {} # Level -> List[GrammarRule]
        self.radicals: Dict[str, str] = {} # Character -> Radical

    def load_level_data(self, level: int) -> None:
        """Loads vocabulary and grammar for a specific level."""
        file_path = self.data_path / f"level_{level}.json"
        
        if not file_path.exists():
            raise FileNotFoundError(f"Data file for level {level} not found: {file_path}")

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            # Load Words (Deduplicated)
            words_data = data.get("vocabulary", [])
            unique_words = {}
            for w in words_data:
                hanzi = w["hanzi"]
                if hanzi not in unique_words:
                    unique_words[hanzi] = w
            
            self.words[level] = [
                Word(
                    hanzi=w["hanzi"],
                    pinyin=w["pinyin"],
                    meaning=w["meaning"],
                    level=level,
                    radicals=w.get("radicals", []),
                    sentences=w.get("sentences", []),
                    pos=w.get("pos", []),
                    frequency=w.get("frequency", 0)
                ) for w in unique_words.values()
            ]

            # Load Grammar
            grammar_data = data.get("grammar", [])
            self.grammar_rules[level] = [
                GrammarRule(
                    name=g["name"],
                    description=g["description"],
                    structure=g["structure"],
                    level=level,
                    example=g["example"]
                ) for g in grammar_data
            ]

        except json.JSONDecodeError:
            print(f"Error decoding JSON for level {level}")
            raise
        except KeyError as e:
            print(f"Missing required field in data for level {level}: {e}")
            raise

    def load_radicals(self) -> None:
        """Loads character-to-radical mapping."""
        file_path = self.data_path / "radicals.json"
        if not file_path.exists():
            # Warn but don't fail if radicals are optional for now
            print(f"Warning: Radicals file not found: {file_path}")
            return

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                self.radicals = json.load(f)
        except json.JSONDecodeError:
             print("Error decoding radicals JSON")

    def get_words_for_level(self, level: int) -> List[Word]:
        return self.words.get(level, [])

    def get_grammar_for_level(self, level: int) -> List[GrammarRule]:
        return self.grammar_rules.get(level, [])

    def get_radical_hint(self, character: str) -> Optional[str]:
        return self.radicals.get(character)
