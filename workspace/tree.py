from pathlib import Path


class TreeBuilder:
    SKIP_PARTS = {
        "__pycache__",
        ".git",
        ".pytest_cache",
        ".vibuilder_memory.json",
    }

    @classmethod
    def build(cls, workspace) -> str:
        root = Path(workspace.root)

        if not root.exists():
            return "<workspace does not exist>"

        lines: list[str] = []

        for path in sorted(root.rglob("*")):
            try:
                relative = path.relative_to(root)
            except ValueError:
                continue

            if any(part in cls.SKIP_PARTS for part in relative.parts):
                continue

            depth = len(relative.parts) - 1
            indent = "  " * depth
            suffix = "/" if path.is_dir() else ""
            lines.append(f"{indent}{relative.name}{suffix}")

        return "\n".join(lines) if lines else "<empty>"
