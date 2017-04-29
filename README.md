# Project Overview

"What's the pitch?"

Sequencer-architecture platform, currently written in python3, offered under a
free-software license (LGPL).


"What can I get from this that I can't get elsewhere?"

Solent is a good foundation for creating sophisticated systems using
event-driven programming techniques. As far as I know, this is the first
version of such a system available under a free software license.

There's a tradition of using message-driven techniques to build
high-availability, high-performance systems using these approaches.

Here is a video by former Nasdaq architect Brian Nigito, "How To Build an
Exchange". https://www.youtube.com/watch?v=b1e4t2k2KJY

For another prespective, see Leslie Lamport's work on State Machine
Replication (`https://en.m.wikipedia.org/wiki/State_machine_replication`)

These ideas have not yet gained widespread use. The author believes that
something like solent will prove to be 'The Railroad of the Digital
Revolution'.


"What is 'message broadcast' all about?"

Mainstream software techniques build systems from nodes or objects. The
messages that pass between the nodes are generally an afterthought to the
behaviour of the nodes themselves. As a result, most software is brittle.

Solent has a different focus. Solent systems are defined in terms of their
message schema. Nodes emerge as a consequence of the message schema. This
leads to much better software, particularly at scale.


"What is 'sequencer architecture' all about?"

Once you have a system of a certain size, you will want to distribute it
across server farms. Since we have defined the system in terms of messages, it
is straightforward to move nodes off their local messaging groups (nearcasts)
to network groups (broadcasts).

But once we reach this scale, we will also want fault-tolerence.

Key to this is to have ordered and reliable messaging. Hence, sequencer
architecture.


"What are the advantages again?"

You can build small things quickly. You can easily scale small things into
large things. You can easily maintain large things.

Solent is a good approach to building embarassingly concurrent problems.
Example: simulations, games, trading systems. It's also effective for building
small staff.


"What components does solent have?"

* Eng: concurrency engine. Uses async networking patterns (e.g. select). Offers TCP client/server and UDP pub/sub. Select loop and scheduling is done for you.

* Nearcast: an in-process mechanism backbone.

* Gruel: general-purpose bidirection asynchronous network protocol. (Nasdaq publish a spec for a protocol called SOUP. Somebody who knew about SOUP would hopefully judge Gruel to be a predictable evolution.)

* Term: general-purpose textual console (currently offers pygame and curses consoles)

* Mechanisms to build create shared libraries from C and access them from python

* Mechanisms for creating binary distributions (uses pyinstaller)


"How evolved is it?"

/Functionality that is already solid

Solent is now effective for building single-process message-oriented systems.
If you wanted to build a complex network app or roguelike game in a single
process, you'd find it to be a sharp tool.

/Memory management

So far, solent development has been sloopy about memory management. Ideally
we'd be deliberately allocating all memory using either the struct library
or the C bridge.

It's possible that a JITting VM like pypy would manage out the remaining
inefficiencies.

Regardless, we've introduced a memory pool, and started to be deliberate about
allocation in the engine core. This is still in the early days.

/Broadcasting

We don't yet have solid redundancy mechanisms in place, and we will
need that before we offer network-based broadcasting.

You could get some distance by wiring nodes together with using supplied Gruel
tools. But that's not at all in the spirit of the system. Where we need to get
to is sequenced broadcasting with a scribe and failover options.


"With all that, what are some things it would be a good foundation for?"

Digital audio studio, alt-coin exchange, clearing house, monitoring platform,
reference-data aggregator.


"Where can I learn more?"

The Glossary (docs/glossary.md) gives an overview of the platform's major
concepts.


"Is it fast?"

Probably not, at the moment.

The engine currently uses the select() mechanism in Windows and Unix. select()
is slower than poll on unix, and significantly slower than
IO-completion-sockets on Windows, kevent on BSD, epoll on linux.

There is nothing inherently slow in its design. Perhaps at some future time we
will replace the innards of Engine with a solution derived from asyncio,
twisted or libuv. Or we could rewrite the engine in C++ and then offer python
wrappers to it.


"How does it compare to system x?"

/Comment

The essential idea in solent is the nearcast. As far as we know, there are no
other platforms pitching a software method around this idea.

In time, solent will develop the ability to offer nearcast-like functionality
over multiple hosts. This will consist of UDP-broadcast with a reliability
layer over the top of it.

These approaches give rise to a programming style that is message-centric and
event-driven. This encourages a layering approach that leads to strong code.

Hence, the answer to "why didn't you use x" is likely to be, "because
nearcasting".


/NodeJS

NodeJS is an toolbox for building asynchronous applications in javascript.

Its core is a high-performance async library called libuv. This is excellent.
Perhaps we will reimplement solent.eng.Engine in libuv.

NodeJS doesn't do nearcasting.


/Python3 asyncio

Asyncio is a asynchronous concurrency library. A lot of engineering has
gone into its throughput performance.

AsyncIO doesn't aspire to have high-level patterns, and asyncio doesn't do
nearcasting.


/Twisted

Twisted is a multiplatform concurrency systems. A lot of engineering has gone
into its throughput performance.

Twisted has something like spins, but nothing like the nearcast, orbs or cogs.


/Tornado

It's like twisted, with fewer features, but a bit easier to get started with
for the features it does have. Has nothing like the nearcast.


/RabbitMQ

RabbitMQ is a message broker system. In a typical RabbitMQ ecosystem, you will
have a standalone message broker, and then applications that want to talk to
one another. The applications will use a rabbitmq library to send messages to
the broker, and then the broker distributes them out to applications.

You could see this approach as rival worldview to solent, and think in terms
of skeleton vs exo-skeleton.

Solent systems tend to be a single codebase. Within this codebase, there is a
contained message system. RabbitMQ systems tend to be dispirate codebases that
fire messages to one another via the broker.

As you would expect, RabbitMQ has no concept of a nearcast.

The RabbitMQ approach can be used to great effect. But if you are not vigilant
about the circumstances of who can send to each channel, and who can receive
from each channel, it rapidly evolves into horror.

It would probably not be much work to create a spin in solent that could talk
to RabbitMQ.


/Tibco

Tibco is essentially a commercialised form of the same ideas behind RabbitMQ.


/ZeroMQ

ZeroMQ is a messaging system that takes a lot of the hassle out of messaging
between hosts. Unlike RabbitMQ, there is no central broker.

In ZeroMQ, everyone needs to be talking ZeroMQ. It doesn't deal with design
within an applicaiton. Hence, there is no nearcast.

It would probably not be much work to create a spin in solent that could talk
to ZeroMQ.


/Apache Kafka

Kafka is a bit like RabbitMQ. A difference is that the kafka cluster caches
messages that are sent to it. So if an application misses some messages or
restarts, it can go to the kafka cluster and backfill.

It is not much work to create a spin in solent that could talk to Kafka. At
the time of writing, the quality of the libraries for Python are not
fantastic.


/Java

Java NIO2 is a fantastic concurrency library. There is no concept of the
nearcast inherent to nio2.

With effort, you develop a zero-garbage coding style in Java.

You could definitely implement Solent on a Java foundation. If anyone is
interested in undertaking a project like this, let me know.


/Other languages

We chose python because it was easy to get started. Given thta we would like
to evolve this system towards high-throughput, low-latency behaviour, it may
make sense to rewrite the core to a non-garbange-collected platforms such as
C, C++ or Rust. Also, Golang has an easy-to-understand garbage collection
methodology, and a tight syntax. If anyone has interest in doing work to port
either the engine or all of solent to one of these systems, get in touch. Some
groundwork is already done.


# Community/Contributions

Except where specifically marked, the codebase will be licensed under the
LGPL, with copyright assigned to the FSF. Contributions are welcome. See
[Contributing guidelines](CONTRIBUTING.md)

We aim for this system to be multi-platform with no dependencies on other
libraries.


# Quickstart (unix systems)

This will get you seeing some basic stuff

```bash
git clone https://github.com/cratuki/solent.git

cd solent

bin/arrange_dependencies

# Whenever you open a new prompt, do this to make your
# virtual env active
(cd venv; . bin/activate; cd ..)

# Demo of the solent.eng concurrency system
python -m solent.eng.scenarios

# Install pygame (if you want - you can use curses instead).
pip3 install hg+https://bitbucket.org/pygame/pygame

python -m solent.release.snake --curses
python -m solent.release.snake --pygame

python -m solent.release.roguebox_00_weed_the_garden --curses
python -m solent.release.roguebox_00_weed_the_garden --pygame
```

If you want to understand the network layer, look at solent.eng.scenarios.


# Quickstart (Windows)

Install git for windows (from https://git-for-windows.github.io).

Install python 3.6 (other versions of python3 may work). On the launch screen,
select the option to add it to your PATH. Virtual env comes bundled in recent
releases of python.

Once you are in your git-for-windows shell, you can clone the repository,
create a virtual environment, and activate it. In these steps, be sure to use
the package virtualenv and not the reduced version of it that bundles with
recent versions of python (venv), as they behave differently. For example, you
don't get a unixy activate script with the venv module.

```bash
git clone https://github.com/cratuki/solent

cd solent

python -m virtualenv venv

. venv/bin/activate

pip install pygame

python -m solent.release.snake --pygame

python -m solent.release.roguebox_00_weed_the_garden --pygame
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

# What people are saying

"I definitely see the value, having gone through the pain of implementing
get/setsockopt. You've taken the common 5 or 6 steps required to get a BSD
socket up and running and boiled it down to a nice set of options. Kudos."
(Lead developer of a free software operating system project)

"I'm guessing you're off work, how long have you got for all this (really
jealous BTW). (... some evangelism from me about getting involved with the
project ,,,) So when I said jealous I meant of your time, you have time, so
jealous." (Former colleague)

"Apart from that you are apparently still not working? I am not exactly sure
what the problem is - do you need to go in a different direction?" (My mother)


