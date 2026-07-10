# Autocorrect & Next-Word Prediction

An NLP-based autocorrect and next-word prediction system built with Python. The model trains on a corpus of classic literature from Project Gutenberg, using n-gram language models for word prediction and edit-distance algorithms for spelling correction.

## Features

- **Spelling Correction** — Detects and corrects misspelled words using Norvig's edit-distance algorithm, weighted by word frequency in the training corpus.
- **Next-Word Prediction** — Predicts the most likely next word using trigram → bigram → unigram back-off with Laplace smoothing.
- **Multi-Source Training** — Automatically loads and trains on all `.txt` files in the `training_data/` directory.
- **Large Vocabulary** — Trained on 1M+ tokens across 8 classic novels, yielding ~28,000 unique words.

## Project Structure

```
Project-1/
├── autocorrect.py       # Main application (autocorrect + prediction)
├── download_data.py     # Script to download training data from Project Gutenberg
├── training_data/       # Training corpus (downloaded .txt files)
│   ├── alice_in_wonderland.txt
│   ├── dracula.txt
│   ├── frankenstein.txt
│   ├── great_expectations.txt
│   ├── moby_dick.txt
│   ├── pride_and_prejudice.txt
│   ├── tale_of_two_cities.txt
│   └── war_of_the_worlds.txt
└── README.md
```

## How It Works

### Autocorrect (Edit Distance)

When a user types a misspelled word, the system:

1. Checks if the word exists in the vocabulary — if yes, it's correct.
2. Generates all words that are **1 edit** away (insertions, deletions, replacements, transpositions).
3. If no match, generates all words that are **2 edits** away.
4. Among the candidates found in the vocabulary, picks the one with the **highest corpus frequency**.

### Next-Word Prediction (N-Gram Model)

The system uses a back-off strategy:

1. **Trigram** — If the last two words match a known trigram context, predict the third word.
2. **Bigram** — Otherwise, if the last word matches a known bigram, predict the next word.
3. **Unigram** — As a fallback, return the most frequent words in the corpus.

All predictions use **Laplace (add-1) smoothing** to handle unseen word combinations.

## Setup & Usage

### 1. Download Training Data

Run the download script to fetch 8 classic novels from Project Gutenberg:

```bash
python download_data.py
```

This creates a `training_data/` folder with the downloaded books (~5 MB total). Only needs to be run once.

### 2. Run the Autocorrect

```bash
python autocorrect.py
```

**Example session:**

```
Loading training data …
Building language models …

==================================================
  Training complete!
  Sources       : 8 files
  Total tokens  : 1,003,230
  Vocabulary    : 27,938 unique words
==================================================

Enter the Word or Sentance (Press 'q' to quit): what do you do

  You entered : what do you do
  Likely next words :
    - not  (p=0.002066)
    - it  (p=0.000392)
    - i  (p=0.000285)
    - but  (p=0.000214)
    - you  (p=0.000214)

Enter the Word or Sentance (Press 'q' to quit): arifivial

  You entered : arifivial
  Suggested correction : artificial
  Likely next words :
    - knee  (p=6.9e-05)

Enter the Word or Sentance (Press 'q' to quit): q
Bye!
```

## Training Data

The model trains on 8 public-domain novels from [Project Gutenberg](https://www.gutenberg.org/):

| Book | Author |
|------|--------|
| Pride and Prejudice | Jane Austen |
| Moby Dick | Herman Melville |
| Great Expectations | Charles Dickens |
| Dracula | Bram Stoker |
| The War of the Worlds | H.G. Wells |
| A Tale of Two Cities | Charles Dickens |
| Frankenstein | Mary Shelley |
| Alice's Adventures in Wonderland | Lewis Carroll |

To add more training data, simply drop any `.txt` file into the `training_data/` folder and re-run `autocorrect.py`.

## Requirements

- Python 3.7+
- No external libraries required (uses only Python standard library)

## Tech Stack

| Component | Implementation |
|-----------|---------------|
| Language | Python |
| Autocorrect | Norvig's edit-distance algorithm |
| Prediction | N-gram model (unigram, bigram, trigram) |
| Smoothing | Laplace (add-1) smoothing |
| Data Source | Project Gutenberg (public domain) |
