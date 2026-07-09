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

        return provider.chat([{"role": "user", "content": prompt}])
