import os
from django.core.management.base import BaseCommand
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from twisted.internet import defer

class Command(BaseCommand):
    help = 'Runs the Scrapy spiders sequentially to fetch job listings.'

    def add_arguments(self, parser):
        # Optional --spider argument
        parser.add_argument(
            '--spider', 
            type=str, 
            help='Run a specific spider (e.g., remoteok, jobicy)'
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS("Initializing scraper..."))
        
        os.environ.setdefault("SCRAPY_SETTINGS_MODULE", "scraper.scrapy_settings")
        process = CrawlerProcess(get_project_settings())
        
        target_spider = options.get('spider')
        available_spiders = ['remoteok', 'jobicy']
        
        # Determine which spiders to run
        if target_spider:
            if target_spider not in available_spiders:
                self.stdout.write(self.style.ERROR(
                    f"Spider '{target_spider}' not found. Available: {', '.join(available_spiders)}"
                ))
                return
            spiders_to_run = [target_spider]
        else:
            spiders_to_run = available_spiders

        # Define an inline callback to yield the execution of spiders sequentially
        @defer.inlineCallbacks
        def run_sequentially():
            for spider_name in spiders_to_run:
                self.stdout.write(self.style.WARNING(f"\n--- Starting spider: {spider_name} ---"))
                
                # We manually create the crawler so we can access its stats later
                crawler = process.create_crawler(spider_name)
                
                # Yield pauses execution of the next loop iteration until this spider finishes
                yield process.crawl(crawler)
                
                # Extract the number of items successfully scraped
                scraped_count = crawler.stats.get_value('item_scraped_count', 0)
                self.stdout.write(self.style.SUCCESS(
                    f"--> Finished '{spider_name}'! Total jobs scraped: {scraped_count}"
                ))
                
        # Fire the callback sequence
        run_sequentially()
        
        # Start the Twisted reactor (blocks until the sequence finishes)
        process.start()
        
        self.stdout.write(self.style.SUCCESS("\nAll scraping processes completed!"))
