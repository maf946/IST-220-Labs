# How the poem socket programs work

All programs use Python's standard library. The four short entry-point files select TCP or UDP and client or server behavior. The implementation is in `lab4_common.py`; read that file when tracing socket calls.

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
