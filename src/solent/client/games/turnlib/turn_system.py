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

class TurnSystem(object):
    def __init__(self):
        #
        # List of meeps, maintained in a deliberate order. The ordering of
        # this list is the heart of the time mechanism.
        self.prio = []
    def add_meep(self, meep):
        '''
        Find or create the fatigue run that matches the meep's fatigue. If
        there are other meeps already on the rung, the insertion meep gets
        last spot on the rung.
        '''
        b_placed = False
        for idx in range(len(self.prio)):
            if self.prio[idx].fatigue > meep.fatigue:
                self.prio.insert(idx, meep)
                b_placed = True
                break
        if not b_placed:
            self.prio.append(meep)
    def dispatch_next_tick(self):
        '''finds the next tick that it to be dispatched, and then activates
        all the meeps who are to have their turn.
        '''
        if not self.prio:
            return
        backup_prio = self.prio[:]
        #
        # Synchronise time so that the first item in the list is at 0 fatigue.
        self._normalise_time_to_first_meep_action()
        #
        # Find all of the meeps who have zero fatigue. It's going to be their
        # turn. So we move them from our prio list into a team list. (The
        # mechanism by which we are doing this at the moment is probably
        # super-inefficient. See comments at top.)
        team = []
        while self.prio and self.prio[0].fatigue == 0:
            team.append(self.prio[0])
            del self.prio[0]
        #
        # Grant turns for the selected meeps
        for meep in team:
            if meep.has_died:
                continue
            mind = meep.mind
            if None == mind:
                continue
            mind.turn(meep)
            meep.fatigue += meep.overhead
        #
        # Reduce fatigue for the meeps that are still in the queue. i.e.
        # The meeps who just had a turn do not benefit from this.
        for itm in self.prio:
            itm.fatigue -= 1
        #
        # Now we put our team meeps back in the queue. (They are demoted
        # to the bottom of their fatigue rung. This avoids a starvation
        # scenario)
        for meep in team:
            if meep.has_died:
                continue
            self.add_meep(
                meep=meep)
    def _normalise_time_to_first_meep_action(self):
        '''We need the meep at the front of the priority list to have a fatigue
        of 0. Hence, we want adjust all the meeps in the queue by the fatigue
        of that first meep. Effectively, we are shift time to the point at
        which the meep would have 0 fatigue.'''
        fatigue = self.prio[0].fatigue
        if 0 == fatigue:
            return
        for meep in self.prio:
            meep.fatigue -= fatigue
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

def turn_system_new():
    ob = TurnSystem()
    return ob


# --------------------------------------------------------
#   :testing
# --------------------------------------------------------
def test():
    import types
    def coords(s, e):
        ob = types.ModuleType('coords')
        ob.s = s
        ob.e = e
        return ob
    class FakeMind(object):
        def __init__(self):
            pass
        def turn(self, meep):
            print('turn: %s (%s)'%(meep.c, meep.overhead))
    mind = FakeMind()
    ts = turn_system_new()
    ts.add_meep(
        meep=meep_new(
            mind=mind,
            coords=coords(
                s=0,
                e=0),
            c='a',
            overhead=5))
    ts.add_meep(
        meep=meep_new(
            mind=mind,
            coords=coords(
                s=0,
                e=0),
            c='b',
            overhead=8))
    ts.add_meep(
        meep=meep_new(
            mind=mind,
            coords=coords(
                s=0,
                e=0),
            c='c',
            overhead=10))
    ts.add_meep(
        meep=meep_new(
            mind=mind,
            coords=coords(
                s=0,
                e=0),
            c='d',
            overhead=7))
    ts.add_meep(
        meep=meep_new(
            mind=mind,
            coords=coords(
                s=0,
                e=0),
            c='e',
            overhead=9))
    ts.add_meep(
        meep=meep_new(
            mind=mind,
            coords=coords(
                s=0,
                e=0),
            c='f',
            overhead=12))
    ts.add_meep(
        meep=meep_new(
            mind=mind,
            coords=coords(
                s=0,
                e=0),
            c='g',
            overhead=2))
    def pause():
        print('[paused]', end='')
        input()
    def step():
        ts.dispatch_next_tick()
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


