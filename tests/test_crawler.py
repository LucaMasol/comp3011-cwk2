import sys
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

import requests

SRC_DIR = Path(__file__).resolve().parents[1] / "src"
sys.path.insert(0, str(SRC_DIR))

import crawler
from crawler import CrawledPage


class TestCrawler(unittest.TestCase):
  def test_normalise_url_removes_fragment(self) -> None:
    # GIVEN a URL with a fragment
    # WHEN normalise_url is called
    url = crawler.normalise_url("https://quotes.toscrape.com/page/1/#quote")
    # THEN the fragment is removed
    self.assertEqual(url, "https://quotes.toscrape.com/page/1/")


  def test_normalise_url_adds_trailing_slash_for_page_paths(self) -> None:
    # GIVEN a page path without a trailing slash
    # WHEN normalise_url is called
    url = crawler.normalise_url("https://quotes.toscrape.com/page/1")
    # THEN a trailing slash is added
    self.assertEqual(url, "https://quotes.toscrape.com/page/1/")

  def test_normalise_url_keeps_existing_trailing_slash(self) -> None:
    # GIVEN a URL that already has a trailing slash
    # WHEN normalise_url is called
    url = crawler.normalise_url("https://quotes.toscrape.com/page/1/")
    # THEN the URL is returned unchanged
    self.assertEqual(url, "https://quotes.toscrape.com/page/1/")

  def test_is_internal_url_accepts_target_website(self) -> None:
    # GIVEN a URL from the target website
    # WHEN is_internal_url is called
    result = crawler.is_internal_url("https://quotes.toscrape.com/page/1/")
    # THEN it returns True
    self.assertTrue(result)


  def test_is_internal_url_rejects_external_website(self) -> None:
    # GIVEN a URL from an external website
    # WHEN is_internal_url is called
    result = crawler.is_internal_url("https://example.com/page/1/")
    # THEN it returns False
    self.assertFalse(result)

  def test_extract_links_returns_internal_normalised_links_only(self) -> None:
    # GIVEN HTML with internal and external links
    html = """
    <html>
      <body>
        <a href="/page/2">Next</a>
        <a href="https://quotes.toscrape.com/tag/life/">Life</a>
        <a href="https://example.com/">External</a>
      </body>
    </html>
    """

    # WHEN extract_links is called
    links = crawler.extract_links(html, "https://quotes.toscrape.com/")

    # THEN only internal links are returned and they are normalised
    self.assertEqual(
      links,
      [
        "https://quotes.toscrape.com/page/2/",
        "https://quotes.toscrape.com/tag/life/",
      ],
    )

  def test_extract_page_text_extracts_quote_author_and_tags(self) -> None:
    # GIVEN HTML with quote content, authors, tags, and other text
    html = """
    <html>
      <body>
        <h1>Quotes to Scrape</h1>
        <a href="/login">Login</a>
        <div class="quote">
          <span class="text">“A test quote.”</span>
          <small class="author">Test Author</small>
          <div class="tags">
            <a class="tag">testing</a>
            <a class="tag">example</a>
          </div>
        </div>
        <footer>Footer text that should be ignored</footer>
      </body>
    </html>
    """

    # WHEN extract_page_text is called
    text = crawler.extract_page_text(html)

    # THEN only quote, author, and tag text is extracted
    self.assertIn("A test quote", text)
    self.assertIn("Test Author", text)
    self.assertIn("testing", text)
    self.assertIn("example", text)
    self.assertNotIn("Quotes to Scrape", text)
    self.assertNotIn("Login", text)
    self.assertNotIn("Footer text", text)

  def test_extract_page_text_includes_author_details_page(self) -> None:
    # GIVEN an author details page
    html = """
    <html>
      <body>
        <div class="author-details">
          <h3 class="author-title">Test Author</h3>
          <p class="author-description">This is a test biography.</p>
        </div>
      </body>
    </html>
    """

    # WHEN extract_page_text is called
    text = crawler.extract_page_text(html)

    # THEN author details are extracted
    self.assertIn("Test Author", text)
    self.assertIn("This is a test biography.", text)

  def test_fetch_html_returns_response_text(self) -> None:
    # GIVEN a successful mocked HTTP response
    mock_response = Mock()
    mock_response.text = "<html>Success</html>"

    # WHEN fetch_html is called
    with patch("crawler.requests.get", return_value=mock_response) as mock_get:
      html = crawler.fetch_html("https://quotes.toscrape.com/")

    # THEN requests.get and raise_for_status are used correctly
    mock_get.assert_called_once_with(
      "https://quotes.toscrape.com/",
      timeout=crawler.REQUEST_TIMEOUT_SECONDS,
    )
    mock_response.raise_for_status.assert_called_once()
    self.assertEqual(html, "<html>Success</html>")

  def test_crawl_site_follows_internal_links_without_real_network(self) -> None:
    # GIVEN mocked pages with internal links
    page_one = """
    <html>
      <body>
        <div class="quote">
          <span class="text">“First quote.”</span>
          <small class="author">Author One</small>
        </div>
        <a href="/page/2/">Next</a>
      </body>
    </html>
    """
    page_two = """
    <html>
      <body>
        <div class="quote">
          <span class="text">“Second quote.”</span>
          <small class="author">Author Two</small>
        </div>
      </body>
    </html>
    """
    pages_by_url = {
      "https://quotes.toscrape.com/": page_one,
      "https://quotes.toscrape.com/page/2/": page_two,
    }
    def fake_fetch_html(url: str) -> str:
      return pages_by_url[url]

    # WHEN crawl_site is called
    with patch("crawler.fetch_html", side_effect=fake_fetch_html):
      pages = crawler.crawl_site(delay_seconds=0)

    # THEN all reachable pages are crawled and their text is extracted
    self.assertEqual(
      pages,
      [
        CrawledPage(url="https://quotes.toscrape.com/", text="“First quote.” Author One"),
        CrawledPage(url="https://quotes.toscrape.com/page/2/", text="“Second quote.” Author Two"),
      ],
    )

  def test_crawl_site_respects_max_pages(self) -> None:
    # GIVEN mocked pages where page 1 links to page 2
    page_one = """
    <html>
      <body>
        <div class="quote">
          <span class="text">“First quote.”</span>
          <small class="author">Author One</small>
        </div>
        <a href="/page/2/">Next</a>
      </body>
    </html>
    """
    page_two = """
    <html>
      <body>
        <div class="quote">
          <span class="text">“Second quote.”</span>
          <small class="author">Author Two</small>
        </div>
      </body>
    </html>
    """
    pages_by_url = {
      "https://quotes.toscrape.com/": page_one,
      "https://quotes.toscrape.com/page/2/": page_two,
    }

    def fake_fetch_html(url: str) -> str:
      return pages_by_url[url]

    # WHEN crawl_site is limited to one page
    with patch("crawler.fetch_html", side_effect=fake_fetch_html):
      pages = crawler.crawl_site(delay_seconds=0, max_pages=1)

    # THEN only one page is crawled
    self.assertEqual(
      pages,
      [
        CrawledPage(url="https://quotes.toscrape.com/", text="“First quote.” Author One"),
      ],
    )

  def test_crawl_site_handles_request_errors(self) -> None:
    # GIVEN fetch_html raises a request error
    def fake_fetch_html(_url: str) -> str:
      raise requests.RequestException("Network error")

    # WHEN crawl_site is called
    with patch("crawler.fetch_html", side_effect=fake_fetch_html):
      pages = crawler.crawl_site(delay_seconds=0, max_pages=1)

    # THEN the error is handled and no page is returned
    self.assertEqual(pages, [])

  def test_crawl_site_prints_verbose_progress(self) -> None:
    # GIVEN a mocked page and verbose mode enabled
    html = """
    <html>
      <body>
        <div class="quote">
          <span class="text">“Verbose quote.”</span>
          <small class="author">Verbose Author</small>
        </div>
      </body>
    </html>
    """

    # WHEN crawl_site is called
    with patch("crawler.fetch_html", return_value=html):
      with patch("builtins.print") as mock_print:
        pages = crawler.crawl_site(delay_seconds=0, max_pages=1, verbose=True)

    # THEN progress is printed
    self.assertEqual(
      pages,
      [
        CrawledPage(url="https://quotes.toscrape.com/", text="“Verbose quote.” Verbose Author"),
      ],
    )
    self.assertTrue(
      any("Crawled:" in str(call) for call in mock_print.call_args_list)
    )

  def test_page_urls_returns_only_urls(self) -> None:
    # GIVEN a list of crawled pages
    pages = [
      CrawledPage(url="https://quotes.toscrape.com/", text="Page one"),
      CrawledPage(url="https://quotes.toscrape.com/page/2/", text="Page two"),
    ]

    # WHEN page_urls is called
    urls = crawler.page_urls(pages)

    # THEN only the URLs are extracted and returned
    self.assertEqual(
      urls,
      [
        "https://quotes.toscrape.com/",
        "https://quotes.toscrape.com/page/2/",
      ],
    )


  def test_normalise_url_does_not_add_slash_to_file_paths(self) -> None:
    # GIVEN a URL that points to a file
    # WHEN normalise_url is called
    url = crawler.normalise_url("https://quotes.toscrape.com/static/style.css")

    # THEN no trailing slash is added
    self.assertEqual(url, "https://quotes.toscrape.com/static/style.css")

  def test_crawl_site_applies_politeness_delay_between_requests(self) -> None:
    # GIVEN two linked pages
    page_one = """
    <html>
      <body>
        <div class="quote">
          <span class="text">“First quote.”</span>
          <small class="author">Author One</small>
        </div>
        <a href="/page/2/">Next</a>
      </body>
    </html>
    """

    page_two = """
    <html>
      <body>
        <div class="quote">
          <span class="text">“Second quote.”</span>
          <small class="author">Author Two</small>
        </div>
      </body>
    </html>
    """

    pages_by_url = {
      "https://quotes.toscrape.com/": page_one,
      "https://quotes.toscrape.com/page/2/": page_two,
    }

    def fake_fetch_html(url: str) -> str:
      return pages_by_url[url]

    # WHEN crawl_site visits more than one page with a delay
    with patch("crawler.fetch_html", side_effect=fake_fetch_html):
      with patch("crawler.time.sleep") as mock_sleep:
        pages = crawler.crawl_site(delay_seconds=1)

    # THEN the politeness delay is applied
    self.assertEqual(len(pages), 2)
    mock_sleep.assert_called()

if __name__ == "__main__":
  unittest.main()
