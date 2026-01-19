import json
from pathlib import Path


def audit_level_9():
    data_dir = Path("hsk/data")

    # Load Level 6 and Level 9
    with open(data_dir / "level_6.json", encoding="utf-8") as f:
        l6_data = json.load(f)
        l6_vocab = {w["hanzi"] for w in l6_data["vocabulary"]}

    with open(data_dir / "level_9.json", encoding="utf-8") as f:
        l9_data = json.load(f)
        l9_vocab = [w["hanzi"] for w in l9_data["vocabulary"]]

    print(f"Level 6 Count: {len(l6_vocab)}")
    print(f"Level 9 Count: {len(l9_vocab)}")

    # Check Overlap
    overlap = [w for w in l9_vocab if w in l6_vocab]
    print(f"Overlap (L9 words found in L6): {len(overlap)}")
    if overlap:
        print(f"Sample Overlap: {overlap[:10]}")

    # Check Single Char vs Compound
    single_char = [w for w in l9_vocab if len(w) == 1]
    compounds = [w for w in l9_vocab if len(w) > 1]

    print("Level 9 Breakdown:")
    print(f"  Single Char: {len(single_char)} ({len(single_char) / len(l9_vocab) * 100:.1f}%)")
    print(f"  Compounds:   {len(compounds)} ({len(compounds) / len(l9_vocab) * 100:.1f}%)")

    # Check Source Levels in L9 (if we can infer from raw data audit or just assume strict ingestion)
    # The ingestion script forced them to be strictly separated if strict matching used.
    # But let's check what 'level' valid is stored (wait, we store 'level' in Word object but JSON just lists them)


if __name__ == "__main__":
    audit_level_9()
