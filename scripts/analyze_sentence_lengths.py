import json
import statistics

def analyze_lengths(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    vocab_list = data.get("vocabulary", [])
    
    lengths = []
    short_sentences = []
    
    # Threshold for "suspiciously short"
    THRESHOLD = 10

    for word_entry in vocab_list:
        for sent in word_entry.get("sentences", []):
            text = sent.replace(" ", "") # Remove spaces if any (though Chinese usually doesn't have them in raw source, Tatoeba might)
            # Remove punctuation for pure character count? 
            # Or just count raw string length. Let's count raw string length.
            l = len(text)
            lengths.append(l)
            if l < THRESHOLD:
                short_sentences.append(text)

    if not lengths:
        print(f"No sentences found in {file_path}")
        return

    print(f"--- Analysis for {file_path} ---")
    print(f"Total Sentences: {len(lengths)}")
    print(f"Min Length: {min(lengths)}")
    print(f"Max Length: {max(lengths)}")
    print(f"Avg Length: {statistics.mean(lengths):.2f}")
    print(f"Median Length: {statistics.median(lengths)}")
    print(f"Sentences < {THRESHOLD} chars: {len(short_sentences)} ({len(short_sentences)/len(lengths)*100:.2f}%)")
    
    print("\nSample Short Sentences:")
    for s in short_sentences[:20]:
        print(f" - {s}")

if __name__ == "__main__":
    analyze_lengths("hsk/data/level_6.json")
