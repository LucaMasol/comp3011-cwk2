from dataclasses import dataclass

from indexer import InvertedIndex, get_index_entry, tokenise


@dataclass(frozen=True)
class SearchResult:
  """A page that matched a search query"""
  url: str
  appearances: int


def find_pages(index: InvertedIndex, query: str) -> list[SearchResult]:
  """Find each page containing every word in the query"""
  query_words = tokenise(query)

  if not query_words:
    return []

  # Remove duplicate query words
  unique_query_words = list(dict.fromkeys(query_words))
  matching_page_sets: list[set[str]] = []

  for word in unique_query_words:
    word_entry = get_index_entry(index, word)

    if not word_entry:
      return []

    matching_page_sets.append(set(word_entry.keys()))

  # Keep only pages that contain each word in arguments (intersection / AND statement)
  matching_pages = set.intersection(*matching_page_sets)
  results: list[SearchResult] = []

  for page_url in matching_pages:
    appearances = 0

    # `appearances`` is the sum of per-word frequencies on the page
    for word in unique_query_words:
      word_entry = get_index_entry(index, word)
      page_entry = word_entry[page_url]
      appearances += int(page_entry["frequency"])

    results.append(SearchResult(url=page_url, appearances=appearances))

  return sorted(results, key=lambda result: (-result.appearances, result.url))


def format_index_entry(index: InvertedIndex, word: str) -> str:
  """Format a word's index entry for output"""
  entry = get_index_entry(index, word)
  tokens = tokenise(word)

  if len(tokens) != 1:
    return "Please provide exactly one word."

  normalised_word = tokens[0]

  if not entry:
    return f"No index entry found for '{normalised_word}'."

  lines = [f"Index entry for '{normalised_word}':"]

  for page_url in sorted(entry):
    page_entry = entry[page_url]
    frequency = page_entry["frequency"]
    positions = page_entry["positions"]

    lines.append(f"- {page_url}")
    lines.append(f"  frequency: {frequency}")
    lines.append(f"  positions: {positions}\n")

  return "\n".join(lines)


def format_search_results(results: list[SearchResult], query: str) -> str:
  """Format search results for terminal output"""
  query_words = tokenise(query)

  if not query_words:
    return "Please provide at least one search word."

  normalised_query = " ".join(query_words)

  if not results:
    return f"No pages found for '{normalised_query}'."

  lines = [f"Found {len(results)} page(s) for '{normalised_query}':"]

  for result in results:
    lines.append(f"- {result.url} (appearances: {result.appearances})")

  return "\n".join(lines)
