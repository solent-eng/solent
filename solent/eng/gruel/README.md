# Overview

Gruel is deliberately-simple network protocol.

xxx Will refactor this to a spec along the lines of
https://www.nasdaqtrader.com/content/technicalsupport/specifications/dataproducts/soupbintcp.pdf


# Compare to SOUP

It's similar to SOUP, but serves a different purpose.
- SOUP is a near tradeoff that is well-suited to certain trading scenarios.
- Gruel seeks to be open-ended, and a lowest-common-denominator protocol over
  which you can then build more sophisticated application protocols.

Some detailed differences:
- Heartbeat logic is a bit simpler to implement in gruel.
- Developers can have direct control over payload size in gruel.
- Messages don't have a sequence number. There's no concept of gap-filling at
  the protocol level. (You can still achieve this, but you'd implement it at
  the application layer.)
- You can put newline characters in your payload.
- UTF8 is fine in gruel. (Many SOUP participants don't care)


# Messages


```
// Types
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
                    u2/max_doc_size         in bytes
                    vs/protocol_h           identifier for the protocol
                    vs/password
                    vs/notes

    server_greet:   u1/message_type         1
                    u2/max_packet_size      in bytes
                    u2/max_doc_size         in bytes
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


