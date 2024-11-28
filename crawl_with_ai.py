import asyncio
from crawl4ai import AsyncWebCrawler

async def fetch_url_content(url):
    """
    Fetches the content of a given URL using AsyncWebCrawler.

    :param url: The URL to fetch content from.
    :return: The complete HTML content of the page.
    """
    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun(url=url)
        return result.markdown  # Returns the complete HTML

# Example usage with URL passed as a parameter
def fetch_from_url(url):
    """
    Wrapper function to run the async fetch_url_content function.

    :param url: The URL to fetch content from.
    :return: The HTML content fetched from the URL.
    """
    return asyncio.run(fetch_url_content(url))

# Call the function
# if __name__ == "__main__":
#     url = "https://indiankanoon.org/doc/210/"
#     html_content = fetch_from_url(url)
#     print(html_content)  # Prints the complete HTML content
