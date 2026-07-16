from pathlib import Path
import shutil


class WorkspaceManager:
    def __init__(self, root: str | Path = "agent_workspace") -> None:
        root_path = Path(root).expanduser()

        try:
            self.root = root_path.resolve()
            self.root.mkdir(parents=True, exist_ok=True)
        except OSError as exc:
            raise ValueError(
                f"Unable to create or access workspace "
                f"{root_path!s}: {exc}"
            ) from exc

        if not self.root.is_dir():
            raise ValueError(
                f"Workspace path is not a directory: {self.root}"
            )

    def resolve(self, path: str | Path) -> Path:
        raw_path = Path(path)

        if raw_path.is_absolute():
            raise ValueError(f"Absolute paths are not allowed: {path}")

        resolved = (self.root / raw_path).resolve()

        try:
            resolved.relative_to(self.root)
        except ValueError as exc:
            raise ValueError(
                f"Path escapes workspace: {path}"
            ) from exc

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
        resolved = self.resolve(path)

        if not resolved.exists():
            raise FileNotFoundError(
                f"File not found: {resolved}"
            )

        if not resolved.is_file():
            raise ValueError(
                f"Path is not a file: {resolved}"
            )

        return resolved.read_text(encoding="utf-8")

    def list_directory(self, path: str | Path = ".") -> list[dict[str, str]]:
        resolved = self.resolve(path)

        if not resolved.exists():
            raise FileNotFoundError(
                f"Directory not found: {resolved}"
            )

        if not resolved.is_dir():
            raise ValueError(
                f"Path is not a directory: {resolved}"
            )

        children = sorted(
            resolved.iterdir(),
            key=lambda item: (
                not item.is_dir(),
                item.name.lower(),
            ),
        )

        entries: list[dict[str, str]] = []
        for child in children:
            entries.append(
                {
                    "name": child.name,
                    "type": "directory" if child.is_dir() else "file",
                }
            )

        return entries

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
