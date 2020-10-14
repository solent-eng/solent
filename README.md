# Obsolete

20201014 Update. Now that the Rust language supports coroutines, this points
to a better way of building event-driven distributed systems than the path
that I was carving out with Solent. Regard solent as obsolete. Instead, see
cthulix.com/preview.html


# Overview

Solent is a toolkit for creating event-driven systems.

Solent is currently implemented mostly in python3, with small amounts of
C/C++. When the model is stable, we will lift-and-shift it to become its own
language, with an independent ecosystem.

The goal here is to create a flexible systems-programming platform.


# Platform Goal

Become the leading foundation for the development of concurrent systems.


# Qualities

Priorities, in order of precedence,

* Allow developers to reason about what the machine is doing.

* Be low-dependency. This library should be useful as a go-to tool even in
  tight situations.

* Offer convenience and abstraction

* Be good for programming in the small.

* Be good for programming in the large.

* Be effective for users who want to pursue high-performance.

* Operate well in Unix.

* Operate well in Windows.

* Expand to support other platforms (e.g. Android, Haiku).


# License

LGPL, except for some directories which are marked as MIT-license. (in
particular, documentation and tutorials are intended to be obligation-free)


# Quickstart

This will get you seeing some basic stuff

```bash
# In unix, you will need python3 and git

git clone https://github.com/solent-eng/solent.git
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
# (The Windows native console is not working at the time of writing, and these
# steps will fail. This is due to the build process for the DLLs being too
# tightly tied to my dev environment. Covered in issue #139).

git clone https://github.com/solent-eng/solent.git
cd solent
python3 -m venv venv

venv\Scripts\activate
pip install pygame

# Use keys around 's' to navigate.
python -m solent.demo.winsnake
python -m solent.demo.weeds

# There are many more scenarios in this directory
python -m scenarios.eng_10_orb_nearcast_and_cog_basics
```

# Community/Contributions

Except where specifically marked, the codebase will be licensed under the
LGPL, with copyright assigned to the FSF. Contributions are welcome. See
[Contributing guidelines](CONTRIBUTING.md)


# Principle of "Bolts on the outside"

We construct the systems so that user-developers can methodically reason about
what is going on.

Code should be readable.

Good design should encourage users to speculate about how the system is
working, and then quickly source-dive to confirm this. If Solent evolves this
way, its design should steer user-developers to build enclosing systems to a
similar standard.

We follow a guiding principle is "bolts on the outside".


# Learning more

The engine is the heart of the system. Once you understand this, the rest
unfolds.

You can see examples of solent in use in solent.demo, solent.tools and
scenarios.

An important concept is "the Nearcast". Think of this as an in-process message
bus. Non-trivial applications tend to be a set of actors ("Cogs") arranged
around a nearcast. These concepts are described in more detail in the Glossary
(docs/glossary.md).


# Questions and answers

"I want to do network programming in Python. Why should I chose Solent?"

You probably shouldn't. We do not currently have support for coroutines, and
this is a game-changer if you are an application programmer. You should
probably be learning python3 asyncio.

(However, if you are struggling with python3 asyncio, you may find a study of
solent helps you to understand the concepts that drive it. The solent engine
is quite similar to selector at the heart of asyncio, and probably an easier
study.)


"What can I get from this that I can't get elsewhere?"

Not much at the moment.

Solent is intended to be the foundation of a sophisticated systems programming
platform. Work in progress.


"So why are you doing this?"

There's a tradition of using message-driven techniques to build
high-availability, high-performance systems. For example, here is a video by
former Nasdaq architect Brian Nigito, "How To Build an Exchange".
https://www.youtube.com/watch?v=b1e4t2k2KJY

The canonical work that this builds on is Leslie Lamport's work on State
Machine Replication
(`https://en.m.wikipedia.org/wiki/State_machine_replication`)

Solent will evolve into such a platform. And it will be covered by a free
software license.


"What is 'sequencer architecture' all about?"

Once you have a system of a certain size, you will want to distribute it
across server farms. Since we have defined the system in terms of messages, it
is straightforward to move from local messaging groups (nearcasts) to network
groups (broadcasts).

In order to be fault-tollerant and deterministic, we must have ordered and
reliable messaging. The messages must be delivered in a deliberately-ordered
sequence. Hence, sequencer architecture. 


"What components does solent have?"

So far,

* Engine: concurrency engine. Uses async networking patterns (e.g. select). Offers TCP client/server and UDP pub/sub. Select loop and scheduling is done for you.

* Nearcast: an in-process messaging backbone.

* Grid console: a general-purpose textual console (curses, windows-native).

* Access shared libraries (e.g. compiled C).

* Binary distriction (uses pyinstaller)


"Is it fast?"

Not currently.

We currently have a single engine implementaiton only, and that uses
select(2). select(2) is slower than poll on unix, and significantly slower
than IO-completion-sockets on Windows, kevent on BSD, epoll on linux.

There is nothing inherently slow in the Solent design. In time we may replace
the internals of Engine with a solution taken from asyncio, twisted or libuv.
Or we may rewrite the engine in C++ and offer python wrappers to it.


"Any notable flaws?"

It is unfortunate that the current user interface system is essentially
synchronous. It would be better as an event-driven settlement.



