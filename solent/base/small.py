import types

UNIQ = 0
def uniq():
    global UNIQ
    UNIQ += 1
    return UNIQ

def Ns():
    ob = types.ModuleType(str(uniq()))
    return ob

class SolentQuitException(Exception):
    pass

