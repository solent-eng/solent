import time

class Clock:
    def __init__(self):
        pass
    def now(self):
        return time.time()

def clock_new():
    ob = Clock()
    return ob

