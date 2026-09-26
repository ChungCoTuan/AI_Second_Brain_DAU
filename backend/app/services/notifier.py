import asyncio

class Notifier:
    def __init__(self):
        self.queues = []

    def push_sync(self, message: str):
        """Hàm dùng cho các route đồng bộ (sync) để đẩy sự kiện"""
        for q in self.queues:
            # push without waiting
            q.put_nowait(message)

    async def get_generator(self):
        q = asyncio.Queue()
        self.queues.append(q)
        try:
            while True:
                message = await q.get()
                yield f"data: {message}\n\n"
        finally:
            if q in self.queues:
                self.queues.remove(q)

notifier = Notifier()
