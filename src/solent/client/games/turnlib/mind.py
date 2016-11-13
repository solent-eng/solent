import types

def mind_interface(cb_add_key, cb_ready, cb_blocking_memo, cb_turn):
    ob = types.ModuleType('mind')
    ob.add_key = cb_add_key
    ob.ready = cb_ready
    ob.blocking_memo = cb_blocking_memo
    ob.turn = cb_turn
    return ob

