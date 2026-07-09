import logging

logger = logging.getLogger(__name__)


class Tester:
    def evaluate(self, provider, test_results) -> str:
        prompt = (
            "Evaluate these test results and suggest fixes if any fail:\n\n"
            f"{test_results}\n\n"
            "If all tests passed, provide a summary of what was verified."
        )

        return provider.chat([{"role": "user", "content": prompt}])
