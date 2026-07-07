import logging

logger = logging.getLogger(__name__)

class Architect:
    def design(self, provider, goal):
        prompt = f"Design the system architecture for the following goal:\n\n{goal}\n\nDescribe the components, file structure, and data flow."
        return provider.chat([{"role": "user", "content": prompt}])
