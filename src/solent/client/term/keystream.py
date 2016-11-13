import types

def keystream_new(cb_async_getc, cb_block_getc):
    ob = types.ModuleType('keystream')
    ob.async_getc = cb_async_getc
    ob.block_getc = cb_block_getc
    return ob

