"""
app/services/extractor.py — Article content, URL metadata, and document text extraction.
"""

import re
import urllib.parse
from typing import Dict, Any, Optional
import requests
from bs4 import BeautifulSoup


HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 TruthGuardAI/1.0"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}


def sanitize_text(text: str) -> str:
    """Removes viral forwarding headers, excess blank lines, and normalizes spaces."""
    if not text:
        return ""
    
    # Strip common WhatsApp / Telegram forwarding signatures
    cleaned = re.sub(r"(?i)^forwarded\s+(as\s+received|many\s+times|from\s+another\s+chat)[:\s-]*", "", text.strip())
    cleaned = re.sub(r"(?i)please\s+forward\s+to\s+(all\s+groups|maximum\s+people|everyone)!*", "", cleaned)
    
    # Normalize whitespaces
    cleaned = re.sub(r"\r\n|\r", "\n", cleaned)
    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)
    return cleaned.strip()


def extract_domain(url: str) -> str:
    """Extract clean domain name from URL."""
    try:
        parsed = urllib.parse.urlparse(url)
        netloc = parsed.netloc.lower()
        if netloc.startswith("www."):
            netloc = netloc[4:]
        return netloc
    except Exception:
        return "unknown"


def extract_from_url(url: str, timeout: int = 10) -> Dict[str, Any]:
    """
    Fetches URL content and extracts title, author, publication date, and body text.
    Handles fallbacks gracefully without crashing.
    """
    clean_domain = extract_domain(url)
    result = {
        "title": "Article from " + clean_domain,
        "content": "",
        "author": "Editorial Staff",
        "publish_date": None,
        "domain": clean_domain,
        "source_url": url,
        "success": True,
        "error": None,
    }

    try:
        response = requests.get(url, headers=HEADERS, timeout=timeout)
        response.raise_for_status()
        html = response.text
        soup = BeautifulSoup(html, "html.parser")

        # 1. Extract Title
        if soup.title and soup.title.string:
            result["title"] = soup.title.string.strip()
        og_title = soup.find("meta", property="og:title") or soup.find("meta", attrs={"name": "twitter:title"})
        if og_title and og_title.get("content"):
            result["title"] = og_title["content"].strip()
        h1 = soup.find("h1")
        if h1 and not result["title"]:
            result["title"] = h1.get_text().strip()

        # 2. Extract Author
        author_meta = (
            soup.find("meta", attrs={"name": "author"})
            or soup.find("meta", property="article:author")
            or soup.find("span", class_=re.compile(r"author|byline", re.I))
        )
        if author_meta:
            result["author"] = author_meta.get("content") or author_meta.get_text().strip()

        # 3. Extract Publish Date
        date_meta = (
            soup.find("meta", property="article:published_time")
            or soup.find("meta", attrs={"name": "pubdate"})
            or soup.find("meta", attrs={"name": "date"})
            or soup.find("time")
        )
        if date_meta:
            result["publish_date"] = date_meta.get("content") or date_meta.get_text().strip()

        # 4. Extract Main Content
        for tag in soup(["script", "style", "nav", "footer", "header", "aside", "form"]):
            tag.decompose()

        article = soup.find("article") or soup.find("main") or soup.find("div", class_=re.compile(r"content|body|story", re.I))
        if article:
            paragraphs = [p.get_text().strip() for p in article.find_all("p") if len(p.get_text().strip()) > 25]
        else:
            paragraphs = [p.get_text().strip() for p in soup.find_all("p") if len(p.get_text().strip()) > 25]

        content = "\n\n".join(paragraphs)
        if not content:
            content = soup.get_text(separator="\n", strip=True)
            content = "\n".join([line for line in content.splitlines() if len(line) > 40])

        result["content"] = sanitize_text(content[:15000])  # limit to reasonable length

    except Exception as e:
        result["success"] = False
        result["error"] = str(e)
        # Fallback content
        result["content"] = f"Unable to fetch live webpage content ({str(e)}). Proceeding with domain and URL verification."

    return result


def extract_from_document(raw_text: str, filename: Optional[str] = None) -> Dict[str, Any]:
    """Extracts and formats text from uploaded document files."""
    cleaned = sanitize_text(raw_text)
    
    # Generate title from first line or filename
    lines = [line.strip() for line in cleaned.split("\n") if line.strip()]
    title = lines[0][:150] if lines else (filename or "Uploaded Document Analysis")
    
    return {
        "title": title,
        "content": cleaned,
        "author": "Document Author (Unverified)",
        "publish_date": None,
        "domain": "document.upload",
        "source_url": None,
        "success": True,
        "error": None,
    }
