import scrapy
from scraper.items import JobItem
import urllib.parse

class IndeedSpider(scrapy.Spider):
    name = 'indeed'
    allowed_domains = ['ke.indeed.com', 'indeed.com']
    
    # Enforce the 2-second download delay
    custom_settings = {
        'DOWNLOAD_DELAY': 2,
    }

    # Generate start URLs for different search terms
    search_terms = ['software engineer', 'data analyst', 'python developer']
    start_urls = [
        f'https://ke.indeed.com/jobs?q={urllib.parse.quote(term)}'
        for term in search_terms
    ]

    def parse(self, response):
        """
        Parses the search results page to extract job cards and follow pagination.
        """
        # Select all job cards on the page
        job_cards = response.css('div.job_seen_beacon, td.resultContent')
        
        for card in job_cards:
            # Extract basic info from the search results
            title = card.css('h2.jobTitle span::text, h2.jobTitle a::text').get()
            company = card.css('span.companyName::text, span[data-testid="company-name"]::text').get()
            location = card.css('div.companyLocation::text, div[data-testid="text-location"]::text').get()
            
            # Extract relative URL and build absolute URL
            relative_url = card.css('h2.jobTitle a::attr(href)').get()
            
            if relative_url:
                job_url = response.urljoin(relative_url)
                
                # Follow the job detail link to extract the full description
                yield scrapy.Request(
                    url=job_url,
                    callback=self.parse_job_detail,
                    meta={
                        'title': title.strip() if title else None,
                        'company': company.strip() if company else None,
                        'location': location.strip() if location else None,
                        'url': job_url
                    }
                )

        # Handle Pagination (Next page button)
        next_page = response.css('a[data-testid="pagination-page-next"]::attr(href), a[aria-label="Next Page"]::attr(href)').get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)


    def parse_job_detail(self, response):
        """
        Parses the specific job posting page.
        """
        meta = response.meta
        
        item = JobItem()
        item['title'] = meta.get('title')
        item['company'] = meta.get('company')
        item['location'] = meta.get('location')
        item['url'] = meta.get('url')
        item['platform'] = "Indeed"
        
        # Extract full description
        description_parts = response.css('div#jobDescriptionText *::text').getall()
        item['description'] = " ".join([p.strip() for p in description_parts if p.strip()])
        
        # Extract date posted
        # Note: Indeed's dates are usually strings like "Posted 3 days ago". 
        # A pipeline should ideally parse this into a standard format.
        date_text = response.css('span.css-19j1a75::text, div.jobsearch-JobMetadataFooter::text').get()
        item['date_posted'] = date_text.strip() if date_text else None
        
        # Leave skills blank; our NLP processor will extract these from the description later
        item['skills_required'] = ""
        
        yield item
