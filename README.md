## Setup
1. Create virtual environment: `py -m venv venv`
2. Activate virtual environment: `.venv\Scripts\Activate.ps1`
3. Install dependencies: `pip install -r .\requirements.txt`

## Running the application
To open the shell, run `py src/main.py` in the project root.

| Command | Description |
| --- | --- |
| `build [maxPages] [-v]` | Build and store inverted index to `./data/index.json` |
| `load` | Load inverted index from `./data/index.json` |
| `print <word>` | Print the index entry for a word |
| `find <word> [word ...]` | Find pages matching a string |
| `help` | Show commands and their usage |
| `exit \| quit` | Exit shell |

## Testing Suite
Run unit tests from root with `py -m unittest discover tests`
### Crawler
* URL normalisation
* Internal/external URL checking
* Link extraction
* Meaningful text extraction
* Crawling without real network requests
* Extracting URLs from CrawledPage objects

### Indexer:
* Tokenising
* Case-insensitive indexing
* Full-word behaviour
* Frequency and position storage
* Getting one word’s index entry
* Saving/loading index JSON
* Missing/invalid index files