import os
from pathlib import Path
import shutil

class WorkspaceManager:
    def __init__(self, root="agent_workspace"):
        self.root = Path(root).resolve()
        self.root.mkdir(exist_ok=True)

    def resolve_safe(self, relative_path: str) -> Path:
        """
        Resolves a relative path safely within the workspace root.
        Prevents path traversal attacks.
        """
        # If relative_path is empty or just '.', resolve to root
        if not relative_path or relative_path == ".":
            return self.root

        candidate = (self.root / relative_path).resolve()

        # Check if candidate is inside root or is the root itself
        if candidate != self.root and self.root not in candidate.parents:
            raise ValueError(f"Path escapes workspace: {relative_path}")

        return candidate

    def create_folder(self, path):
        full_path = self.resolve_safe(path)
        full_path.mkdir(parents=True, exist_ok=True)

    def create_file(self, path, content=""):
        full_path = self.resolve_safe(path)
        full_path.parent.mkdir(parents=True, exist_ok=True)
        full_path.write_text(content, encoding="utf-8")

    def read_file(self, path):
        full_path = self.resolve_safe(path)
        return full_path.read_text(encoding="utf-8")

    def edit_file(self, path, content):
        # In this implementation, edit_file overwrites.
        # Refinement might be needed if "edit" means something else.
        full_path = self.resolve_safe(path)
        full_path.write_text(content, encoding="utf-8")

    def replace_text(self, path, search, replacement):
        full_path = self.resolve_safe(path)
        text = full_path.read_text(encoding="utf-8")
        text = text.replace(search, replacement)
        full_path.write_text(text, encoding="utf-8")

    def delete_file(self, path):
        full_path = self.resolve_safe(path)
        if full_path.is_file():
            full_path.unlink(missing_ok=True)

    def delete_folder(self, path):
        full_path = self.resolve_safe(path)
        if full_path.is_dir() and full_path != self.root:
            shutil.rmtree(full_path)
