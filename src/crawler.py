import time
from collections import deque
from dataclasses import dataclass
from typing import Iterable
from urllib.parse import urldefrag, urljoin, urlparse

import requests
from bs4 import BeautifulSoup

BASE_URL = "https://quotes.toscrape.com/"
POLITENESS_DELAY_SECONDS = 6.0
REQUEST_TIMEOUT_SECONDS = 10


@dataclass(frozen=True)
class CrawledPage:
  """Text and URL of a crawled page"""
  url: str
  text: str


def normalise_url(url: str) -> str:
  """Remove URL fragments and normalise trailing slashes"""
  url, _ = urldefrag(url)

  if url.endswith("/"):
    return url

  parsed_url = urlparse(url)

  if parsed_url.path and "." not in parsed_url.path.rsplit("/", maxsplit=1)[-1]:
    return f"{url}/"

  return url


def is_internal_url(url: str, base_url: str = BASE_URL) -> bool:
  """Return True when a URL belongs to the target website."""
  parsed_url = urlparse(url)
  parsed_base_url = urlparse(base_url)

  return parsed_url.scheme in {"http", "https"} and parsed_url.netloc == parsed_base_url.netloc


def extract_links(html: str, page_url: str, base_url: str = BASE_URL) -> list[str]:
  """Extract same-site links from one HTML page."""
  soup = BeautifulSoup(html, "html.parser")
  links: list[str] = []

  for anchor in soup.find_all("a", href=True):
    absolute_url = normalise_url(urljoin(page_url, anchor["href"]))

    if is_internal_url(absolute_url, base_url):
      links.append(absolute_url)

  return links


def extract_page_text(html: str) -> str:
  """Extract meaningful text from page"""
  soup = BeautifulSoup(html, "html.parser")
  pieces: list[str] = []

  for quote in soup.select(".quote"):
    quote_text = quote.select_one(".text")
    author = quote.select_one(".author")
    tags = quote.select(".tags .tag")

    if quote_text is not None:
      pieces.append(quote_text.get_text(" ", strip=True))

    if author is not None:
      pieces.append(author.get_text(" ", strip=True))

    for tag in tags:
      pieces.append(tag.get_text(" ", strip=True))

  author_details = soup.select_one(".author-details")

  if author_details is not None:
    pieces.append(author_details.get_text(" ", strip=True))

  return " ".join(piece for piece in pieces if piece)


def fetch_html(url: str) -> str:
  """Fetch page and return the HTML"""
  response = requests.get(url, timeout=REQUEST_TIMEOUT_SECONDS)
  response.raise_for_status()
  return response.text


def crawl_site(
  verbose: bool = False,
  start_url: str = BASE_URL,
  delay_seconds: float = POLITENESS_DELAY_SECONDS,
  max_pages: int | None = None,
) -> list[CrawledPage]:
  """
  Crawl website and return pages with extracted text.
  Performs a BFS crawl over internal links only.
  """
  start_url = normalise_url(start_url)
  queue: deque[str] = deque([start_url])
  queued_urls = {start_url}
  visited_urls: set[str] = set()
  crawled_pages: list[CrawledPage] = []
  last_request_time: float | None = None

  while queue:
    if max_pages is not None and len(visited_urls) >= max_pages:
      break

    current_url = queue.popleft()

    if current_url in visited_urls:
      continue

    if last_request_time is not None:
      elapsed = time.monotonic() - last_request_time
      remaining_delay = delay_seconds - elapsed

      if remaining_delay > 0:
        time.sleep(remaining_delay)

    try:
      html = fetch_html(current_url)
    except requests.RequestException as error:
      print(f"Warning: failed to crawl {current_url}: {error}")
      visited_urls.add(current_url)
      continue

    last_request_time = time.monotonic()
    visited_urls.add(current_url)

    page_text = extract_page_text(html)

    if page_text:
      crawled_pages.append(CrawledPage(url=current_url, text=page_text))

    for discovered_url in extract_links(html, current_url):
      if discovered_url not in visited_urls and discovered_url not in queued_urls:
        queue.append(discovered_url)
        queued_urls.add(discovered_url)

    if verbose:
      print(f"Crawled: {current_url} | Queued: {len(queue)} | Crawled pages: {len(crawled_pages)}")

  return crawled_pages


def page_urls(pages: Iterable[CrawledPage]) -> list[str]:
  """Return only the URLs from a collection of crawled pages."""
  return [page.url for page in pages]
