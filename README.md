# COMP3011 - CWK2 - QUOTES SCRAPER
## Overview
This project provides a command-line shell tool for https://quotes.toscrape.com/. It crawls the site and scrapes meaningful text such as quotes, descriptions, authors, and tags that it uses to build an inverted index of tokenised words. The index stores each word case-insensitively, the page it appears on, the frequency on each page, and the position of the word on each page. It does not index structural words such as site headers and the login page, as these would appear on every web page and provide no meaningful data.

## Structure
* `src`
  * `crawler.py` - BFS crawler, URL normalisation, link filtering, request delay
  * `indexer.py` - tokenisation, creating/loading inverted index
  * `search.py` - `print` and `find` logic
  * `main.py` - command-line interface shell
* `tests`
  * `test_crawler.py`
  * `test_indexer.py`
  * `test_search.py`
* `data`
  * `index.json` - Inverted index file


## Dependencies
The project uses the following Python packages:
* `requests` - HTTP requests
* `beautifulsoup4` - HTML parsing
* `coverage` - for test coverage reporting


## Setup
**Windows**:
1. Create virtual environment: `py -m venv venv`
2. Activate virtual environment: `venv\Scripts\Activate.ps1`
3. Install dependencies: `pip install -r .\requirements.txt`

**Linux/macOS**:
1. Create virtual environment: `python3 -m venv venv`
2. Activate virtual environment: `source venv/bin/activate`
3. Install dependencies: `pip install -r ./requirements.txt`

## Running the application
To open the shell, run `py src/main.py` in the project root.

| Command | Description |
| --- | --- |
| `build [maxPages] [-v]` | Build and store inverted index to `./data/index.json`. If `maxPages` is omitted, all pages are crawled and indexed. |
| `load` | Load inverted index from `./data/index.json`. |
| `print <word>` | Print the index entry for a word. |
| `find <word> [word ...]` | Find pages matching a list of words. |
| `help` | Show commands and their usage. |
| `exit \| quit` | Exit shell. |

## Example Usage
```bash
$ py src/main.py
> build -v
> load
> print love
> print wordThatIsNotIndexed
> find good friends
> find friendship
> find
> print good friends
```


## Testing Suite
Run unit tests from root with `py -m unittest discover tests`

To find coverage of tests, run:
1. `py -m coverage run --source=src -m unittest discover tests`
2. `py -m coverage report -m`

Example coverage results from previous testing:
| File | Statements | Miss | Coverage | Notes|
| --- | --- | --- | --- | --- |
| `src/crawler.py` | 91  | 1   | 99% | Remaining uncovered line is a defense against URL-handling, which is difficult to reach in testing |
| `src/indexer.py` | 40  | 0   | 100% |  |
| `src/search.py`  | 53  | 0   | 100% |  |
| __TOTAL__ | __184__ | __1__ | __99%__ | `src/main.py` not covered in tests, as not relevant to units and is instead simply the interface |

Coverage results may change as the codebase changes, though these results were updated on the project's final commit.


### Crawler tests
* URL normalisation (fragments, page paths, trailing slashes, file paths)
* Internal and external URL checking
* Link extraction that keeps only internal, normalised links
* Page text extraction for quotes, authors, tags, and author detail pages
* HTTP fetching
* Crawling without real network requests
* Crawling with `max_pages` limits
* Request error handling
* Verbose crawling output (`-v`)
* Extracting URLs from `CrawledPage` objects
* 6 second politeness delays between requests

### Indexer tests
* Tokenising behaviour, including apostrophes inside words
* Case-insensitive indexing
* Frequency and position storage
* Fetching a word's index entry
* Returning an empty entry for unknown words when printing index entries
* Rejecting multiple words in `get_index_entry` (printing)
* Saving/loading index JSON
* Creating parent directories when saving an index
* Returning `None` for missing or invalid index files

### Search tests
* Single-word search
* Case-insensitive search
* Multi-word AND search
* Full-word matching without fragment matches
* Empty and missing query handling
* Duplicate query word handling
* Result ordering by appearances, then URL
* Formatting output for `print <word>`
* Formatting output for missing and invalid `print` queries
* Formatting output for `find <word> [word ...]`
* Formatting output for empty and missing `find` queries


## Design decisions
The crawler uses breadth-first search so pages are discovered systematically from the homepage. URLs are normalised to avoid duplicate crawling caused by fragments or missing trailing slashes.

The inverted index is implemented as a nested dictionary:

```
{
  ...
  "friends": {
    "https://quotes.toscrape.com/author/Douglas-Adams/": {
      "frequency": 1,
      "positions": [
        240
      ]
    },
    "https://quotes.toscrape.com/page/2/": {
      "frequency": 8,
      "positions": [
        40,
        65,
        77,
        200,
        228,
        233,
        518,
        534
      ]
    },
    ...
  },
  "good": {
    ...
  }
  ...
}
```
This structure makes the `print` command efficient because the entry for a word can be retrieved directly in `O(1)` using a dictionary lookup. Multi-word find queries are handled by intersecting the page sets for each query word (simple AND statement).

The search tool uses case-insensitive tokenisation and full-word matching, meaning a search for 'friends' will not match '**friends**hip'.

## Limitations
The scraper tool is designed for the site structure of https://quotes.toscrape.com/, rather than arbitrary websites. It uses specific element tags in the HTML of the site to find meaningful data, which would not transfer well to other external sites without change to the code.

## Use of Generative AI
Generative AI tools were used throughout development as given in the coursework specification. It influenced most aspects of the application, though this was not without proper checks made on its outputs.

Generative AI was used for:
* Problem understanding of distinct areas to focus on such that development would be incremental
* Planning structure of each file
* Explanation and initial code structure generation of library tools such as `BeautifulSoup4`
* Code generation of repetitive functions and areas (testing suite, for example)
* Refactoring of written code for maintainability and future-proofing for upcoming features
* Debugging logical and runtime errors
* AI code reviews at the code repository before merging to the main branch (essentially treated as a pair programmer)
* Proof reading and refactoring of language/ structure of README.md
* Planning structure of video demonstration

The generative AI tools used were:
* ChatGPT - OpenAI. (2026). ChatGPT Large Language Model. Available at https://chat.openai.com/
* GitHub Copilot – GitHub. (2026). GitHub Copilot AI coding assistant. Available at https://github.com/features/copilot/