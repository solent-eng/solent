#
# menu: stores a unique trigger character against some text and a callback.
#

from collections import OrderedDict as od

class Menu(object):
    def __init__(self):
        # c vs (text, fn_callback)
        self.d = od()
    def add(self, key, text, fn_callback):
        if key in self.d:
            raise Exception("Can't add duplicate key. [%s]"%(c))
        if 1 != len(key):
            raise Exception("Key must be a single char [%s] "%(c))
        self.d[key] = (text, fn_callback)
    def get_keys(self):
        return self.d.keys()
    def get_desc(self, key):
        return self.d[key][0]
    def get_callback(self, key):
        return self.d[key][1]
    def get_lines(self):
        sb = []
        for k, v in self.d.items():
            (text, fn_callback) = v
            sb.append('[%s] %s'%(k, text))
        return '\n'.join(sb)

def menu_new():
    ob = Menu()
    return ob

