import json
from pathlib import Path


def audit_coverage():
    data_dir = Path("hsk/data")
    full_coverage = True

    for level in range(1, 10):
        file_path = data_dir / f"level_{level}.json"
        if not file_path.exists():
            continue

        with open(file_path, encoding="utf-8") as f:
            data = json.load(f)

        vocab = data.get("vocabulary", [])
        total_words = len(vocab)
        words_with_sentences = sum(1 for w in vocab if w.get("sentences"))

        print(
            f"Level {level}: {words_with_sentences}/{total_words} words have sentences ({words_with_sentences / total_words * 100:.1f}%)"
        )

        if level >= 7:
            single_w_sent = sum(1 for w in vocab if w.get("sentences") and len(w["hanzi"]) == 1)
            compound_w_sent = sum(1 for w in vocab if w.get("sentences") and len(w["hanzi"]) > 1)
            total_single = sum(1 for w in vocab if len(w["hanzi"]) == 1)
            total_compound = sum(1 for w in vocab if len(w["hanzi"]) > 1)

            print(
                f"  -> Single Char with Sentences: {single_w_sent}/{total_single} ({single_w_sent / total_single * 100:.1f}%)"
            )
            print(
                f"  -> Compounds with Sentences:   {compound_w_sent}/{total_compound} ({compound_w_sent / total_compound * 100:.1f}%)"
            )

        if level <= 6 and (words_with_sentences / total_words) < 0.1:
            print("  WARNING: Low coverage!")
            full_coverage = False


if __name__ == "__main__":
    audit_coverage()
