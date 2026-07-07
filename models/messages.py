from dataclasses import dataclass

@dataclass
class Message:
    role: str
    content: str

    def to_dict(self):
        return {"role": self.role, "content": self.content}
