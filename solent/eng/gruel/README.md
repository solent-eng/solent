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
    client_greet:   u8/message_type     0
                    u8/beat_interval    seconds between heartbeats
                    u16/max_packet_len  in bytes
                    u16/max_doc_size    in bytes
                    s100/protocol_h     identifier for the protocol
                    s100/username
                    s100/password
                    s100/notes

    server_greet:   u8/message_type     1
                    u16/max_packet_len
                    u16/max_doc_size    in bytes
                    vs/notes

    client_logout:  u8/message_type     2
                    vs/notes

    server_bye:     u8/message_type     3
                    vs/notes

    heartbeat:      u8/message_type     4

    docpart:        u8/message_type     5
                    u8/b_completes      boolean
                    s40/sender_doc_h
                    b/payload
```


