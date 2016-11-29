import time

class Clock:
    def __init__(self):
        self.t = 0
    def add(self, n):
        self.t += n
    def set(self, t):
        self.t = t
    def inc(self):
        self.t += 1
    def now(self):
        return self.t

def clock_fake():
    ob = Clock()
    return ob

