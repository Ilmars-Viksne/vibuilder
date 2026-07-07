class TreeBuilder:
    @staticmethod
    def build(workspace):
        items = []
        root = workspace.root
        if not root.exists():
            return "(empty workspace)"
        for p in sorted(root.rglob("*")):
            if "__pycache__" not in str(p) and ".git" not in str(p) and ".vibuilder" not in str(p):
                items.append(str(p.relative_to(root)))
        return "\n".join(items) if items else "(empty workspace)"
