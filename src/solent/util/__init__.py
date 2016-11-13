import types

UNIQ = 0
def uniq():
    global UNIQ
    UNIQ += 1
    return UNIQ

def ns():
    ob = types.MethodType(uniq())
    return ob

