## Setup
1. Create virtual environment: `py -m venv venv`
2. Activate virtual environment: `venv\Scripts\Activate.ps1`
3. Install dependencies: `pip install -r .\requirements.txt`

## Running the application
To open the shell, run `py src/main.py` in the project root.

| Command | Description |
| --- | --- |
| `build [maxPages] [-v]` | Build and store inverted index to `./data/index.json` |
| `load` | Load inverted index from `./data/index.json` |
| `print <word>` | Print the index entry for a word |
| `find <word> [word ...]` | Find pages matching a list of words |
| `help` | Show commands and their usage |
| `exit \| quit` | Exit shell |

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

Coverage results will change as the codebase changes, though this was updated on last commit.


### Crawler
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
* Politeness delays between requests

### Indexer:
* Tokenising behaviour, including apostrophes inside words
* Case-insensitive indexing
* Frequency and position storage
* Fetching a word's index entry
* Returning an empty entry for unknown words when indexing/ printing
* Rejecting multiple words in `get_index_entry` (printing)
* Saving/loading index JSON
* Creating parent directories when saving an index
* Returning `None` for missing or invalid index files

### Search
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
