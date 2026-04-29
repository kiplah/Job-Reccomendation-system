import scrapy

class JobItem(scrapy.Item):
    """
    A unified Scrapy Item to hold scraped job data before it is 
    passed to the pipeline and saved to the Django database.
    """
    title = scrapy.Field()
    company = scrapy.Field()
    location = scrapy.Field()
    description = scrapy.Field()
    skills_required = scrapy.Field()
    platform = scrapy.Field()
    url = scrapy.Field()
    date_posted = scrapy.Field()
