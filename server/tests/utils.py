import json
from typing import List

class MockWebSocket:
    def __init__(self):
        self.sent_messages: List[str] = []
        self.accepted = False

    async def accept(self):
        self.accepted = True

    async def send_text(self, text: str):
        self.sent_messages.append(text)

    async def receive_text(self):
        raise RuntimeError("MockWebSocket cannot receive messages.")

    def get_json(self, index=-1):
        return json.loads(self.sent_messages[index])
