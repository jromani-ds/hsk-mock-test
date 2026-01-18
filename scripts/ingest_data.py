import csv
import json
import os
from pathlib import Path
from typing import Dict, List, Any, Set

DATA_DIR = Path("hsk/data")
RAW_VOCAB = DATA_DIR / "hsk30_raw.csv"
RAW_GRAMMAR = DATA_DIR / "hsk30_grammar_raw.csv"
RAW_DICT = DATA_DIR / "dictionary.txt"

OUTPUT_DIR = DATA_DIR

def load_radicals() -> Dict[str, str]:
    """Loads character to radical mapping from dictionary.txt."""
    print("Loading radicals...")
    char_to_radical = {}
    with open(RAW_DICT, 'r', encoding='utf-8') as f:
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
    levels_data: Dict[int, Dict[str, List[Any]]] = {} # level -> {vocab: [], grammar: []}
    used_characters: Set[str] = set()
    
def link_sentences(levels_data: Dict[int, Dict[str, List[Any]]]):
    """
    Links sentences from sentences.tsv to vocabulary words.
    Algorithm:
    1. Build map: FirstChar -> List[WordObject]
    2. Stream sentences.
    3. For each char in sentence, check if it starts a known word.
    4. If so, add sentence to word (limit 5).
    """
    print("Linking sentences...")
    SENTENCES_FILE = DATA_DIR / "sentences.tsv"
    if not SENTENCES_FILE.exists():
        print("Warning: sentences.tsv not found. Skipping.")
        return

    # 1. Build Index: Char -> List of (Level, VocabIndex, WordHanzi)
    # We need to reference the actual dict object to append to it.
    # Store: char -> list of dicts (the vocab objects themselves)
    word_index: Dict[str, List[Dict[str, Any]]] = {}
    
    total_words = 0
    for level, data in levels_data.items():
        for word in data["vocabulary"]:
            word["sentences"] = [] # Initialize
            hanzi = word["hanzi"]
            if not hanzi: continue
            
            first_char = hanzi[0]
            if first_char not in word_index:
                word_index[first_char] = []
            word_index[first_char].append(word)
            total_words += 1
            
    print(f"Indexed {total_words} words for sentence matching.")

    # 2. Stream Sentences
    matched_count = 0
    with open(SENTENCES_FILE, 'r', encoding='utf-8') as f:
        reader = csv.reader(f, delimiter='\t')
        for i, row in enumerate(reader):
            if len(row) < 2: continue
            
            sentence = row[1].strip()
            if not sentence: continue
            
            # Simple substring linking
            # Optimization: Check chars present
            # We iterate the sentence. If char in word_index, check matches.
            
            # Helper to keep track of words matched in THIS sentence to avoid duplicates
            matched_words_in_sentence = set()
            
            for j, char in enumerate(sentence):
                if char in word_index:
                    potential_words = word_index[char]
                    for word_obj in potential_words:
                        target = word_obj["hanzi"]
                        # Check if matches at position j
                        if sentence[j:].startswith(target):
                            # MATCH!
                            if id(word_obj) not in matched_words_in_sentence:
                                if len(word_obj["sentences"]) < 5:
                                    word_obj["sentences"].append(sentence)
                                    matched_count += 1
                                matched_words_in_sentence.add(id(word_obj))
            
            if i % 10000 == 0:
                print(f"Processed {i} sentences...")

    print(f"Linked sentences to words. Total matches events: {matched_count}")

def process_data():
    radicals_map = load_radicals()
    
    # Storage for processed data
    levels_data: Dict[int, Dict[str, List[Any]]] = {} # level -> {vocab: [], grammar: []}
    used_characters: Set[str] = set()
    
    # Initialize levels 1-9
    for i in range(1, 10):
        levels_data[i] = {"vocabulary": [], "grammar": []}

    # 1. Process Vocabulary (from drkameleon.json)
    print("Processing Vocabulary from drkameleon.json...")
    DRK_VOCAB = DATA_DIR / "drkameleon.json"
    
    with open(DRK_VOCAB, 'r', encoding='utf-8') as f:
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
                         lvl_num_str = lvl_num_str.split('-')[0]
                    
                    hsk_new_level = int(lvl_num_str)
                    break
                except ValueError:
                    continue
        
        if not hsk_new_level:
            continue
            
        hanzi = entry.get("simplified")
        if not hanzi:
            continue
            
        # Get pinyin/meaning from first form
        forms = entry.get("forms", [])
        if not forms:
            continue
            
        first_form = forms[0]
        pinyin = first_form.get("transcriptions", {}).get("pinyin", "")
        meanings = first_form.get("meanings", [])
        meaning_str = "; ".join(meanings)
        
        # Radicals
        word_radicals = []
        for char in hanzi:
            used_characters.add(char)
            r = radicals_map.get(char)
            if r and r not in word_radicals:
                word_radicals.append(r)
        
        if hsk_new_level in levels_data:
            levels_data[hsk_new_level]["vocabulary"].append({
                "hanzi": hanzi,
                "pinyin": pinyin,
                "meaning": meaning_str,
                "radicals": word_radicals,
                "sentences": [] # Init
            })

    # Link Sentences
    link_sentences(levels_data)

    # 2. Process Grammar (from CSV)
    print("Processing Grammar from CSV...")
    if RAW_GRAMMAR.exists():
        with open(RAW_GRAMMAR, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    level_str = row['Level']
                    # Handle "7-9" in grammar CSV if present
                    if "-" in level_str:
                        level = int(level_str.split('-')[0])
                    else:
                        level = int(level_str)
                except ValueError:
                    continue
                    
                if level in levels_data:
                    levels_data[level]["grammar"].append({
                        "name": f"{row['Category']} - {row['Details']}",
                        "description": row['Group'],
                        "structure": row['Content'],
                        "example": f"See {row['Details']}" # Placeholder
                    })
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
        print(f"Level {level}: {len(data['vocabulary'])} words, {len(data['grammar'])} grammar points.")
        with open(out_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
            
    # 4. Write Radicals (Subset)
    print("Writing radicals.json...")
    final_radicals = {}
    for char in used_characters:
        if char in radicals_map:
            final_radicals[char] = radicals_map[char]
            
    with open(OUTPUT_DIR / "radicals.json", 'w', encoding='utf-8') as f:
        json.dump(final_radicals, f, indent=2, ensure_ascii=False)

    print("Done.")

if __name__ == "__main__":
    process_data()
