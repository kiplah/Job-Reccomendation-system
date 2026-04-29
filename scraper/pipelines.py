import logging
from scrapy.exceptions import DropItem
from asgiref.sync import sync_to_async

# We must import the model AFTER django.setup() is called in settings or management command.
from jobs.models import JobListing

logger = logging.getLogger(__name__)

class DjangoSavePipeline:
    """
    Saves JobItem data directly to the Django database using the ORM.
    """
    async def process_item(self, item):
        # 1. Skip items with missing title or url
        if not item.get('title') or not item.get('url'):
            logger.warning("Dropping item due to missing title or url.")
            raise DropItem("Missing title or url")
        
        defaults = {
            'title': item.get('title'),
            'company': item.get('company') or '',
            'location': item.get('location') or '',
            'description': item.get('description') or '',
            'skills_required': item.get('skills_required') or '',
            'platform': item.get('platform') or '',
            'date_posted': item.get('date_posted')
        }
        
        # 2. Django 5+ enforces strict thread safety. Since Scrapy uses the asyncio reactor,
        # we MUST wrap our database hits in sync_to_async!
        @sync_to_async
        def save_job():
            return JobListing.objects.update_or_create(
                url=item.get('url'),
                defaults=defaults
            )

        job, created = await save_job()

        # 3. Log a message
        action = "Created new" if created else "Updated existing"
        logger.info(f"{action} job: '{job.title}' at {job.company}")

        return item
