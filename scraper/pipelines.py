from asgiref.sync import sync_to_async

class ScraperPipeline:
    def process_item(self, item, spider):
        # The logic to save the scraped item to the database using the 
        # jobs.JobListing Django model will go here.
        return item
