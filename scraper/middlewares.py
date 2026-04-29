import random
from scrapy.utils.project import get_project_settings

class RandomUserAgentMiddleware:
    """
    Middleware to rotate User-Agents dynamically for each request.
    """
    def __init__(self):
        settings = get_project_settings()
        self.user_agents = settings.getlist('USER_AGENTS')

    def process_request(self, request):
        if self.user_agents:
            request.headers.setdefault(b'User-Agent', random.choice(self.user_agents).encode('utf-8'))
