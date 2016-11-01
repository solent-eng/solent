from collections import deque

class Entry(object):
    def __init__(self, text):
        self.text = text
        #
        self.b_new = True

class Logbook(object):
    def __init__(self, capacity):
        self.capacity = capacity
        #
        self.q = deque()
        self.t = 0
    def log(self, t, s):
        self.t = t
        self.q.append(Entry(s))
        if len(self.q) > self.capacity:
            self.q.popleft()
    def recent(self):
        out = []
        for itm in self.q:
            if itm.b_new:
                out.append(itm.text)
                itm.b_new = False
        return out

def logbook_new(capacity):
    ob = Logbook(
        capacity=capacity)
    return ob

