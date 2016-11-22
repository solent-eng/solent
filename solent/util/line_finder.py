import types

class LineFinder:
    "When you get to the end of a line, callback."
    def __init__(self, cb_line):
        self.cb_line = cb_line
        #
        self.sb = []
    def clear(self):
        self.sb = []
    def accept_bytes(self, barr):
        for b in barr:
            self.accept_string(
                s=chr(b))
    def accept_string(self, s):
        if not isinstance(s, str):
            raise Exception('Wrong type supplied [%s]'%(type(s)))
        for c in s:
            if c == '\n':
                self.cb_line(''.join(self.sb))
                self.sb = []
            else:
                self.sb.append(c)

def line_finder_new(cb_line):
    ob = LineFinder(
        cb_line=cb_line)
    return ob

