from pathlib import Path
import shutil

class WorkspaceManager:
    def __init__(self, root="agent_workspace"):
        self.root = Path(root)
        self.root.mkdir(exist_ok=True)

    def resolve(self, path):
        return self.root / path

    def create_folder(self, path):
        self.resolve(path).mkdir(parents=True, exist_ok=True)

    def create_file(self, path, content=""):
        file_path = self.resolve(path)
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text(content, encoding="utf-8")

    def read_file(self, path):
        return self.resolve(path).read_text(encoding="utf-8")

    def edit_file(self, path, content):
        self.resolve(path).write_text(content, encoding="utf-8")

    def replace_text(self, path, search, replacement):
        text = self.read_file(path)
        text = text.replace(search, replacement)
        self.edit_file(path, text)

    def delete_file(self, path):
        self.resolve(path).unlink(missing_ok=True)

    def delete_folder(self, path):
        folder = self.resolve(path)
        if folder.exists():
            shutil.rmtree(folder)
