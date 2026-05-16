from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

SRC_DIR = Path(__file__).resolve().parents[1] / "src"
sys.path.insert(0, str(SRC_DIR))

from crawler import CrawledPage
from indexer import build_index, get_index_entry, load_index, save_index, tokenise


class TestIndexer(unittest.TestCase):
  def test_tokenise_lowercases_words(self) -> None:
    # GIVEN a string with mixed case words
    # WHEN tokenise is called
    tokens = tokenise("Good FRIENDS are good.")
    # THEN all words are lowercased
    self.assertEqual(tokens, ["good", "friends", "are", "good"])

  def test_tokenise_matches_full_words_not_word_fragments(self) -> None:
    # GIVEN words that could be confused as fragments
    # WHEN tokenise is called
    tokens = tokenise("friends friendship friend")
    # THEN full words are extracted as separate tokens
    self.assertEqual(tokens, ["friends", "friendship", "friend"])

  def test_tokenise_keeps_apostrophes_inside_words(self) -> None:
    # GIVEN words with apostrophes
    # WHEN tokenise is called
    tokens = tokenise("Don't stop believing.")
    # THEN apostrophes within words are preserved
    self.assertEqual(tokens, ["don't", "stop", "believing"])

  def test_build_index_stores_frequency_and_positions(self) -> None:
    # GIVEN multiple pages with repeated and unique words
    pages = [
      CrawledPage(
        url="https://quotes.toscrape.com/page/1/",
        text="Good friends are good",
      ),
      CrawledPage(
        url="https://quotes.toscrape.com/page/2/",
        text="Friends matter",
      ),
    ]

    # WHEN build_index is called
    index = build_index(pages)

    # THEN an index with frequency and position data is created
    self.assertEqual(
      index["good"]["https://quotes.toscrape.com/page/1/"],
      {
        "frequency": 2,
        "positions": [0, 3],
      },
    )
    self.assertEqual(
      index["friends"]["https://quotes.toscrape.com/page/1/"],
      {
        "frequency": 1,
        "positions": [1],
      },
    )
    self.assertEqual(
      index["friends"]["https://quotes.toscrape.com/page/2/"],
      {
        "frequency": 1,
        "positions": [0],
      },
    )

  def test_get_index_entry_returns_entry_for_one_word(self) -> None:
    # GIVEN an index and a word in it
    pages = [
      CrawledPage(
        url="https://quotes.toscrape.com/page/1/",
        text="Good friends are good",
      ),
    ]
    index = build_index(pages)

    # WHEN get_index_entry is called with that word
    entry = get_index_entry(index, "GOOD")

    # THEN the index entry for that word is returned
    self.assertEqual(
      entry,
      {
        "https://quotes.toscrape.com/page/1/": {
          "frequency": 2,
          "positions": [0, 3],
        },
      },
    )

  def test_get_index_entry_returns_empty_dict_for_unknown_word(self) -> None:
    # GIVEN an index and a word not in it
    index = build_index([
      CrawledPage(url="https://quotes.toscrape.com/page/1/", text="Good friends")
    ])

    # WHEN get_index_entry is called with that word
    entry = get_index_entry(index, "missing")

    # THEN an empty dict is returned
    self.assertEqual(entry, {})

  def test_get_index_entry_rejects_multiple_words(self) -> None:
    # GIVEN an index and multiple words
    index = build_index([
      CrawledPage(url="https://quotes.toscrape.com/page/1/", text="Good friends")
    ])

    # WHEN get_index_entry is called with multiple words
    entry = get_index_entry(index, "good friends")

    # THEN an empty dict is returned (only single words are supported)
    self.assertEqual(entry, {})

  def test_save_and_load_index_round_trip(self) -> None:
    # GIVEN an index
    pages = [
      CrawledPage(
        url="https://quotes.toscrape.com/page/1/",
        text="Good friends are good",
      ),
    ]
    index = build_index(pages)

    # WHEN save_index and load_index are called in sequence
    with tempfile.TemporaryDirectory() as temp_dir:
      file_path = Path(temp_dir) / "index.json"
      save_index(index, file_path)
      loaded_index = load_index(file_path)

    # THEN the loaded index matches the original
    self.assertEqual(loaded_index, index)

  def test_save_index_creates_parent_directory(self) -> None:
    # GIVEN a nested file path that doesn't exist
    index = build_index([
      CrawledPage(url="https://quotes.toscrape.com/page/1/", text="Good friends")
    ])

    with tempfile.TemporaryDirectory() as temp_dir:
      # WHEN save_index is called
      file_path = Path(temp_dir) / "nested" / "index.json"
      save_index(index, file_path)

      # THEN parent directories are created
      self.assertTrue(file_path.exists())

  def test_load_index_returns_none_when_file_missing(self) -> None:
    # GIVEN a file path that doesn't exist
    # WHEN load_index is called
    with tempfile.TemporaryDirectory() as temp_dir:
      file_path = Path(temp_dir) / "missing.json"
      loaded_index = load_index(file_path)
    # THEN None is returned
    self.assertIsNone(loaded_index)

  def test_load_index_returns_none_when_json_invalid(self) -> None:
    # GIVEN a file with invalid JSON content
    # WHEN load_index is called
    with tempfile.TemporaryDirectory() as temp_dir:
      file_path = Path(temp_dir) / "index.json"
      file_path.write_text("", encoding="utf-8")
      loaded_index = load_index(file_path)
    # THEN None is returned
    self.assertIsNone(loaded_index)


if __name__ == "__main__":
  unittest.main()
