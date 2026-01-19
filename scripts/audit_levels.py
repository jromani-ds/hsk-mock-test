import json
import pathlib
from typing import Dict, List, Set

DATA_DIR = pathlib.Path(__file__).parent.parent / "hsk" / "data"


def load_all_words() -> Dict[str, int]:
    """Load all words from all levels into a Map: Hanzi -> Level"""
    word_level_map = {}
    for level in range(1, 10):
        path = DATA_DIR / f"level_{level}.json"
        if not path.exists():
            continue

        with open(path, encoding="utf-8") as f:
            data = json.load(f)
            for w in data.get("vocabulary", []):
                hanzi = w.get("hanzi")
                if hanzi:
                    # If word appears in multiple levels (rare for new HSK), keep lowest?
                    # HSK 3.0 is usually distinct.
                    if hanzi not in word_level_map:
                        word_level_map[hanzi] = level
    print(f"Loaded {len(word_level_map)} unique words across all levels.")
    return word_level_map


def max_match_segment(text: str, dictionary: Set[str]) -> List[str]:
    """Simple MaxMatch segmentation to find words in sentence."""
    # This is a heuristic.
    # Greedily match longest possible word from dictionary starting at current pos
    start = 0
    tokens = []
    n = len(text)

    while start < n:
        matched = False
        # Try to match lengths 4 down to 1
        for length in range(4, 0, -1):
            if start + length > n:
                continue

            sub = text[start : start + length]
            if sub in dictionary:
                tokens.append(sub)
                start += length
                matched = True
                break

        if not matched:
            # Skip unknown char
            tokens.append(text[start])
            start += 1

    return tokens


def audit_level(target_level: int, word_level_map: Dict[str, int]):
    path = DATA_DIR / f"level_{target_level}.json"
    if not path.exists():
        return

    print(f"\n--- Auditing Level {target_level} ---")

    with open(path, encoding="utf-8") as f:
        data = json.load(f)

    vocab = data.get("vocabulary", [])

    total_sentences = 0
    bad_sentences = 0

    dictionary_keys = set(word_level_map.keys())

    for word_obj in vocab:
        sentences = word_obj.get("sentences", [])
        for sent in sentences:
            total_sentences += 1

            # Check vocab in this sentence
            tokens = max_match_segment(sent, dictionary_keys)

            max_word_level = 0
            offender = ""

            for token in tokens:
                lvl = word_level_map.get(token, 0)
                if lvl > max_word_level:
                    max_word_level = lvl
                    offender = token

            if max_word_level > target_level:
                bad_sentences += 1
                # print(f"  [Fail] Sent: {sent} | Found Level {max_word_level} word: {offender}")

    if total_sentences > 0:
        fail_rate = (bad_sentences / total_sentences) * 100
        print(f"Total Sentences: {total_sentences}")
        print(f"Non-Compliant Sentences: {bad_sentences} ({fail_rate:.2f}%)")
        print(f"Status: {'CRITICAL' if fail_rate > 10 else 'OK'}")
    else:
        print("No sentences found.")


def main():
    word_map = load_all_words()
    # Audit Levels 1, 2, 3 (Most sensitive to this issue)
    for i in [1, 2, 3]:
        audit_level(i, word_map)


if __name__ == "__main__":
    main()
