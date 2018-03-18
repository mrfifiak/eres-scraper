from observer import Subscriber
import email


class Mailer(Subscriber):
    def __init__(self, name, from_address, to_address, password):
        super().__init__(name)
        self.password = password
        self.from_address = from_address
        self.to_address = to_address
        self.body = None
        self.subject = None

    def update(self, payload):