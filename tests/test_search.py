import sys
import unittest
from pathlib import Path

SRC_DIR = Path(__file__).resolve().parents[1] / "src"
sys.path.insert(0, str(SRC_DIR))

from search import SearchResult, find_pages, format_index_entry, format_search_results


class TestSearch(unittest.TestCase):
  def setUp(self) -> None:
    self.index = {
      "good": {
        "https://quotes.toscrape.com/page/1/": {
          "frequency": 2,
          "positions": [0, 3],
        },
        "https://quotes.toscrape.com/page/2/": {
          "frequency": 1,
          "positions": [4],
        },
      },
      "friends": {
        "https://quotes.toscrape.com/page/1/": {
          "frequency": 1,
          "positions": [1],
        },
        "https://quotes.toscrape.com/page/3/": {
          "frequency": 3,
          "positions": [0, 2, 5],
        },
      },
      "books": {
        "https://quotes.toscrape.com/page/2/": {
          "frequency": 4,
          "positions": [1, 2, 5, 8],
        },
      },
    }

  def test_find_pages_returns_pages_containing_single_word(self) -> None:
    # GIVEN an index containing the word "good"
    # WHEN find_pages is called with that word
    results = find_pages(self.index, "good")

    # THEN all pages containing the word are returned
    self.assertEqual(
      results,
      [
        SearchResult(url="https://quotes.toscrape.com/page/1/", appearances=2),
        SearchResult(url="https://quotes.toscrape.com/page/2/", appearances=1),
      ],
    )

  def test_find_pages_is_case_insensitive(self) -> None:
    # GIVEN an index containing lowercase tokens
    # WHEN find_pages is called with uppercase input
    results = find_pages(self.index, "GOOD")

    # THEN it still matches the lowercase indexed word
    self.assertEqual(
      results,
      [
        SearchResult(url="https://quotes.toscrape.com/page/1/", appearances=2),
        SearchResult(url="https://quotes.toscrape.com/page/2/", appearances=1),
      ],
    )

  def test_find_pages_uses_and_logic_for_multiple_words(self) -> None:
    # GIVEN an index where only page 1 contains both "good" and "friends"
    # WHEN find_pages is called with both words
    results = find_pages(self.index, "good friends")

    # THEN only pages containing every query word are returned
    self.assertEqual(
      results,
      [
        SearchResult(url="https://quotes.toscrape.com/page/1/", appearances=3),
      ],
    )

  def test_find_pages_does_not_match_word_fragments(self) -> None:
    # GIVEN an index containing "friends" but not "friendship"
    # WHEN searching for "friendship"
    results = find_pages(self.index, "friendship")

    # THEN "friends" is not treated as a match
    self.assertEqual(results, [])

  def test_find_pages_returns_empty_list_for_unknown_word(self) -> None:
    # GIVEN a query word that is not in the index
    # WHEN find_pages is called
    results = find_pages(self.index, "missing")

    # THEN no results are returned
    self.assertEqual(results, [])

  def test_find_pages_returns_empty_list_for_empty_query(self) -> None:
    # GIVEN an empty query
    # WHEN find_pages is called
    results = find_pages(self.index, "")

    # THEN no results are returned
    self.assertEqual(results, [])

  def test_find_pages_ignores_duplicate_query_words(self) -> None:
    # GIVEN a query with the same word repeated
    # WHEN find_pages is called
    results = find_pages(self.index, "good good")

    # THEN the repeated query word is only counted once for matching
    self.assertEqual(
      results,
      [
        SearchResult(url="https://quotes.toscrape.com/page/1/", appearances=2),
        SearchResult(url="https://quotes.toscrape.com/page/2/", appearances=1),
      ],
    )

  def test_find_pages_sorts_by_appearances_then_url(self) -> None:
    # GIVEN multiple matching pages
    # WHEN find_pages is called
    results = find_pages(self.index, "good")

    # THEN results are sorted by appearances descending, then URL ascending
    self.assertEqual(results[0].url, "https://quotes.toscrape.com/page/1/")
    self.assertEqual(results[0].appearances, 2)
    self.assertEqual(results[1].url, "https://quotes.toscrape.com/page/2/")
    self.assertEqual(results[1].appearances, 1)

  def test_format_index_entry_formats_existing_word(self) -> None:
    # GIVEN an index containing "good"
    # WHEN format_index_entry is called
    output = format_index_entry(self.index, "good")

    # THEN the output contains the word, page URLs, frequency, and positions
    self.assertIn("Index entry for 'good':", output)
    self.assertIn("https://quotes.toscrape.com/page/1/", output)
    self.assertIn("frequency: 2", output)
    self.assertIn("positions: [0, 3]", output)

  def test_format_index_entry_returns_message_for_missing_word(self) -> None:
    # GIVEN an index without the requested word
    # WHEN format_index_entry is called
    output = format_index_entry(self.index, "missing")

    # THEN a useful not-found message is returned
    self.assertEqual(output, "No index entry found for 'missing'.")

  def test_format_index_entry_rejects_multiple_words(self) -> None:
    # GIVEN multiple words
    # WHEN format_index_entry is called
    output = format_index_entry(self.index, "good friends")

    # THEN a useful validation message is returned
    self.assertEqual(output, "Please provide exactly one word.")

  def test_format_search_results_formats_results(self) -> None:
    # GIVEN search results
    results = [
      SearchResult(url="https://quotes.toscrape.com/page/1/", appearances=3),
    ]

    # WHEN format_search_results is called
    output = format_search_results(results, "good friends")

    # THEN the output lists the matching page and appearances
    self.assertIn("Found 1 page(s) for 'good friends':", output)
    self.assertIn("https://quotes.toscrape.com/page/1/", output)
    self.assertIn("appearances: 3", output)

  def test_format_search_results_returns_message_for_no_results(self) -> None:
    # GIVEN no search results
    # WHEN format_search_results is called
    output = format_search_results([], "missing")

    # THEN a useful not-found message is returned
    self.assertEqual(output, "No pages found for 'missing'.")

  def test_format_search_results_rejects_empty_query(self) -> None:
    # GIVEN an empty query
    # WHEN format_search_results is called
    output = format_search_results([], "")

    # THEN a useful validation message is returned
    self.assertEqual(output, "Please provide at least one search word.")


if __name__ == "__main__":
  unittest.main()
