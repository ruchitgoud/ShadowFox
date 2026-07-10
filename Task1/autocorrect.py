from pathlib import Path
import re
from collections import Counter, defaultdict

PROJECT_DIR = Path(__file__).parent
TRAINING_DIR = PROJECT_DIR / "training_data"

def strip_gutenberg_boilerplate(text: str) -> str:
    start = re.search(
        r"\*\*\*\s*START OF (THE|THIS) PROJECT GUTENBERG EBOOK", text, re.I
    )
    if start:
        text = text[start.end():]
    end = re.search(
        r"\*\*\*\s*END OF (THE|THIS) PROJECT GUTENBERG EBOOK", text, re.I
    )
    if end:
        text = text[:end.start()]
    return text

def load_all_texts() -> str:
    parts = []

    if TRAINING_DIR.is_dir():
        for p in sorted(TRAINING_DIR.glob("*.txt")):
            raw = p.read_text(encoding="utf-8", errors="ignore")
            parts.append(raw)

    if not parts:
        raise FileNotFoundError(
            "No training data found.  Place .txt files in training_data/ "
            "or run download_data.py first."
        )
    return "\n".join(parts)

def clean_text(text: str) -> str:
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s']", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text

def build_models(text: str):
    tokens = clean_text(text).split()
    if not tokens:
        return {
            "unigrams": Counter(),
            "bigrams": defaultdict(Counter),
            "trigrams": defaultdict(Counter),
            "total_tokens": 0,
        }

    unigrams = Counter(tokens)

    bigrams = defaultdict(Counter)
    for i in range(len(tokens) - 1):
        bigrams[tokens[i]][tokens[i + 1]] += 1

    trigrams = defaultdict(Counter)
    for i in range(len(tokens) - 2):
        trigrams[(tokens[i], tokens[i + 1])][tokens[i + 2]] += 1

    return {
        "unigrams": unigrams,
        "bigrams": bigrams,
        "trigrams": trigrams,
        "total_tokens": len(tokens),
    }

LETTERS = "abcdefghijklmnopqrstuvwxyz'"

def _splits(word):
    return [(word[:i], word[i:]) for i in range(len(word) + 1)]

def _edits1(word):
    pairs = _splits(word)
    deletes    = [a + b[1:]             for a, b in pairs if b]
    transposes = [a + b[1] + b[0] + b[2:] for a, b in pairs if len(b) > 1]
    replaces   = [a + c + b[1:]         for a, b in pairs if b for c in LETTERS]
    inserts    = [a + c + b             for a, b in pairs for c in LETTERS]
    return set(deletes + transposes + replaces + inserts)

def _edits2(word):
    return {e2 for e1 in _edits1(word) for e2 in _edits1(e1)}

def _known(words, vocabulary):
    return {w for w in words if w in vocabulary}

def autocorrect_word(word: str, vocabulary: Counter) -> str:
    word = word.lower().strip()
    if not word:
        return word

    if word in vocabulary:
        return word

    candidates = _known(_edits1(word), vocabulary)

    if not candidates:
        candidates = _known(_edits2(word), vocabulary)

    if candidates:
        return max(candidates, key=lambda w: vocabulary[w])
    return word  

def predict_next_word(user_input: str, models, top_k: int = 5):
    tokens = clean_text(user_input).split()
    if not tokens:
        return []

    vocab_size = len(models["unigrams"])

    if len(tokens) >= 2:
        context = (tokens[-2], tokens[-1])
        if context in models["trigrams"]:
            counter = models["trigrams"][context]
            total = sum(counter.values())
            scored = [
                (w, (c + 1) / (total + vocab_size))
                for w, c in counter.items()
            ]
            scored.sort(key=lambda x: x[1], reverse=True)
            return [(w, round(p, 6)) for w, p in scored[:top_k]]

    last = tokens[-1]
    if last in models["bigrams"]:
        counter = models["bigrams"][last]
        total = sum(counter.values())
        scored = [
            (w, (c + 1) / (total + vocab_size))
            for w, c in counter.items()
        ]
        scored.sort(key=lambda x: x[1], reverse=True)
        return [(w, round(p, 6)) for w, p in scored[:top_k]]

    total = models["total_tokens"]
    scored = [
        (w, (c + 1) / (total + vocab_size))
        for w, c in models["unigrams"].most_common(top_k)
    ]
    return [(w, round(p, 6)) for w, p in scored]

def main():
    print("Loading training data …")
    text = load_all_texts()

    print("Building language models …")
    models = build_models(text)
    vocabulary = models["unigrams"]

    data_sources = []
    if TRAINING_DIR.is_dir():
        data_sources.extend(p.name for p in sorted(TRAINING_DIR.glob("*.txt")))

    print(f"\n{'='*50}")
    print(f"  Training complete!")
    print(f"  Sources       : {len(data_sources)} files")
    print(f"  Total tokens  : {models['total_tokens']:,}")
    print(f"  Vocabulary    : {len(vocabulary):,} unique words")
    print(f"{'='*50}\n")

    while True:
        try:
            user_input = input("Enter the Word or Sentance (Press 'q' to quit): ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nBye!")
            break

        if user_input.lower() == "q":
            print("Bye!")
            break
        if not user_input:
            continue

        corrected_tokens = [
            autocorrect_word(w, vocabulary) for w in user_input.split()
        ]
        corrected = " ".join(corrected_tokens)

        predictions = predict_next_word(corrected, models)

        print(f"\n  You entered : {user_input}")
        if corrected != user_input.lower():
            print(f"  Suggested correction : {corrected}")
        print("  Likely next words :")
        if predictions:
            for word, prob in predictions:
                print(f"    - {word}  (p={prob})")
        else:
            print("    (no prediction available)")
        print()

if __name__ == "__main__":
    main()