class Keystream(object):
    def __init__(self, fn_async_getc, fn_block_getc):
        self.fn_async_getc = fn_async_getc
        self.fn_block_getc = fn_block_getc
    def block_getc(self):
        return self.fn_block_getc()
    def async_getc(self):
        return self.fn_async_getc()

def keystream_new(fn_async_getc, fn_block_getc):
    ob = Keystream(
        fn_async_getc=fn_async_getc,
        fn_block_getc=fn_block_getc)
    return ob

