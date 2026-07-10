import os
import re
import sys
import urllib.request
import urllib.error

BOOKS = {
    "pride_and_prejudice.txt": "https://www.gutenberg.org/cache/epub/1342/pg1342.txt",
    "moby_dick.txt": "https://www.gutenberg.org/cache/epub/2701/pg2701.txt",
    "great_expectations.txt": "https://www.gutenberg.org/cache/epub/1400/pg1400.txt",
    "dracula.txt": "https://www.gutenberg.org/cache/epub/345/pg345.txt",
    "war_of_the_worlds.txt": "https://www.gutenberg.org/cache/epub/36/pg36.txt",
    "tale_of_two_cities.txt": "https://www.gutenberg.org/cache/epub/98/pg98.txt",
    "frankenstein.txt": "https://www.gutenberg.org/cache/epub/84/pg84.txt",
    "alice_in_wonderland.txt": "https://www.gutenberg.org/cache/epub/11/pg11.txt",
}

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "training_data")

def strip_gutenberg_boilerplate(text: str) -> str:
    start_markers = [
        r"\*\*\*\s*START OF (THE|THIS) PROJECT GUTENBERG EBOOK",
        r"\*\*\* START OF THIS PROJECT GUTENBERG",
    ]
    for pattern in start_markers:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            text = text[match.end():]
            break

    end_markers = [
        r"\*\*\*\s*END OF (THE|THIS) PROJECT GUTENBERG EBOOK",
        r"\*\*\* END OF THIS PROJECT GUTENBERG",
    ]
    for pattern in end_markers:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            text = text[:match.start()]
            break

    return text.strip()

def download_book(name: str, url: str, output_dir: str) -> bool:
    output_path = os.path.join(output_dir, name)

    if os.path.exists(output_path):
        size_kb = os.path.getsize(output_path) / 1024
        print(f"  [SKIP] {name} already exists ({size_kb:.0f} KB)")
        return True

    print(f"  [GET]  {name} ... ", end="", flush=True)
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=30) as resp:
            raw = resp.read().decode("utf-8", errors="ignore")
    except (urllib.error.URLError, OSError) as exc:
        print(f"FAILED ({exc})")
        return False

    cleaned = strip_gutenberg_boilerplate(raw)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(cleaned)

    size_kb = len(cleaned.encode("utf-8")) / 1024
    print(f"OK ({size_kb:.0f} KB)")
    return True

def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    print(f"Downloading {len(BOOKS)} books to: {OUTPUT_DIR}\n")

    success = 0
    failed = 0
    for name, url in BOOKS.items():
        if download_book(name, url, OUTPUT_DIR):
            success += 1
        else:
            failed += 1

    print(f"\nDone: {success} downloaded, {failed} failed.")
    if failed:
        print("Re-run this script to retry failed downloads.")
        sys.exit(1)

if __name__ == "__main__":
    main()