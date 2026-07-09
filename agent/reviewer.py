import logging

logger = logging.getLogger(__name__)

class Reviewer:
    def review(self, provider, history):
        prompt = (
            "Review the following agent action history and provide a final assessment of the work completed:\n\n"
            f"{history}\n\n"
            "Assess whether the original goal was achieved and if the quality of the code is acceptable."
        )
        return provider.chat([{"role": "user", "content": prompt}])
