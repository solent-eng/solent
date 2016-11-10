#
# Scheduling mechanism that allows for different things to happen at different
# times. Everything in here orients around meeps. If you want to do things
# that involve time and which don't inherently have meeps, then create a
# hidden plane and put some meeps on it. Meeps are easy to work with,
# time_system is oriented around meeps.
#
# The mechanism below is fairly simple, but possible not to read. Each meet
# has an 'overhead'. That is - the energy hit taken by making a turn. Whenever
# a meep has a turn, it is given a fatigue value equal to its overhead. At the
# same time, all the meeps who have not just had a turn get one deducted from
# their fatigue. In this way, fast things get more turns, and slow things get
# fewer turns. (There's a bit more to it than that, the logic is arranged to
# discourage starvation, but I won't go into that here)
#
# There's a significant inefficiency in the way that the priority list works
# at the time of writing. The reason I've gone with this approach is that I
# needed to do insertion to a queue. Python doesn't support insertion to deque
# before python 3.5. And I don't want to spend energy writing a more efficient
# implementation unless there's a need for it.
#

from .meep import meep_new

class TimeSystem(object):
    def __init__(self):
        # List of meeps, maintained in a deliberate order. The ordering of
        # this list is the heart of the time mechanism.
        self.prio = []
    def register_meep(self, meep):
        self._insert(meep)
    def next(self):
        if not self.prio:
            return
        self._normalise_to_zero()
        assert (self.prio[0].fatigue == 0) # xxx
        #
        meep = self.prio[0]
        del self.prio[0] # slow! see comments at top
        if meep.has_died:
            return
        #
        # meep gets its turn
        mind = meep.mind
        if None != mind:
            mind.turn(meep)
        meep.fatigue += meep.overhead
        #
        # fatigue adjustments for all the other meeps in the queue
        for itm in self.prio:
            itm.fatigue -= 1
        #
        # now the meep gets back in the list, demoted
        if not meep.has_died:
            self._insert(meep)
    def _normalise_to_zero(self):
        '''You want to find an amount by which you can adjust the item at the
        front of the list by in order to get it to zero. You adjust the
        fatigue of all the items by that amount.'''
        fatigue = self.prio[0].fatigue
        if 0 == fatigue:
            return
        for meep in self.prio:
            meep.fatigue -= fatigue
    def _insert(self, meep):
        b_placed = False
        for idx in range(len(self.prio)):
            if self.prio[idx].fatigue > meep.fatigue:
                self.prio.insert(idx, meep)
                b_placed = True
                break
        if not b_placed:
            self.prio.append(meep)
    def __repr__(self):
        sb = []
        sb.append('  meep   fatigue')
        sb.append('  ==============')
        if not self.prio:
            sb.append('  [none]')
        for meep in self.prio:
            sb.append('  %s(%2s)  %s'%(meep.c, meep.overhead, meep.fatigue))
        sb.append('  ==============')
        sb.append('.')
        return '\n'.join(sb)

def time_system_new():
    ob = TimeSystem()
    return ob


# --------------------------------------------------------
#   :testing
# --------------------------------------------------------
def test():
    class FakeMind(object):
        def __init__(self):
            pass
        def turn(self, meep):
            print('turn: %s (%s)'%(meep.c, meep.overhead))
    mind = FakeMind()
    ts = time_system_new()
    ts.register_meep(
        meep=meep_new(
            mind=mind,
            s=0,
            e=0,
            c='a',
            cpair=None,
            rogue_plane=None,
            overhead=5))
    ts.register_meep(
        meep=meep_new(
            mind=mind,
            s=0,
            e=0,
            c='b',
            cpair=None,
            rogue_plane=None,
            overhead=8))
    ts.register_meep(
        meep=meep_new(
            mind=mind,
            s=0,
            e=0,
            c='c',
            cpair=None,
            rogue_plane=None,
            overhead=10))
    ts.register_meep(
        meep=meep_new(
            mind=mind,
            s=0,
            e=0,
            c='d',
            cpair=None,
            rogue_plane=None,
            overhead=7))
    ts.register_meep(
        meep=meep_new(
            mind=mind,
            s=0,
            e=0,
            c='e',
            cpair=None,
            rogue_plane=None,
            overhead=9))
    ts.register_meep(
        meep=meep_new(
            mind=mind,
            s=0,
            e=0,
            c='f',
            cpair=None,
            rogue_plane=None,
            overhead=12))
    ts.register_meep(
        meep=meep_new(
            mind=mind,
            s=0,
            e=0,
            c='g',
            cpair=None,
            rogue_plane=None,
            overhead=2))
    def pause():
        print('[paused]', end='')
        input()
    def step():
        ts.next()
        print(str(ts))
        pause()
    print('-- initial ---------')
    print(str(ts))
    print('--------------------')
    pause()
    for i in range(20):
        step()

if __name__ == '__main__':
    test()


