

class Event:
    def __init__(self, timestamp, event_type, node=None, message=None):
        self.timestamp = timestamp
        self.type = event_type
        self.node = node
        self.message = message

    def __repr__(self):
        return "event_time: {}, event_type: {}".format(self.timestamp, self.type)


class EventSimulator:
    def __init__(self):
        self.q = []

    def add_event(self, event):
        i = 0
        while i < len(self.q) and self.q[i].timestamp <= event.timestamp:
            i += 1
        self.q.insert(i, event)

    def get_next_event(self):
        if self.q:
            return self.q.pop(0)
        else:
            return None

    def remove_event(self, _type, timestamp):
        i = 0
        while i < len(self.q) and self.q[i].timestamp >= timestamp:
            if self.q[i].type == _type:
                self.q.pop(i)
            else:
                i += 1

