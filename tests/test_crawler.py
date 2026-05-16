import sys
import unittest
from pathlib import Path
from unittest.mock import patch

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


if __name__ == "__main__":
  unittest.main()
