import json
import logging

logger = logging.getLogger(__name__)


class Tester:
    def evaluate(self, provider, test_results) -> str:
        prompt = (
            "Evaluate these test results and suggest fixes if any fail:\n\n"
            f"{json.dumps(test_results, indent=2)}\n\n"
            "If all tests passed, provide a summary of what was verified."
        )

        response = provider.chat(
            [
                {
                    "role": "system",
                    "content": "You are a software test analyst.",
                },
                {
                    "role": "user",
                    "content": prompt,
                },
            ]
        )

        logger.info("Test evaluation completed")
        return response.strip()
