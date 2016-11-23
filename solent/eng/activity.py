class Activity:
    def __init__(self):
        self.lst = []
    def clear(self):
        self.lst = []
    def mark(self, l, s):
        '''l: location; s: string description'''
        self.lst.append("%s/%s"%(str(l), s))
    def get(self):
        return self.lst[:]

def activity_new():
    ob = Activity()
    return ob

