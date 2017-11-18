# Overview

Solent is a toolkit for creating event-driven systems.

Solent is currently implemented mostly in python3, with small amounts of C and
C++. When the model is stable, we will lift-and-shift it to become its own
language, with an independent ecosystem.

The goal here is to create a flexible systems-programming platform.


# Platform Goal

Become the leading foundation for concurrent systems development.


# Qualities

## Headlines

The system must be allow developers to reason about exactly what the machine
is doing. It should not abstract this away from users.

Easy to use for programming in the small.

Easy to use for programming in the large.

Easy path to high-performance for those who want it.

Multiplatform. Should work on Unix, Windows and should be a fast port to
anything else (e.g. Android, Haiku).

Zero-dependency. This library should be useful as a go-to tool even in tight
situations.

## Comment

Performance. We will need to be able to create engines that support kqueue,
epoll and IO completion ports.

Zero-dependency. Some features that stand out,

* We need a standard terminal which supports ncurses (done) and a Windows native console. (in progress)

* A lowest-common-denominator network engine uses select(2). (done)

License: The core is LGPL. This is a "free-software" license. It encourages
the community to feed solent improvements back into our codebase. It gives the
same users flexibility to integrate with the system from proprietary code.
Some directories are MIT-licensed. For example, the scenarios directory is
intended to act as documentation, and not to create license complications.
Directories with special licensing arrangements will be specifically marked.

Performance, zero-dependency: implement a solent compiler frontend to LLVM.
Move off python. In the meantime, reduce dependence on garbage collection or
rich python features.


## Learning about solent

You can see examples of solent in use in solent.demo, solent.tools and
scenarios.

An important concept is "the Nearcast". Think of this as an in-process message
bus. Non-trivial applications tend to be a set of actors ("Cogs") arranged
around a nearcast. These concepts are described in more detail in the Glossary
(docs/glossary.md).

Your feedback would be valuable for us improving these docs,

* What attracted your interest?

* What works and does not work when you try to learn from the scenarios?


# Questions and answers

"What can I get from this that I can't get elsewhere?"

Solent is a good foundation for creating sophisticated systems using
event-driven programming techniques.

The canonical work is Leslie Lamport's work on State Machine Replication
(`https://en.m.wikipedia.org/wiki/State_machine_replication`)

There's a tradition of using message-driven techniques to build
high-availability, high-performance systems. For example, here is a video by
former Nasdaq architect Brian Nigito, "How To Build an Exchange".
https://www.youtube.com/watch?v=b1e4t2k2KJY

These ideas have not yet gained widespread use. The author believes that
something like solent will prove to be 'The Railroad of the Digital
Revolution'.


"What is 'sequencer architecture' all about?"

Once you have a system of a certain size, you will want to distribute it
across server farms. Since we have defined the system in terms of messages, it
is straightforward to move from local messaging groups (nearcasts) to network
groups (broadcasts).

In order to be fault-tollerant and deterministic, we must have ordered and
reliable messaging. The messages must be delivered in a deliberately-ordered
sequence. Hence, sequencer architecture. 


"What are the advantages again?"

You can build small things quickly. You can easily scale small things into
large things. You can easily maintain large things.

Solent is suited to embarassingly-concurrent problems. Example: simulations,
games, trading systems. It is also effective for just building small fiddly
stuff, such as an application that needed to effortlessly juggle several types
of network connection at the same time.


"What components does solent have?"

* Engine: concurrency engine. Uses async networking patterns (e.g. select). Offers TCP client/server and UDP pub/sub. Select loop and scheduling is done for you.

* Nearcast: an in-process messaging backbone.

* Term: general-purpose textual console (currently offers pygame and curses consoles. Windows-native is coming, to maintain our no-dependency goal.)

* Access shared libraries (e.g. compiled C).

* Binary distriction (uses pyinstaller)


"Is it fast?"

Not yet.

The engine currently uses the select() mechanism in Windows and Unix. select()
is slower than poll on unix, and significantly slower than
IO-completion-sockets on Windows, kevent on BSD, epoll on linux.

There is nothing inherently slow in its design. In time we may replace the
internals of Engine with a solution taken from asyncio, twisted or libuv. Or
we may rewrite the engine in C++ and offer python wrappers to it.


# Compare to other systems

"How does it compare to system x?"

The essential idea in solent is for systems to be message-driven. So far, we
demonstrate this with the nearcast.

These approaches give rise to a programming style that is message-centric and
event-driven. This encourages a layering approach that leads to robust,
discoverable systems.

The simpler response to most "why didn't you use x" brings out recurring
themes,

* Not sufficiently message-driven.

* Not ambitious enough.

* Abstracts the computer from the developer too much.


## Python3 asyncio

Asyncio is a asynchronous concurrency library. A lot of engineering has
gone into its throughput performance.

AsyncIO is tied to Python, which is garbage-affected. AsyncIO relies on complex language features of the Python ecosystem, (abstraction).

AsyncIO does not aspire to high-level patterns, and asyncio doesn't do nearcasting. (ambition)

AsyncIO does not do nearcasting. You could implement nearcasting on top of it.


## Twisted

Twisted is a multiplatform concurrency systems. A lot of engineering has gone
into its throughput performance.

Twisted has something like spins, but nothing like the nearcast, orbs or cogs.

It is a python library (ambition).


## Tornado

It's like twisted, with fewer features, but a bit easier to get started with for the features it does have. Has nothing like the nearcast.


## ZeroMQ

ZeroMQ is a messaging system that takes a lot of the hassle out of messaging
between hosts. Unlike RabbitMQ, there is no central broker.

ZeroMQ is an excellent abstraction. But, as a result, it does not allow the developer to reason about what is on the wire (abstraction).


## NodeJS

NodeJS is a toolbox for creating asynchronous applications in javascript.

Its core is a high-performance async library called libuv, which is excellent.
Perhaps we will create a high-performance Engine option using libuv.

NodeJS doesn't do nearcasting. Javascript is garbage-collected (ambition).


## RabbitMQ and Tibco

RabbitMQ is a message broker system. In a typical RabbitMQ ecosystem, you will
have a standalone message broker, and then applications that want to talk to
one another. The applications will use a rabbitmq library to send messages to
the broker, and then the broker distributes them out to applications.

You could see this approach as rival worldview to solent.

Solent systems tend to be a single codebase. Within this codebase, there is a
contained message system. RabbitMQ systems tend to be dispirate codebases that
fire messages to one another via the broker.

The RabbitMQ approach can be used to great effect. But if you are not vigilant
about the circumstances of who can send to each channel, and who can receive
from each channel, it rapidly evolves into horror.

Tibco is essentially a commercialised form of the same ideas behind RabbitMQ.


## Apache Kafka

Kafka is a bit like RabbitMQ. A difference is that the kafka cluster caches
messages that are sent to it. So if an application misses some messages or
restarts, it can go to the kafka cluster and backfill.

It is not much work to create a spin in solent that could talk to Kafka. At
the time of writing, the quality of the libraries for Python are not
fantastic.


## Java

Java NIO2 is a fantastic concurrency library. There is no concept of the
nearcast inherent to nio2.

With effort, you can implement a zero-garbage coding style in Java.

You could definitely implement Solent on a Java foundation. If anyone is
interested in working on this, do say.


## Erlang

In Erlang, you send messages between actors, as a point-to-point interaction.
You design systems to correct in situations where a sent message does not
reach its target.

Solent takes a different approach: its essence is a reliable stream of
deliberately ordered messages.

The nearcast allows Solent to be more effective for programming in the small
than Erlang, and at least as effective for programming in the large.


## C/C++/Ada/Rust

Useful languages. We are using some C/C++ for interacting with Windows.

Solent development is driven by DSLs. For example, the nearcast schema does a
lot of code generation. It is easier to do this in python.

I would be open to writing high-performance engines in Ada or Rust, producing
object files, wrapping them in python/solent-lang.


## Lisp/ML/Haskell

For the core: Lazy functional programming is probably a bad fit for the
requirement that the programmer should be able to reason about exactly what
the machine is doing. Eager evaluation could work. There are garbage
complications with these platforms too. Open to talk.

For templating: those would have worked, but python is just good enough.


# Community/Contributions

Except where specifically marked, the codebase will be licensed under the
LGPL, with copyright assigned to the FSF. Contributions are welcome. See
[Contributing guidelines](CONTRIBUTING.md)


# Quickstart

This will get you seeing some basic stuff

```bash
# In unix, you will need python3 and git

git clone https://github.com/cratuki/solent.git
cd solent
python3 -m venv venv

. venv/bin/activate

# Use keys around 's' to navigate.
python -m solent.demo.snake
python -m solent.demo.weeds

# There are many more scenarios in this directory
python -m scenarios.eng_10_orb_nearcast_and_cog_basics
```

```bash
# In Windows, you will need python3 and git-for-windows

git clone https://github.com/cratuki/solent.git
cd solent
python3 -m venv venv

venv\Scripts\activate
pip install pygame

# Use keys around 's' to navigate.
python -m solent.demo.snake
python -m solent.demo.weeds

# There are many more scenarios in this directory
python -m scenarios.eng_10_orb_nearcast_and_cog_basics
```

# Creating an installer/distribution

Here's how you create a distribution. This could be useful if you're trying to
create a release distro on another platform.

```bash
(Install python3.4 or later)

(Install SDL for your platform)

git clone github.com/cratuki/solent
cd solent

#
# // Create the virtual environment
python -m virtualenv venv

#
# // Activate the virtual environment
(cd venv; . bin/activate; cd ..)

#
# // If you didn't install a system-wide pygame, you can install it via pip.
pip3 install "hg+https://bitbucket.org/pygame/pygame"

#
# // Install other libraries we need in the virtualenv
pip3 install -r requirements.txt

#
# // Use pyinstaller to create the packages
#
# This works on unix, but won't work on Windows.
pyinstaller solent/pyinstaller/snake_curses.spec
#
# This should work anywhere that pygame is installed
pyinstaller solent/pyinstaller/snake_pygame.spec

#
# // Look in the dist directory for the resulting binaries
#
```


