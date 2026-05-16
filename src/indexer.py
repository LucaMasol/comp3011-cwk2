import json
import re
from pathlib import Path
from typing import Any

from crawler import CrawledPage

INDEX_FILE_PATH = Path("data/index.json")
WORD_PATTERN = re.compile(r"[a-z0-9]+(?:'[a-z0-9]+)?")


InvertedIndex = dict[str, dict[str, dict[str, int | list[int]]]]


def tokenise(text: str) -> list[str]:
  """Split text into tokens"""
  return WORD_PATTERN.findall(text.lower())


def build_index(pages: list[CrawledPage]) -> InvertedIndex:
  """Build inverted index from crawled pages"""
  index: InvertedIndex = {}

  for page in pages:
    words = tokenise(page.text)

    for position, word in enumerate(words):
      word_entry = index.setdefault(word, {})
      page_entry = word_entry.setdefault(
        page.url,
        {
          "frequency": 0,
          "positions": [],
        },
      )

      page_entry["frequency"] = int(page_entry["frequency"]) + 1
      positions = page_entry["positions"]

      if isinstance(positions, list):
        positions.append(position)

  return index


def save_index(index: InvertedIndex, file_path: Path = INDEX_FILE_PATH) -> None:
  file_path.parent.mkdir(parents=True, exist_ok=True)

  with file_path.open("w", encoding="utf-8") as index_file:
    json.dump(index, index_file, indent=2, sort_keys=True)


def load_index(file_path: Path = INDEX_FILE_PATH) -> InvertedIndex | None:
  if not file_path.exists():
    return None

  try:
    with file_path.open("r", encoding="utf-8") as index_file:
      loaded_index: Any = json.load(index_file)
  except json.JSONDecodeError:
    return None

  return loaded_index


def get_index_entry(index: InvertedIndex, word: str) -> dict[str, dict[str, int | list[int]]]:
  """Return the index entry for one word"""
  tokens = tokenise(word)

  if len(tokens) != 1:
    return {}

  return index.get(tokens[0], {})
