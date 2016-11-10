class Keystream(object):
    def __init__(self, fn_getc):
        self.fn_getc = fn_getc
    def getc(self):
        return self.fn_getc()

def keystream_new(fn_getc):
    ob = Keystream(
        fn_getc=fn_getc)
    return ob

