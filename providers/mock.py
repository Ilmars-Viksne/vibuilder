import json
from providers.base import BaseProvider, ProviderRegistry

@ProviderRegistry.register("mock")
class MockProvider(BaseProvider):
    def __init__(self, model="mock-model", **kwargs):
        self.model = model
        self.step = 0

    def chat(self, messages, temperature=0.2):
        self.step += 1
        # Simulate a basic agent workflow
        if self.step == 1:
            # Planner
            return json.dumps(["1. Create main.py", "2. Run tests"])
        elif self.step == 2:
            # Architect
            return "Simple single-file architecture"
        elif self.step == 3:
            # Coder Step 1
            return json.dumps({"action": "create_file", "path": "test.py", "content": "print('Mock working')"})
        elif self.step == 4:
            # Coder Step 2
            return json.dumps({"action": "finish"})
        elif self.step == 5:
            # Tester
            return "Tests passed"
        else:
            # Reviewer
            return "Project looks good"
