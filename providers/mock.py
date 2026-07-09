import json

from providers.base import BaseProvider, ProviderRegistry


@ProviderRegistry.register("mock")
class MockProvider(BaseProvider):
    def __init__(self, model: str = "mock-model", **kwargs):
        super().__init__(model=model)
        self.step = 0

    def chat(self, messages: list[dict[str, str]], temperature: float = 0.2) -> str:
        prompt = messages[-1]["content"] if messages else ""

        if "Create a step-by-step project plan" in prompt:
            return json.dumps(
                [
                    "Create a simple Python script",
                    "Run the script",
                    "Finish the task",
                ]
            )

        if "Design the system architecture" in prompt:
            return (
                "Create a single file named hello.py. "
                "The script prints a greeting and can be executed with Python."
            )

        if "Review the following agent action history" in prompt:
            return "The mock run completed successfully."

        if "Evaluate these test results" in prompt:
            return "The mock test evaluation completed."

        actions = [
            {
                "action": "create_file",
                "path": "hello.py",
                "content": "print('hello from vibuilder')\n",
            },
            {
                "action": "run_python",
                "path": "hello.py",
            },
            {
                "action": "finish",
            },
        ]

        index = min(self.step, len(actions) - 1)
        self.step += 1
        return json.dumps(actions[index])
