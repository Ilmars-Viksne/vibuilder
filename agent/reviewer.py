import logging

logger = logging.getLogger(__name__)

class Reviewer:
    def review(self, provider, history):
        prompt = f"Review the following agent action history and provide a final assessment of the work completed:\n\n{history}"
        return provider.chat([{"role": "user", "content": prompt}])
