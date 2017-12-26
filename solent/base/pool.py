from .small import ns

import inspect

def pool_rail_class(rail_class):
    # This is effectively metaprogramming, in order to create an instance of
    # an object pool.
    #
    # Validate that rail_class has the handles we expect
    oclass_methods = dir(rail_class)
    if 'zero' not in oclass_methods:
        raise Exception("Class {%s} needs method zero(..)"%(
            rail_class.__name__))
    #
    class RailPool:
        def __init__(self):
            self.stack = []
            self.count_out = 0
        def get(self, **args):
            if not self.stack:
                self.stack.append(rail_class())
            ob = self.stack.pop()
            ob.zero(**args)
            self.count_out += 1
            return ob
        def put(self, thing):
            self.stack.append(thing)
            self.count_out -= 1
        def size(self):
            return len(self.stack)
        def out(self):
            return self.count_out
    # Now we create a namespace, and attach the methods above to it.
    rail_pool = RailPool()
    #
    return rail_pool

