

class NotificationService():
    def __init__(self):
        self.handlers = []

    def add_handler(self, handler):
        self.handlers.append(handler)


    def notify(self, message):
        for handler in self.handlers:
            handler(message)