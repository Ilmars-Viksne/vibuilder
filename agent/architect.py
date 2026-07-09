import logging

logger = logging.getLogger(__name__)


class Architect:
    def design(self, provider, goal: str) -> str:
        prompt = (
            "Design the system architecture for the following goal:\n\n"
            f"{goal}\n\n"
            "Describe the components, file structure, and data flow. "
            "Be specific about file names and their responsibilities."
        )

        response = provider.chat(
            [
                {
                    "role": "system",
                    "content": "You are a senior software architect.",
                },
                {
                    "role": "user",
                    "content": prompt,
                },
            ]
        )

        logger.info("Architecture design produced")
        return response.strip()
