from solent import run_tests
from solent import test

from solent.base import pool_rail_class

class RailTest:
    def __init__(self):
        pass
    def zero(self, zero_h, a, b):
        self.zero_h = zero_h
        self.a = a
        self.b = b
    def to_string(self):
        return "|".join([self.zero_h, self.a, self.b])

@test
def should_test_create_rail_pool():
    pool_test = pool_rail_class(RailTest)
    #
    assert 0 == pool_test.size()
    assert 0 == pool_test.out()
    #
    rail_test_00 = pool_test.get(
        zero_h='00 zero_h value',
        a='00 a value',
        b='00 b value')
    rail_test_01 = pool_test.get(
        zero_h='01 zero_h value',
        a='01 a value',
        b='01 b value')
    #
    assert 0 == pool_test.size()
    assert 2 == pool_test.out()
    #
    pool_test.put(rail_test_01)
    pool_test.put(rail_test_00)
    #
    assert 2 == pool_test.size()
    assert 0 == pool_test.out()
    #
    rail_test_02 = pool_test.get(
        zero_h='02 zero_h',
        a='a',
        b='b')
    #
    assert 1 == pool_test.size()
    assert 1 == pool_test.out()
    #
    pool_test.put(rail_test_02)
    #
    assert 2 == pool_test.size()
    assert 0 == pool_test.out()
    #
    return True

if __name__ == '__main__':
    run_tests()

