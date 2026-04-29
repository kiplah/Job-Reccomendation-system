import scrapy

class IndeedSpider(scrapy.Spider):
    name = 'indeed'
    allowed_domains = ['indeed.com']
    start_urls = ['https://www.indeed.com/jobs?q=python+developer']

    def parse(self, response):
        # Parsing logic for Indeed will go here
        pass
