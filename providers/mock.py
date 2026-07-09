import json

from providers.base import BaseProvider, ProviderRegistry


@ProviderRegistry.register("mock")
class MockProvider(BaseProvider):
    def __init__(self, model: str = "mock-model", **kwargs):
        super().__init__(model=model)
        self.step = 0

    def chat(
        self,
        messages: list[dict[str, str]],
        temperature: float = 0.2,
    ) -> str:
        content = messages[-1]["content"]

        if "Create a step-by-step project plan" in content:
            return json.dumps(
                [
                    "Create a simple Python module",
                    "Create tests for the module",
                    "Run tests",
                    "Finish",
                ]
            )

        if "Design the system architecture" in content:
            return (
                "Files:\n"
                "- hello.py: contains greeting function\n"
                "- test_hello.py: verifies greeting output\n"
                "Data flow: tests import hello.greet and assert output."
            )

        if "Review the following agent action history" in content:
            return "Mock review: task completed successfully."

        if "Evaluate these test results" in content:
            return "Mock tester: tests were evaluated."

        actions = [
            {
                "action": "create_file",
                "path": "hello.py",
                "content": "def greet(name: str) -> str:\n    return f'Hello, {name}!'\n",
            },
            {
                "action": "create_file",
                "path": "test_hello.py",
                "content": (
                    "from hello import greet\n\n"
                    "def test_greet():\n"
                    "    assert greet('Vibuilder') == 'Hello, Vibuilder!'\n"
                ),
            },
            {"action": "run_tests"},
            {"action": "finish"},
        ]

        action = actions[min(self.step, len(actions) - 1)]
        self.step += 1
        return json.dumps(action)
