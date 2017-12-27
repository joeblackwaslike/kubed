import queue
import threading


class EventHandlers:
    def __init__(self, controller):
        self._controller = controller

    def add(self, event):
        self._controller.queue.add(event)

    def update(self, event):
        self._controller.queue.add(event)

    def delete(self, event):
        self._controller.queue.add(event)


class Worker:
    pass


class Controller(threading.Thread):
    def __init__(self, client, selector, handlers=None):
        self._client = client
        self._selector = selector
        self._pods = self._client.pods.get(selector=selector).all()
        self.queue = queue.Queue()
        handlers = handlers or EventHandlers
        self.handlers = handlers(self)
