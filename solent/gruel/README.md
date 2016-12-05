# Overview

Gruel is a lightweight deliberately-simple asynchronous network protocol. It
uses a client-serer model and is build on TCP.

This protocol is ideal for situations where you need to pass arbitrary
documents in either direction between client and server. Unlike some similar
protocols, it does not identify documents at the protocol level, or directly
offer any rewind or gap-fill functionality. This functionality can still be
implemented at the application level where it is needed.

Anything can be send in the payload of documents. But this system is
particularly well suited to sending and receiving Interface Script. This is a
powerful pairing, and allows for fast construction of robust systems that are
easy to troubleshoot. Interface Script is documented separately.


# Compare to SOUP

Gruel has some similarities to similar to SOUP, but serves a different purpose.
- SOUP is a neat tradeoff suited to certain trading scenarios.
- Gruel seeks to be an open-ended, lowest-common-denominator protocol which
  pushes responsibility for functionality to the application layer.

Some detailed differences:
- Heartbeat logic is simpler to implement in gruel.
- Developers can have direct control over payload size in gruel. This gives
  app developers a means for bypassing infrastructure problems that might
  otherwise block projects.
- You can put newline characters in your payload.
- Gruel supports UTF8.
- Gruel Messages don't have a sequence number. There's no concept of
  gap-filling at the protocol level. (You can still achieve this, but you'd
  implement it at the application layer.)

Systems that require two-factor authentication can achieve this on a Gruel
server by (1) applying an IP permission check and (2) checking the password
that the client sends in their Client Login message.

The current implementation is designed to require one server port per client.


# Protocol flow

A connection starts with a client making a tcp connection to a server.

The server may apply an ip permission check at this stage. Where a new
connection did not satisfy the check, the server would close the TCP
connection, possibly after a short pause.

After a successful TCP connection, the client sends a Client Login message.

The server validates the Client Login message. It responds with either a
Server Greet or Server Bye message. If it is a Server Bye message, they should
give an indication of the reason for the disconnect in the notes field of that
message, and then close the TCP connection, possibly after a short pause.

If it is a Server Connect message, then the link is up. The client and server
can send documents to one another at their whim. To send a document, the
sender breaks it up so that it can be packaged into a number of Docpart
messages. The sender marks each docpart message as incomplete until it reaches
the last. This it flags as complete. A sender cannot send two documents in
parallel.

Server and client should send heartbeat messages to one another based on the
interval recommended in the Client Login message. Exact behaviour of these
messages is not so important, just so long as either party can quickly detect
a dropped connection if they decide this is a priority.


# Messages

The first byte of every payload indicates a message type.


```
// Field datatypes

    u1
        unsigned byte, equv to uint8_t in C

    u2
        equiv to uint16_t in C

    vs:
        string of variable length. the first two bytes are an unsigned int
        that tell you how long the rest of the field is. this string will
        not be terminated by 0x00.

// Messages
    client_login:   u1/message_type         0
                    u1/heartbeat_interval   seconds between heartbeats
                    u2/max_packet_size      in bytes
                    u2/max_fulldoc_size     in bytes
                    vs/protocol_h           identifier for the protocol
                    vs/password
                    vs/notes

    server_greet:   u1/message_type         1
                    u2/max_packet_size      in bytes
                    u2/max_fulldoc_size     in bytes
                    vs/notes

    server_bye:     u1/message_type         2
                    vs/notes

    server_bye:     u1/message_type         3
                    vs/notes

    heartbeat:      u1/message_type         4

    docpart:        u1/message_type         5
                    u1/b_completes          acts as bool. should be 0 or 1.
                    vs/payload
```


