import scrapy
import json
from bs4 import BeautifulSoup
from scraper.items import JobItem

class JobicySpider(scrapy.Spider):
    name = 'jobicy'
    allowed_domains = ['jobicy.com']
    start_urls = ['https://jobicy.com/api/v2/remote-jobs']
    
    custom_settings = {
        'DEFAULT_REQUEST_HEADERS': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'application/json',
        }
    }

    def parse(self, response):
        try:
            data = json.loads(response.text)
        except json.JSONDecodeError:
            self.logger.error("Failed to decode JSON from Jobicy API")
            return

        # Jobs are nested inside the "jobs" array
        jobs = data.get('jobs', [])

        for job in jobs:
            item = JobItem()
            item['title'] = job.get('jobTitle')
            item['company'] = job.get('companyName')
            item['location'] = "Remote"
            
            # Use BeautifulSoup to cleanly strip HTML tags out of the description
            raw_html = job.get('jobDescription', '')
            if raw_html:
                soup = BeautifulSoup(raw_html, "html.parser")
                item['description'] = soup.get_text(separator=' ', strip=True)
            else:
                item['description'] = ""
                
            # Extract tags array and join into a comma-separated string
            tags = job.get('tags', [])
            item['skills_required'] = ", ".join(tags) if isinstance(tags, list) else str(tags)
            
            item['platform'] = "Jobicy"
            item['url'] = job.get('url')
            
            # Handle pubDate which usually arrives as "YYYY-MM-DD HH:MM:SS"
            pub_date = job.get('pubDate', '')
            if pub_date and len(pub_date) >= 10:
                # Slicing the first 10 characters perfectly extracts the YYYY-MM-DD string 
                # that Django's DateField expects natively!
                item['date_posted'] = pub_date[:10]
            else:
                item['date_posted'] = None
                
            yield item
