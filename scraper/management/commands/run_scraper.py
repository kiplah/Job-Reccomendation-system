import os
from django.core.management.base import BaseCommand
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

class Command(BaseCommand):
    help = 'Runs the Scrapy spiders to fetch job listings into the database.'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS("Starting job scraper..."))
        
        # Point Scrapy to our custom settings file
        os.environ.setdefault("SCRAPY_SETTINGS_MODULE", "scraper.scrapy_settings")
        
        # Initialize CrawlerProcess with those settings
        process = CrawlerProcess(get_project_settings())
        
        # Run the 'indeed' spider
        process.crawl('indeed')
        
        # This blocks the process until the spider finishes
        process.start()
        
        self.stdout.write(self.style.SUCCESS("Scraping completed!"))
