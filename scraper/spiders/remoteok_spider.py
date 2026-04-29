import scrapy
import json
from datetime import datetime
from scraper.items import JobItem

class RemoteOKSpider(scrapy.Spider):
    name = 'remoteok'
    allowed_domains = ['remoteok.com']
    
    def start_requests(self):
        # We explicitly set the headers to avoid 403 Forbidden errors
        url = 'https://remoteok.com/api'
        headers = {
            "User-Agent": "Mozilla/5.0",
            "Accept": "application/json"
        }
        yield scrapy.Request(url, headers=headers, callback=self.parse)

    def parse(self, response):
        try:
            data = json.loads(response.text)
        except json.JSONDecodeError:
            self.logger.error("Failed to decode JSON from RemoteOK API")
            return

        # The API's first item is a legal metadata dictionary, so we skip it.
        jobs = data[1:]

        for job in jobs:
            item = JobItem()
            
            # Note: RemoteOK API returns the job title as 'position'
            item['title'] = job.get('position')
            item['company'] = job.get('company')
            item['location'] = "Remote"
            item['description'] = job.get('description', '')
            
            # Combine the tag array into a comma-separated string for our model
            tags = job.get('tags', [])
            item['skills_required'] = ", ".join(tags) if isinstance(tags, list) else ""
            
            item['platform'] = "RemoteOK"
            item['url'] = job.get('url')
            
            # Convert the UNIX epoch timestamp into a Django-friendly Date string
            epoch = job.get('epoch')
            if epoch:
                try:
                    dt = datetime.fromtimestamp(float(epoch))
                    item['date_posted'] = dt.strftime('%Y-%m-%d')
                except (ValueError, TypeError):
                    item['date_posted'] = None
            else:
                item['date_posted'] = None
                
            yield item
