import json
import logging

logger = logging.getLogger(__name__)


class Reviewer:
    def review(self, provider, history) -> str:
        prompt = (
            "Review the following agent action history and provide a final "
            "assessment of the work completed:\n\n"
            f"{json.dumps(history, indent=2)}\n\n"
            "Assess whether the original goal was achieved and whether the "
            "quality of the code is acceptable."
        )

        response = provider.chat(
            [
                {
                    "role": "system",
                    "content": "You are a careful software reviewer.",
                },
                {
                    "role": "user",
                    "content": prompt,
                },
            ]
        )

        logger.info("Review completed")
        return response.strip()
