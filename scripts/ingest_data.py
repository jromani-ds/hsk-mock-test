import csv
import json
from pathlib import Path
from typing import Any, Dict, List, Set

DATA_DIR = Path("hsk/data")
RAW_VOCAB = DATA_DIR / "hsk30_raw.csv"
RAW_GRAMMAR = DATA_DIR / "hsk30_grammar_raw.csv"
RAW_DICT = DATA_DIR / "dictionary.txt"

OUTPUT_DIR = DATA_DIR


def load_radicals() -> Dict[str, str]:
    """Loads character to radical mapping from dictionary.txt."""
    print("Loading radicals...")
    char_to_radical = {}
    with open(RAW_DICT, encoding="utf-8") as f:
        for line in f:
            try:
                entry = json.loads(line)
                char = entry.get("character")
                radical = entry.get("radical")
                if char and radical:
                    char_to_radical[char] = radical
            except json.JSONDecodeError:
                continue
    print(f"Loaded {len(char_to_radical)} radical mappings.")
    return char_to_radical


def parse_cedict(cedict_str: str) -> str:
    """Extracts meaning from CEDICT string."""
    # Format: Traditional|Simplified[pinyin] meaning
    # e.g., 愛|爱[ai4] to love; affection...
    # We want the meaning part after the space/bracket.
    # The csv usually has `Variants,CEDICT`.
    # Example: `愛|爱[ai4]` is NOT the meaning.
    # Wait, the CSV output I saw earlier: `L1-0001,爱,愛,ài,V,1,18,ài,爱,,愛|爱[ai4]`
    # The LAST column is CEDICT which looks like `Traditional|Simplified[pinyin]`.
    # WHERE IS THE MEANING??
    # The `ivankra/hsk30` CSV might NOT have meaning in the CEDICT column??
    # Let me re-check the CSV sample.
    pass


def process_data():
    radicals_map = load_radicals()

    # Storage for processed data
    levels_data: Dict[int, Dict[str, List[Any]]] = {}  # level -> {vocab: [], grammar: []}
    used_characters: Set[str] = set()


def tokenize_sentence(text: str, word_map: Dict[str, int]) -> List[str]:
    """
    Tokenizes text using MaxMatch against the provided word_map.
    Returns a list of token strings.
    """
    tokens = []
    start = 0
    n = len(text)

    while start < n:
        matched_word = ""
        step = 1

        # Try lengths 4 down to 1
        for length in range(4, 0, -1):
            if start + length > n:
                continue

            sub = text[start : start + length]
            if sub in word_map:
                matched_word = sub
                step = length
                break

        if matched_word:
            tokens.append(matched_word)
        else:
            # If no match (unknown char), treat as single char token (or ignore?)
            # For HSK linking, strictly we only care about matched words.
            # But for "level check", unknown words are risky.
            # We add single char as token to handle it.
            tokens.append(text[start])

        start += step

    return tokens


def get_max_level(tokens: List[str], word_map: Dict[str, int]) -> int:
    """Calculates max HSK level from tokens"""
    max_lvl = 0
    for t in tokens:
        max_lvl = max(max_lvl, word_map.get(t, 0))
    return max_lvl


def link_sentences(levels_data: Dict[int, Dict[str, List[Any]]]):
    """
    Links sentences from sentences.tsv to vocabulary words.
    STRICT MODE: Only links if sentence_level <= word_level.
    """
    print("Linking sentences (Strict Mode)...")
    SENTENCES_FILE = DATA_DIR / "sentences.tsv"
    if not SENTENCES_FILE.exists():
        print("Warning: sentences.tsv not found. Skipping.")
        return

    # 1. Build Global Word Map (Hanzi -> Level) for Filtering
    all_word_levels: Dict[str, int] = {}
    for level, data in levels_data.items():
        for w in data["vocabulary"]:
            if w["hanzi"]:
                # If duplicate, keep lowest level usually, but HSK 3.0 is strict.
                if w["hanzi"] not in all_word_levels:
                    all_word_levels[w["hanzi"]] = level

    # 2. Build Index: Char -> List of dicts
    word_index: Dict[str, List[Dict[str, Any]]] = {}
    total_words = 0
    for level, data in levels_data.items():
        for word in data["vocabulary"]:
            word["sentences"] = []  # Reset
            hanzi = word["hanzi"]
            if not hanzi:
                continue

            first_char = hanzi[0]
            if first_char not in word_index:
                word_index[first_char] = []
            word_index[first_char].append(word)
            total_words += 1

    print(f"Indexed {total_words} words for matching.")

    # 3. Stream Sentences
    matched_count = 0
    skipped_count = 0

    MIN_SENTENCE_LENGTH = 6
    BLACKLIST_SENTENCE_IDS = {"43078", "22981"}  # 22981 is "有罢工。", 43078 is "半夜...挨..."

    with open(SENTENCES_FILE, encoding="utf-8") as f:
        reader = csv.reader(f, delimiter="\t")
        for i, row in enumerate(reader):
            if len(row) < 2:
                continue

            sentence_id = row[0]
            sentence = row[1].strip()

            if not sentence:
                continue

            # Filters
            if sentence_id in BLACKLIST_SENTENCE_IDS:
                continue
            if len(sentence) < MIN_SENTENCE_LENGTH:
                continue

            # 3a. Tokenize & Level Check
            tokens = tokenize_sentence(sentence, all_word_levels)

            # Filter: Check if sentence contains ANY unknown words?
            # Current strict logic: max level of KNOWN words.
            sent_max_level = get_max_level(tokens, all_word_levels)

            # 3b. Link to eligible words
            matched_words_in_sentence = set()

            # Check distinct tokens
            for token in tokens:
                if not token:
                    continue

                # word_index keys are the FIRST CHAR of the word.
                # So we look up lists by token[0], then find exact match.
                first_char = token[0]

                if first_char in word_index:
                    potential_words = word_index[first_char]

                    found_word_objs = [w for w in potential_words if w["hanzi"] == token]

                    for word_obj in found_word_objs:
                        target = word_obj["hanzi"]
                        target_level = all_word_levels.get(target, 99)

                        # STRICT LEVEL CHECK: Sentence Diff <= Word Level
                        if sent_max_level <= target_level:
                            if id(word_obj) not in matched_words_in_sentence:
                                if len(word_obj["sentences"]) < 5:
                                    word_obj["sentences"].append(sentence)
                                    matched_count += 1
                                matched_words_in_sentence.add(id(word_obj))
                        else:
                            skipped_count += 1

            if i % 10000 == 0:
                print(f"Processed {i} sentences...")

    print(f"Linked (Strict). Matches: {matched_count}. Skipped Links (Too Hard): {skipped_count}")


def process_data():
    radicals_map = load_radicals()

    # Storage for processed data
    levels_data: Dict[int, Dict[str, List[Any]]] = {}  # level -> {vocab: [], grammar: []}
    used_characters: Set[str] = set()

    # Initialize levels 1-9
    for i in range(1, 10):
        levels_data[i] = {"vocabulary": [], "grammar": []}

    # 1. Process Vocabulary (from drkameleon.json)
    print("Processing Vocabulary from drkameleon.json...")
    DRK_VOCAB = DATA_DIR / "drkameleon.json"

    with open(DRK_VOCAB, encoding="utf-8") as f:
        vocab_list = json.load(f)

    for entry in vocab_list:
        # Check levels
        levels = entry.get("level", [])
        hsk_new_level = None

        # Find HSK 3.0 level (format "new-X")
        for lvl in levels:
            if isinstance(lvl, str) and lvl.startswith("new-"):
                try:
                    # Handle "new-7-9" or just "new-7"
                    # If "new-7-9", maybe we default to 7? or duplicate?
                    # The sample showed "new-7". Let's assume integers.
                    lvl_num_str = lvl.replace("new-", "")
                    # If it's a range like "7-9", take the first?
                    # HSK 3.0 Advanced is often grouped.
                    if "-" in lvl_num_str:
                        # e.g. "7-9" -> 7. Or random? Let's use 7 for now.
                        # Better: Check if specific 7, 8, 9 exist in data.
                        lvl_num_str = lvl_num_str.split("-")[0]

                    hsk_new_level = int(lvl_num_str)
                    break
                except ValueError:
                    continue

        if not hsk_new_level:
            continue

        hanzi = entry.get("simplified")
        if not hanzi:
            continue

        # Get pinyin/meaning/pos
        forms = entry.get("forms", [])
        if not forms:
            continue

        first_form = forms[0]
        pinyin = first_form.get("transcriptions", {}).get("pinyin", "")
        meanings = first_form.get("meanings", [])
        meaning_str = "; ".join(meanings)

        pos_list = entry.get("pos", [])  # ["n"], ["v"] etc
        frequency = entry.get("frequency", 99999)

        # Radicals
        word_radicals = []
        for char in hanzi:
            used_characters.add(char)
            r = radicals_map.get(char)
            if r and r not in word_radicals:
                word_radicals.append(r)

        if hsk_new_level in levels_data:
            levels_data[hsk_new_level]["vocabulary"].append(
                {
                    "hanzi": hanzi,
                    "pinyin": pinyin,
                    "meaning": meaning_str,
                    "pos": pos_list,
                    "radicals": word_radicals,
                    "sentences": [],  # Init
                    "frequency": frequency,
                }
            )

    # Link Sentences
    link_sentences(levels_data)

    # 2. Process Grammar (from CSV)
    print("Processing Grammar from CSV...")
    if RAW_GRAMMAR.exists():
        with open(RAW_GRAMMAR, encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    level_str = row["Level"]
                    # Handle "7-9" in grammar CSV if present
                    if "-" in level_str:
                        level = int(level_str.split("-")[0])
                    else:
                        level = int(level_str)
                except ValueError:
                    continue

                if level in levels_data:
                    levels_data[level]["grammar"].append(
                        {
                            "name": f"{row['Category']} - {row['Details']}",
                            "description": row["Group"],
                            "structure": row["Content"],
                            "example": f"See {row['Details']}",  # Placeholder
                        }
                    )
    else:
        print("Warning: Grammar CSV not found.")

    # Duplicate Level 7 data to 8 and 9 (HSK 7-9 Advanced Band)
    if levels_data[7]["vocabulary"]:
        print("Distributing Advanced Band (Level 7) to Levels 8 and 9...")
        levels_data[8] = levels_data[7].copy()
        levels_data[9] = levels_data[7].copy()

    # 3. Write Levels
    print("Writing level files...")
    for level, data in levels_data.items():
        out_file = OUTPUT_DIR / f"level_{level}.json"
        # Only write if we have data to avoid empty files overwriting logic if any
        # But we want to generate all.
        print(
            f"Level {level}: {len(data['vocabulary'])} words, {len(data['grammar'])} grammar points."
        )
        with open(out_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

    # 4. Write Radicals (Subset)
    print("Writing radicals.json...")
    final_radicals = {}
    for char in used_characters:
        if char in radicals_map:
            final_radicals[char] = radicals_map[char]

    with open(OUTPUT_DIR / "radicals.json", "w", encoding="utf-8") as f:
        json.dump(final_radicals, f, indent=2, ensure_ascii=False)

    print("Done.")


if __name__ == "__main__":
    process_data()
