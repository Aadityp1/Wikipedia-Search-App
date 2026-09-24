"""
wiki_service.py
---------------
Fast and reliable Wikipedia search service.

Features:
- Fast Wikipedia search
- Uses Wikipedia's actual introduction
- Moderate description length
- Image support
- Safe network timeout
- Handles invalid responses
- No unnecessary retry loop
"""

from io import BytesIO
from urllib.parse import quote

import requests
from PIL import Image


# =========================================================
# SETTINGS
# =========================================================

SUMMARY_API = "https://en.wikipedia.org/api/rest_v1/page/summary/"
WIKI_API = "https://en.wikipedia.org/w/api.php"

HEADERS = {
    "User-Agent": "WikipediaSearchEngine/1.0"
}

# Maximum time to wait for Wikipedia
TIMEOUT = 5

# Maximum description length
# Around 2-4 normal paragraphs depending on the topic
MAX_DESCRIPTION = 2200


# =========================================================
# RESULT CLASS
# =========================================================

class WikiResult:
    """Stores the Wikipedia search result."""

    def __init__(
        self,
        title,
        summary,
        url,
        image=None
    ):
        self.title = title
        self.summary = summary
        self.url = url
        self.image = image


# =========================================================
# MAIN SEARCH FUNCTION
# =========================================================

def search_wikipedia(
    query,
    sentences=10,
    image_size=(250, 250)
):
    """
    Search Wikipedia and return a WikiResult.

    The description comes from Wikipedia's actual
    introduction instead of the complete article.
    """

    query = (query or "").strip()

    if not query:
        raise ValueError(
            "Please enter something to search."
        )

    # -----------------------------------------------------
    # Try the requested page directly
    # -----------------------------------------------------

    encoded_query = quote(
        query.replace(" ", "_"),
        safe=""
    )

    url = SUMMARY_API + encoded_query

    try:

        response = requests.get(
            url,
            headers=HEADERS,
            timeout=TIMEOUT
        )

    except requests.exceptions.Timeout:

        raise ConnectionError(
            "Wikipedia took too long to respond."
        )

    except requests.exceptions.RequestException as e:

        raise ConnectionError(
            f"Could not connect to Wikipedia: {e}"
        )

    # -----------------------------------------------------
    # Page found
    # -----------------------------------------------------

    if response.status_code == 200:

        try:

            data = response.json()

        except ValueError:

            raise ConnectionError(
                "Wikipedia returned invalid data."
            )

        title = data.get(
            "title",
            query
        )

        page_url = (
            data.get("content_urls", {})
            .get("desktop", {})
            .get("page", "")
        )

        # Get proper Wikipedia introduction
        description = get_wikipedia_intro(
            title
        )

        # Fallback to REST API extract
        if not description:

            description = data.get(
                "extract",
                ""
            )

        # Get image
        image = None

        thumbnail = data.get(
            "thumbnail"
        )

        if thumbnail:

            image_url = thumbnail.get(
                "source"
            )

            if image_url:

                image = download_image(
                    image_url,
                    image_size
                )

        return WikiResult(
            title=title,
            summary=description,
            url=page_url,
            image=image
        )

    # -----------------------------------------------------
    # Exact page not found
    # Use Wikipedia search API
    # -----------------------------------------------------

    if response.status_code == 404:

        return search_using_api(
            query,
            image_size
        )

    # -----------------------------------------------------
    # Other HTTP errors
    # -----------------------------------------------------

    raise ConnectionError(
        f"Wikipedia returned HTTP "
        f"{response.status_code}."
    )


# =========================================================
# WIKIPEDIA SEARCH API
# =========================================================

def search_using_api(
    query,
    image_size=(250, 250)
):
    """
    Search Wikipedia when the exact page isn't found.
    """

    params = {
        "action": "query",
        "list": "search",
        "srsearch": query,
        "format": "json",
        "utf8": 1,
        "srlimit": 1
    }

    try:

        response = requests.get(
            WIKI_API,
            params=params,
            headers=HEADERS,
            timeout=TIMEOUT
        )

    except requests.exceptions.Timeout:

        raise ConnectionError(
            "Wikipedia search timed out."
        )

    except requests.exceptions.RequestException as e:

        raise ConnectionError(
            f"Wikipedia connection failed: {e}"
        )

    if response.status_code != 200:

        raise ConnectionError(
            f"Wikipedia returned HTTP "
            f"{response.status_code}."
        )

    try:

        data = response.json()

    except ValueError:

        raise ConnectionError(
            "Wikipedia returned invalid JSON."
        )

    results = (
        data.get("query", {})
        .get("search", [])
    )

    if not results:

        raise ValueError(
            "No Wikipedia results found."
        )

    title = results[0].get(
        "title"
    )

    if not title:

        raise ValueError(
            "Wikipedia did not return a valid result."
        )

    # -----------------------------------------------------
    # Get page information
    # -----------------------------------------------------

    encoded_title = quote(
        title.replace(" ", "_"),
        safe=""
    )

    page_url = SUMMARY_API + encoded_title

    try:

        page_response = requests.get(
            page_url,
            headers=HEADERS,
            timeout=TIMEOUT
        )

    except requests.exceptions.Timeout:

        raise ConnectionError(
            "Wikipedia page request timed out."
        )

    except requests.exceptions.RequestException:

        raise ConnectionError(
            "Could not load the Wikipedia page."
        )

    if page_response.status_code != 200:

        raise ConnectionError(
            "Could not load the selected Wikipedia page."
        )

    try:

        page_data = page_response.json()

    except ValueError:

        raise ConnectionError(
            "Wikipedia returned invalid page data."
        )

    page_title = page_data.get(
        "title",
        title
    )

    final_url = (
        page_data.get("content_urls", {})
        .get("desktop", {})
        .get("page", "")
    )

    # -----------------------------------------------------
    # Get actual Wikipedia introduction
    # -----------------------------------------------------

    description = get_wikipedia_intro(
        page_title
    )

    # Fallback
    if not description:

        description = page_data.get(
            "extract",
            ""
        )

    # -----------------------------------------------------
    # Get image
    # -----------------------------------------------------

    image = None

    thumbnail = page_data.get(
        "thumbnail"
    )

    if thumbnail:

        image_url = thumbnail.get(
            "source"
        )

        if image_url:

            image = download_image(
                image_url,
                image_size
            )

    if not description:

        raise ValueError(
            "No information was found."
        )

    return WikiResult(
        title=page_title,
        summary=description,
        url=final_url,
        image=image
    )


# =========================================================
# GET WIKIPEDIA INTRODUCTION
# =========================================================

def get_wikipedia_intro(title):
    """
    Get only the introduction of the Wikipedia article.

    This does NOT fetch the complete article.
    """

    params = {
        "action": "query",
        "prop": "extracts",

        # Plain text instead of HTML
        "explaintext": 1,

        # IMPORTANT:
        # Only the introduction is requested
        "exintro": 1,

        "titles": title,

        "format": "json",

        "formatversion": 2
    }

    try:

        response = requests.get(
            WIKI_API,
            params=params,
            headers=HEADERS,
            timeout=TIMEOUT
        )

    except requests.exceptions.Timeout:

        return None

    except requests.exceptions.RequestException:

        return None

    if response.status_code != 200:

        return None

    try:

        data = response.json()

    except ValueError:

        return None

    pages = (
        data.get("query", {})
        .get("pages", [])
    )

    if not pages:

        return None

    extract = pages[0].get(
        "extract",
        ""
    )

    if not extract:

        return None

    # -----------------------------------------------------
    # Limit description length
    # -----------------------------------------------------

    if len(extract) > MAX_DESCRIPTION:

        extract = extract[
            :MAX_DESCRIPTION
        ]

        # Don't cut a word in half
        last_space = extract.rfind(
            " "
        )

        if last_space > 0:

            extract = extract[
                :last_space
            ]

        extract += "..."

    return extract.strip()


# =========================================================
# DOWNLOAD IMAGE
# =========================================================

def download_image(
    image_url,
    size=(250, 250)
):
    """
    Download and resize Wikipedia thumbnail.

    If image download fails, the text result
    will still be returned.
    """

    try:

        response = requests.get(
            image_url,
            headers=HEADERS,
            timeout=3
        )

        if response.status_code != 200:

            return None

        image = Image.open(
            BytesIO(response.content)
        )

        image.load()

        return image.resize(
            size
        )

    except Exception:

        return None