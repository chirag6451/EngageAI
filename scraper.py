import requests
from bs4 import BeautifulSoup
import os
import json
from datetime import datetime

class CrunchbaseScraper:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        self.output_dir = 'scraped_data'
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

    def scrape_url(self, url):
        """
        Scrape content from a given Crunchbase URL
        """
        try:
            # Make request to the URL
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()

            # Parse the HTML content
            soup = BeautifulSoup(response.text, 'html.parser')

            # Extract relevant information
            data = {
                'url': url,
                'timestamp': datetime.now().isoformat(),
                'title': soup.title.string if soup.title else '',
                'text_content': soup.get_text(separator='\n', strip=True),
                'html_content': response.text
            }

            # Generate filename based on URL
            filename = url.split('/')[-1] if url.split('/')[-1] else 'homepage'
            filename = f"{filename}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

            # Save raw HTML
            html_path = os.path.join(self.output_dir, f"{filename}.html")
            with open(html_path, 'w', encoding='utf-8') as f:
                f.write(response.text)

            # Save extracted data as JSON
            json_path = os.path.join(self.output_dir, f"{filename}.json")
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4, ensure_ascii=False)

            return {
                'success': True,
                'files': {
                    'html': html_path,
                    'json': json_path
                },
                'data': data
            }

        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    def process_url_list(self, urls):
        """
        Process a list of URLs and return results
        """
        results = []
        for url in urls:
            result = self.scrape_url(url)
            results.append({
                'url': url,
                'result': result
            })
        return results
