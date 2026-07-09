from pathlib import Path
import shutil


class WorkspaceManager:
    def __init__(self, root: str | Path = "agent_workspace"):
        self.root = Path(root).resolve()
        self.root.mkdir(parents=True, exist_ok=True)

    def resolve(self, path: str | Path) -> Path:
        raw_path = Path(path)

        if raw_path.is_absolute():
            raise ValueError(f"Absolute paths are not allowed: {path}")

        resolved = (self.root / raw_path).resolve()

        if resolved != self.root and self.root not in resolved.parents:
            raise ValueError(f"Path escapes workspace: {path}")

        return resolved

    def create_folder(self, path: str | Path) -> Path:
        folder = self.resolve(path)
        folder.mkdir(parents=True, exist_ok=True)
        return folder

    def write_file(self, path: str | Path, content: str) -> Path:
        file_path = self.resolve(path)
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text(content, encoding="utf-8")
        return file_path

    def read_file(self, path: str | Path) -> str:
        file_path = self.resolve(path)
        return file_path.read_text(encoding="utf-8")

    def replace_text(self, path: str | Path, search: str, replace: str) -> Path:
        file_path = self.resolve(path)
        content = file_path.read_text(encoding="utf-8")

        if search not in content:
            raise ValueError(f"Search text not found in file: {path}")

        content = content.replace(search, replace)
        file_path.write_text(content, encoding="utf-8")
        return file_path

    def delete(self, path: str | Path) -> None:
        target = self.resolve(path)

        if target.is_dir():
            shutil.rmtree(target)
        elif target.exists():
            target.unlink()

    def exists(self, path: str | Path) -> bool:
        return self.resolve(path).exists()
