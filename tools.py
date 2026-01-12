import os, re

from crewai.tools import tool
from firecrawl import FirecrawlApp
from firecrawl.v2.types import ScrapeOptions


@tool
def web_search_tool(query: str):
    """
    Web Search Tool.
    Args:
        query: str
            The query to search the web for.
    Returns
        A list of search results with the website content in Markdown format.
    """
    app = FirecrawlApp(api_key=os.getenv("FIRECRAWL_API_KEY"))

    try:
        response = app.search(
            query=query,
            limit=5,
            scrape_options=ScrapeOptions(
                formats=["markdown"],
            ),
        )
    except Exception as e:
        return f"Error using tool: {str(e)}"

    cleaned_chunks = []

    # response is a SearchData object with web, news, images fields
    # Combine all results from web searches
    web_results = response.web or []

    for result in web_results:
        # Check if result is a Document object (has markdown) or SearchResultWeb
        if hasattr(result, "markdown"):
            # Document object
            markdown = result.markdown or ""
            title = result.metadata.title if result.metadata else ""
            url = result.metadata.url if result.metadata else ""
        elif hasattr(result, "description"):
            # SearchResultWeb object (no markdown, only description)
            title = result.title or ""
            url = result.url or ""
            markdown = result.description or ""
        else:
            # Fallback for dict
            title = result.get("title", "")
            url = result.get("url", "")
            markdown = result.get("markdown", result.get("description", ""))

        cleaned = re.sub(r"\\+|\n+", "", markdown).strip()
        cleaned = re.sub(r"\[[^\]]+\]\([^\)]+\)|https?://[^\s]+", "", cleaned)

        cleaned_result = {
            "title": title,
            "url": url,
            "markdown": cleaned,
        }

        cleaned_chunks.append(cleaned_result)

    return cleaned_chunks
