import logging
from scrapy.exceptions import DropItem

# We must import the model AFTER django.setup() is called in settings or management command.
# Since this runs inside the Scrapy project, django.setup() was already fired by scrapy_settings.py
from jobs.models import JobListing

logger = logging.getLogger(__name__)

class DjangoSavePipeline:
    """
    Saves JobItem data directly to the Django database using the ORM.
    """
    def process_item(self, item, spider):
        # 1. Skip items with missing title or url
        if not item.get('title') or not item.get('url'):
            logger.warning("Dropping item due to missing title or url.")
            raise DropItem("Missing title or url")
        
        # We safely extract fields to populate defaults.
        # Note: We omit date_posted for now because raw strings like "3 days ago" 
        # will crash a Django DateField. We can add a date parser later!
        defaults = {
            'title': item.get('title'),
            'company': item.get('company') or '',
            'location': item.get('location') or '',
            'description': item.get('description') or '',
            'skills_required': item.get('skills_required') or '',
            'platform': item.get('platform') or '',
        }
        
        # 2. Use update_or_create with 'url' to avoid duplicates
        job, created = JobListing.objects.update_or_create(
            url=item.get('url'),
            defaults=defaults
        )

        # 3. Log a message
        action = "Created new" if created else "Updated existing"
        logger.info(f"{action} job: '{job.title}' at {job.company}")

        return item
