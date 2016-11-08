class Cursor(object):
    def __init__(self, fn_s, fn_e, fn_c, fn_cpair):
        self.fn_s = fn_s
        self.fn_e = fn_e
        self.fn_c = fn_c
        self.fn_cpair = fn_cpair
    def get_s(self):
        return self.fn_s()
    def get_e(self):
        return self.fn_e()
    def get_c(self):
        return self.fn_c()
    def get_cpair(self):
        return self.fn_cpair()

def cursor_new(fn_s, fn_e, fn_c, fn_cpair):
    ob = Cursor(
        fn_s=fn_s,
        fn_e=fn_e,
        fn_c=fn_c,
        fn_cpair=fn_cpair)
    return ob

