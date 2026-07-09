from pathlib import Path
import shutil


class WorkspaceManager:
    def __init__(self, root: str | Path = "agent_workspace"):
        self.root = Path(root).resolve()
        self.root.mkdir(parents=True, exist_ok=True)

    def resolve(self, relative_path: str | Path) -> Path:
        relative_path = Path(relative_path)

        if relative_path.is_absolute():
            raise ValueError("Absolute paths are not allowed")

        candidate = (self.root / relative_path).resolve()

        try:
            candidate.relative_to(self.root)
        except ValueError as exc:
            raise ValueError("Path escapes workspace") from exc

        return candidate

    def create_folder(self, path: str) -> dict:
        target = self.resolve(path)
        target.mkdir(parents=True, exist_ok=True)
        return {
            "status": "ok",
            "operation": "create_folder",
            "path": str(target.relative_to(self.root)),
        }

    def create_file(self, path: str, content: str) -> dict:
        target = self.resolve(path)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")
        return {
            "status": "ok",
            "operation": "create_file",
            "path": str(target.relative_to(self.root)),
            "bytes": len(content.encode("utf-8")),
        }

    def write_file(self, path: str, content: str) -> dict:
        target = self.resolve(path)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")
        return {
            "status": "ok",
            "operation": "write_file",
            "path": str(target.relative_to(self.root)),
            "bytes": len(content.encode("utf-8")),
        }

    def read_file(self, path: str) -> str:
        target = self.resolve(path)
        return target.read_text(encoding="utf-8")

    def replace_text(self, path: str, search: str, replace: str) -> dict:
        target = self.resolve(path)

        if not target.exists():
            raise FileNotFoundError(f"File not found: {path}")

        content = target.read_text(encoding="utf-8")

        if search not in content:
            raise ValueError(f"Search text not found in {path}")

        updated = content.replace(search, replace)
        target.write_text(updated, encoding="utf-8")

        return {
            "status": "ok",
            "operation": "replace_text",
            "path": str(target.relative_to(self.root)),
            "replacements": content.count(search),
        }

    def delete_path(self, path: str) -> dict:
        target = self.resolve(path)

        if target.is_dir():
            shutil.rmtree(target)
        elif target.exists():
            target.unlink()
        else:
            return {
                "status": "noop",
                "operation": "delete_path",
                "path": path,
                "message": "Path did not exist",
            }

        return {
            "status": "ok",
            "operation": "delete_path",
            "path": path,
        }
