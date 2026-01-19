import json
from pathlib import Path
from collections import Counter

def check_duplicates():
    data_dir = Path("hsk/data")
    for level in range(1, 10):
        file_path = data_dir / f"level_{level}.json"
        if not file_path.exists(): continue
        
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        hanzi_list = [w["hanzi"] for w in data["vocabulary"]]
        counts = Counter(hanzi_list)
        duplicates = {k: v for k, v in counts.items() if v > 1}
        
        if duplicates:
            print(f"Level {level} Duplicates: {len(duplicates)}")
            # print(duplicates)
        else:
            print(f"Level {level}: No duplicates.")

if __name__ == "__main__":
    check_duplicates()
