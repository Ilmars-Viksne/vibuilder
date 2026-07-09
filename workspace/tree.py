class TreeBuilder:
    SKIP_PARTS = {
        "__pycache__",
        ".git",
        ".pytest_cache",
        ".vibuilder_memory.json",
    }

    @staticmethod
    def build(workspace) -> str:
        root = workspace.root

        if not root.exists():
            return "(empty workspace)"

        items = []

        for path in sorted(root.rglob("*")):
            relative = path.relative_to(root)

            if any(part in TreeBuilder.SKIP_PARTS for part in relative.parts):
                continue

            suffix = "/" if path.is_dir() else ""
            items.append(f"{relative}{suffix}")

        return "\n".join(items) if items else "(empty workspace)"
