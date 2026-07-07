import os

class FileSystemTools:
    @staticmethod
    def list_directory(path="agent_workspace"):
        try:
            return os.listdir(path)
        except FileNotFoundError:
            return []
