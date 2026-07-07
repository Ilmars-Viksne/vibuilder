import logging

logger = logging.getLogger(__name__)

class Tester:
    def evaluate(self, provider, test_results):
        prompt = f"Evaluate these test results and suggest fixes if any fail:\n\n{test_results}"
        return provider.chat([{"role": "user", "content": prompt}])
