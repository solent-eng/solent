= Brick

Required knowledge: Engine

Bricks are simply standard-library units that are useful for building
applications. For example, a menu.

The main qualities of a brick:
* They are intended to be general-purpose units.
* They do not directly receive initiative from the engine (they're not spins)


= Bridge

Required knowledge: Engine, Spin, Orb, Cog.

Bridge refers to a convention rather than a class name.

Only cogs can send to their orb's nearcast. This creates a bootstrapping
problem: who sends the first message that kicks off initiative on a nearcast?

There's a few ways of doing this, and the bridge approach is elegant.

We create a cog where its only responsibility is to nearcast the initial
message.

Bridges get more extensive use in unit tests, where the logic in the test
function can use them to push messages to the nearcast, and to inspect data
that has passed through the nearcast.

See the glossary entry for Orb to see an example of a bridge.


= Cog

Required knowledge: Engine, Spin, Orb

A cog is an execution unit that sits within Orb. It can send and receive
nearcast messages.

The relationship between Engine and Spin is similar to the relationship
between Orb and Cog.

Cogs are allowed to implement `at_turn` and `at_close`. But they are not
required to do this.

Unlike spins, they also get nearcast abliities, but this is contained to the
Orb that they are attached to.


= Engine

Required knowledge: None, this is a good starting point.

Solent is fundamentally an asynchronous scheduling system, and the engine
is the core of it.

If you want to create a network interaction through solent, it is best
done through calls on engine such as `engine.open_tcp_client(..)`

After setting up an engine, you will typically call `engine.event_loop()`.
After this, initiative is coordinated by the engine.

The engine's event loop runs two types of operation:

* It gives turns a class of thing called a Spin (see below).

* It runs a select loop on all of its managed sockets, and makes callbacks
  when appropriate.

Applications refer to engine-managed sockets using a concept called a 'sid'.
People with a unix background might notice similarities to the unix concept of
file descriptors.

The engine currently supports these kinds of sid:

* TCP server

* TCP accept (send/receive socket on the server end of a TCP connection)

* TCP client (A client who initiates a TCP connection to the server)

* UDP broadcast sender ("pub")

* UDP broadcast receiver ("sub")

There's no particular reason we couldn't add other mechanisms in the future.


= Interface script

Required knowledge: None

This is a simple and flexible serialisation mechanism. At the start of the
stream you need to assert the vectors you intend to send over. That way the
receiver can check that their API matches the receiver's expectations.
Having asserted the message vectors, you can then send messages on those
vectors.

Example:
```
#
# Assert the vectors
# ------------------
# The i prefix indicates that this is an interface assertion
#
# h is a general-purpose token that is short for handle. You could think of
# it as being like an id. "id" is reserved word in many languages, including
# python. "h" typically is not.

i organisation h name
i person h organistion_h name

#
# Send over the vectors
# ---------------------

organisation org/0 "huddersfield supplies"
person person/0 org/0 "john matthewman"
person person/1 org/0 "stephen stevens"

organisation org/1 "george shipping"
person person/2 org/1 "reg"
```


= Nearcast

Required knowledge: Engine, Spin, Orb

See Orb to understand how it fits into the platform.

The motivation for nearcasting is that it generates a lot less code than
point-to-point messagine. Point-to-point messaging requires the sender to know
something of the state of the receiver. This is not true of broadcast
approaches. It is easier to build and refactor applications that use this
broadcast approach.

The nearcast is an application of a technique the 'gang of four' have
described as /The Observer Pattern/.

The interface-script format for the nearcast schema is:
```
i message h
i field h
```


= Orb

Required knowledge: Engine, Spin.

An Orb is a special type of Spin. Its behaviour is a major focus for the
platform. As a result it's bundled in the same package as the engine
(solent.eng).

Like other spins, an orb gets regular turns from the engine. Within, it hosts
(1) worker-agents called Cogs and (2) a broadcast-like messaging system called
a nearcast.

The orb constructor requires a document that defines the schema of its
nearcats. See Nearcast in this document for that format.

Once the engine event loop is running, the orb will periodically receive
turns. Each time a turn happens, it checks to see whether there are any
messages waiting to be nearcast, and distributes them to each of its cogs
which has a receiver message for that message subject.

When a cog wants to communicate, it "nearcasts" to this messaging system using
a notation such as `self.nearcast.message_name(args)`. On the orb's next
engine turn, it will send that message to all associated cogs who implement
`on_message_name(args)`.

Example application that shows the setup of a simple orb that can hosts
a terminal

```
# Nearcast message format. In 
I_NEARCAST = '''
    i message h
    i field h

    message init
        field height
        field width

    message keystroke
        field keycode
'''

# Example cog which sends and receives. The Cog signature is fixed - all cogs
# must accept the three variables cog_h, org, engine. (The orb assumes that
# structure when it constructs the cog.)
class CogTerm:
    def __init__(self, cog_h, orb, engine):
        self.cog_h = cog_h
        self.orb = orb
        self.engine = engine
        #
        # Term is a spin so that it can receive initiative from the engine
        # independent of the orb. This allows it to do self-maintenance such
        # as screen redraws, or cursor flashing.
        self.spin_term = self.engine.init_spin(
            construct=spin_term_new)
            console_type='curses',
            cb_keycode=self._term_on_keycode,
            cb_select=self._term_on_select)
    def on_init(self, height, width):
        # This method is called when a cog nearcasts an init message.
        # The orb looks out for the 'on_' prefix.
        self.spin_term.open_console(
            height=height,
            width=width)
    def _term_on_keycode(self, keycode):
        # Here, we see this cog sending to the nearcast. This nearcast object
        # is injected into the cog by the orb when it is initialised.
        self.nearcast.keystroke(
            keycode=keycode)
    def _term_on_select

# There is a glossary entry for "Bridge" which gives some more detail on
# this concept.
class CogBridge:
    def __init__(self, cog_h, orb, engine):
        self.cog_h = cog_h
        self.orb = orb
        self.engine = engine
    def nc_init(self, height, width):
        # The orb injects this nearcast object into the cog as part of its
        # init_cog processing. (below)
        self.nearcast.init(
            height=height,
            width=width)

# Example application construction:
def main():
    engine = None
    try:
        engine = engine_new(
            mtu=1500)
        orb = engine.init_orb(
            spin_h='orb',
            i_nearcast=I_NEARCAST)
        #
        # Initialise cogs: this constructs the cogs, injects a nearcast object
        # into each, and places them in the orb's internal nearcast group.
        orb.init_cog(CogTerm)
        bridge = orb.init_cog(CogBridge)
        #
        # Now we use the bridge to kick off the application
        bridge.nc_init(
            height=30,
            width=72)
        #
        # Now we let the engine run its event_loop. At some point it will throw
        # an exception, which we catch below to clean up.
        engine.event_loop()
    finally:
        if engine != None:
            engine.close()

if __name__ == '__main__':
    main()

```

For a slightly more detailed example, see solent.tools.tclient. This shows
basic networking functionality.

This orb/nearcast/cog approach allows developers to quickly build
applications, even if they include complex networking arrangements. Each orb
wraps a plain-old-object. This object doesn't care about the context that it
lives in, just so long as its inputs are respected, and it has somewhere to
make callbacks to.

The cogs act as glue between the plain-old-object they wrap, and their
application's specific messaging arrangements.

The broadcast approach makes it straightforward to unit test. The divide
between general-purpose functionality and application-specific functionality
becomes obvious, and it's easy to write systems of unit tests around each.

People who have worked on sequenced message architectures may like to think of
Orb as being an in-process version of a sequencer architecture.


= Sid

Required knowledge: Engine

Socket management is done entirely within the engine. This allows the engine
to run an efficient select loop.

Applications refer to engine-managed sockets using a concept called a 'sid'.
People with a unix background might notice similarities to the unix concept of
file descriptors.

When an application asks the service to create a network service, it will need
to pass in callbacks. For example, if you create a tcp client, you will need
to provide callbacks that happen on a successful connection
(`cb_tcp_client_connect`), on a connection drop/failed connection
(`cb_tcp_client_condrop`) and when data is received (`cb_tcp_client_recv`).
These callbacks will refer to the socket by its sid.

When an application wants to send data over the client connection, it calls
`engine.send(sid, bb)`. bb is a payloda of bytes.


= Spin

Required knowledge: Engine

A spin is a service that can be associated with the engine, and which will
periodically receive turns in the event loop.


= Track

Required knowledge: Engine, Spin, Orb, Cog

Track consumes nearcast messages, but can't sequence them. It's easiest to
understand this by working to it from the problem it solves.

Imagine you had an application orb, and then a dozen cogs. Several of them
need to track what mode the application is in. If the app is showing a menu,
then keystrokes from the terminal should be translated into menu directives.
If the terminal is currently showing a game board, then keystrokes should be
translated into game instructions.

You don't want to have each cog having special code to keep track of who has
the focus. That would be duplication. Better would be to define all the logic
in a single place. That's what a track is for.

```
class TrackDisplayState:
    def __init__(self, orb):
        self.orb = orb
        #
        self.focus = None
    def on_menu_focus(self):
        self.focus = 'menu'
    def on_game_focus(self):
        self.focus = 'game'
    #
    def is_in_menu_focus(self):
        return self.focus == 'menu'
    def is_in_game_focus(self):
        return self.focus == 'game'

class CogGame:
    def __init__(self, cog_h, orb, engine):
        self.cog_h = cog_h
        self.orb = orb
        self.engine = engine
        #
        self.track_display_state = self.orb.init_track(
            construct=TrackDisplayState)
    def on_something(self):
        if self.track_display_state.is_in_game_focus():
            # etc
```


