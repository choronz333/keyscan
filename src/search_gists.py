import re
import time
import urllib.parse
import requests
from typing import Generator, List, Sequence, Set, Tuple, cast

from bs4 import BeautifulSoup, Tag


GIST_SEARCH_BASE_URL = "https://gist.github.com/search"


def build_search_url(keyword: str, page_number: int, file_type: str) -> str:
    return f"{GIST_SEARCH_BASE_URL}?l={file_type}&q={urllib.parse.quote(keyword)}&p={page_number}"


def get_headers() -> dict:
    return {
        "User-Agent": (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36"
        ),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
    }


def fetch_search_html(
    keyword: str,
    page_number: int,
    file_type: str,
    session: requests.Session,
    timeout_seconds: int = 20,
) -> str:
    url = build_search_url(keyword, page_number, file_type)
    response = session.get(url, headers=get_headers(), timeout=timeout_seconds)
    response.raise_for_status()
    return response.text


def get_gist_ids_from_html(html_text: str) -> List[str]:
    """
    Parse gist IDs from a GitHub Gist search HTML page.
    Searches for <a> tags with links to the gist page.
    The link will match the pattern /{username}/{gist_id}.
    """

    beautiful_soup = BeautifulSoup(html_text, "html.parser")

    def href_check(href: str) -> bool:
        return re.compile(r"\/[^\/]+\/[0-9a-f]{20,}").search(href) != None

    a_tags: Sequence[Tag] = cast(
        Sequence[Tag],
        beautiful_soup.find_all("a", class_="Link--muted", href=href_check),
    )

    id_matcher = re.compile(r"\/[^\/]+\/([0-9a-f]{20,})", re.IGNORECASE)

    gist_ids: Set[str] = set()
    for a in a_tags:
        href: str = cast(str, a.get("href"))
        match = id_matcher.search(href)
        if match:
            gist_ids.add(match.group(1))

    return list(gist_ids)


def check_page_no_results(html_text: str) -> bool:
    return "We couldn\u2019t find any gists matching" in html_text


last_fetch_time = time.time() - 99999


def search_gists(
    keyword: str, file_type: str, delay_seconds: float
) -> Generator[Tuple[int, List[str]], None, None]:
    """
    Continuously iterates through search result pages yielding (page_number, List[gist_ids]).

    Stops when no results page is detected or when an HTTP error occurs.
    """

    session = requests.Session()
    global last_fetch_time
    try:
        current_page = 1
        while True:
            time_since_last_fetch = time.time() - last_fetch_time
            sleep_duration = delay_seconds - time_since_last_fetch
            if sleep_duration > 0:
                time.sleep(delay_seconds)

            html = fetch_search_html(keyword, current_page, file_type, session)
            last_fetch_time = time.time()

            if check_page_no_results(html):
                break

            gist_ids = get_gist_ids_from_html(html)
            yield current_page, gist_ids

            current_page += 1
    finally:
        session.close()
