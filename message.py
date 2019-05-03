import uuid


class Message:
    def __init__(self, msg_type, payload, public_key, signature, seed=None, prio=None):
        # TODO: Add all members of message
        self.id = uuid.uuid4() #unique ID
        self.msg_type = msg_type
        self.payload = payload
        self.public_key = public_key
        self.signature = signature
        self.seed = seed
        self.prio = prio

    def verify(self):
        return self.public_key.verify(self.signature, self.payload)
