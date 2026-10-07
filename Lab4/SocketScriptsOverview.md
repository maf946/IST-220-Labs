# How the poem socket programs work

The socket programs use Python's standard library; the HTTPS helper also uses certifi's trusted certificate bundle. Install certifi into the project interpreter as explained in the lab instructions. Clients alone do not call the HTTPS helper. Each of the four scripts contains its own socket operations, JSON handling, validation, and main program. Some code is deliberately duplicated so you can follow a complete exchange without switching to a shared transport implementation. Only the AI configuration and HTTPS call remain in `lab4_common.py`; neither client imports it.

## Where to look in the code

| Script | Follow these operations in `main()` |
|---|---|
| `UDPClient.py` | Prompt → create `SOCK_DGRAM` socket → select peer → `send` one datagram → `recv` one reply → print poem |
| `UDPServer.py` | Load AI settings → create `SOCK_DGRAM` socket → `bind` → repeatedly `recvfrom`, build a reply, and `sendto` the sender |
| `TCPClient.py` | Prompt → create `SOCK_STREAM` socket → `connect` → `sendall` → collect a newline-delimited reply → print poem |
| `TCPServer.py` | Load AI settings → create `SOCK_STREAM` socket → `bind` → `listen` → repeatedly `accept`, read, reply, and close the accepted socket |

Start with `main()` in each script, then read the helper functions above it. In both servers, `reply_for()` shows how the received JSON becomes an AI request and how the poem becomes a reply. In both TCP scripts, `receive_line()` shows the loop needed to collect a full message from a byte stream. Each socket is inside a `with` block, which closes it on exit.

The servers’ `show_address()` function uses a separate UDP socket to ask the operating system which local address it would use to reach an external address. It does not send application data; this is only a suggested address for the startup display.

The class key, certificate bundle, model prompt, and HTTPS request live in `lab4_common.py`. The student socket conversation is entirely in the four scripts.

## One request, two network conversations

The client prompts for a numeric IPv4 address, port, first name, and hobby. It creates a random request ID and sends a UTF-8 JSON object:

```json
{"request_id":"example-id","name":"Alex","hobby":"stargazing"}
```

The Python server validates the request, then sends a separate HTTPS POST to the shared AI service. It includes the class key in that HTTPS request's Authorization header. The key never belongs in the student client's message.

The shared model returns a poem. The Python server extracts it and sends an application response back to the student client:

```json
{"request_id":"example-id","ok":true,"poem":"A first line\nA second line"}
```

Errors use `ok: false` and an `error` field. The client checks the request ID and displays the poem or error. An ID correlates messages; it is not encryption, authentication, or a delivery guarantee.

## UDP

`socket(AF_INET, SOCK_DGRAM)` creates an IPv4 UDP socket. The server binds to `('', 0)`: all local IPv4 interfaces and an operating-system-selected port. It receives a request with `recvfrom` and replies to the sender with `sendto`.

The UDP client calls `connect` to select its peer, then uses `send` and `recv`. UDP's `connect` does not exchange a handshake and does not establish TCP-style reliability. Each request and response occupies one datagram. The server limits the encoded response to 1,200 bytes, trimming poem text if needed and adding `truncated: true`. This keeps responses small; it does not guarantee that every possible network path avoids IP fragmentation.

There are no automatic retries. If a request or response is lost, the client can time out. Re-running the client creates a new ID and may create another model request.

## TCP

`socket(AF_INET, SOCK_STREAM)` creates an IPv4 TCP socket. After binding, the server calls `listen`, then `accept` to obtain a separate connected socket for each client.

TCP transports an ordered byte stream. A single `recv` call is not guaranteed to return one complete application message. This lab ends each JSON message with a newline; `receive_line` reads until that delimiter arrives, with a maximum message size. JSON escapes line breaks inside the poem, so they do not interfere with framing. `sendall` sends the complete encoded message. The application handles one request per connection and closes afterward.

An empty connection from a port scan is closed without contacting the model. An incomplete request or idle connection is bounded by a timeout. The server processes clients sequentially; a listen backlog is not parallel model execution.

## Timing and limits

The shared AI request has a 110-second socket timeout; student clients wait up to 120 seconds for socket operations. These are network operation timeouts, not strict guarantees of total wall-clock duration. Proxies may impose their own limits. Name and hobby lengths are bounded, and messages are limited to 4,096 bytes. The server does not retry or grade poem quality.

The student-to-Python-server exchange is readable plaintext over either protocol. The Python-server-to-AI exchange uses HTTPS. Capture the correct interface and port to distinguish them.
