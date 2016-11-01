#
# experimental. possibly wacky. not yet completely given up on the idea.
#

class DictPool(object):
    def __init__(self, solent_type, keys, initial_allocation):
        self.solent_type = solent_type
        self.keys = keys
        #
        self.store = []
        for i in range(initial_allocation):
            self._create()
    def _create(self):
        d = {}
        for k in keys:
            d[k] = None
        d['__solent_type__'] = self.solent_type
        self.store.append(d)
    def get(self):
        if not self.store:
            self._create()
        ob = self.store.pop()
        return ob
    def put(self, d):
        self.store.append(d)

def dict_pool_new(solent_type, keys, initial_allocation):
    '''
    solent_type: an arbitrary string that should clearly identify the purpose
    of each dictionary.
    keys: a set or list of field names.
    '''
    ob = DictPool(
        solent_type=solent_type,
        keys=keys,
        initial_allocation=initial_allocation)
    return ob

