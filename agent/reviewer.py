import logging

logger = logging.getLogger(__name__)


class Reviewer:
    def review(self, provider, history) -> str:
        prompt = (
            "Review the following agent action history and provide a final "
            "assessment of the work completed:\n\n"
            f"{history}\n\n"
            "Assess whether the original goal was achieved and whether the "
            "quality of the code is acceptable."
        )

        return provider.chat([{"role": "user", "content": prompt}])
