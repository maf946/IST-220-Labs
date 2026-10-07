"""UDP poem server: bind, receive, generate a reply, and send it back.

Leave this running while a client connects. Only the AI-service configuration
and HTTPS request are imported; the student-facing protocol is shown here.
"""
import json
import socket
from lab4_common import settings, ask_ai

MAX_MESSAGE = 4096
RESPONSE_LIMIT = 1200


def encode(value):
    return json.dumps(value, ensure_ascii=False, separators=(',', ':')).encode('utf-8')


def validate(request):
    if not isinstance(request, dict):
        raise ValueError('Request must be a JSON object.')
    for field, limit in (('request_id', 32), ('name', 40), ('hobby', 80)):
        value = request.get(field)
        if not isinstance(value, str) or not value.strip() or len(value) > limit or any(ord(c) < 32 for c in value):
            raise ValueError(f'{field} must contain 1–{limit} printable characters.')
    return request


def reply_for(data, config):
    request_id = ''
    try:
        if len(data) > MAX_MESSAGE:
            raise ValueError('Request is too large.')
        request = validate(json.loads(data))
        request_id = request['request_id']
        print(f"Request from {request['name']} ({request['hobby']})", flush=True)
        # This helper makes the separate authenticated HTTPS request.
        poem, _ = ask_ai(request['name'], request['hobby'], config)
        reply = {'request_id': request_id, 'ok': True, 'poem': poem}
        # Bound both transports to one small application response. JSON escaping counts.
        while len(encode(reply)) > RESPONSE_LIMIT:
            reply['truncated'] = True
            reply['poem'] = reply['poem'][:-1]
        return encode(reply)
    except (ValueError, UnicodeError) as error:
        # Do not echo malformed input or service bodies (which may contain secrets).
        message = str(error) if not isinstance(error, (json.JSONDecodeError, UnicodeError)) else 'Invalid JSON request.'
        return encode({'request_id': request_id, 'ok': False, 'error': message})


def show_address(server):
    """Print a suggested LAN address; the UDP probe sends no application data."""
    port = server.getsockname()[1]
    address = '127.0.0.1'
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as probe:
            probe.connect(('8.8.8.8', 80))
            address = probe.getsockname()[0]
    except OSError:
        pass
    print(f'Port: {port}\nSuggested LAN IP: {address}\nUse 127.0.0.1 for same-computer tests. Ctrl+C stops the server.', flush=True)


def main():
    # 1. Load the key and URL for the separate HTTPS call to the AI service.
    config = settings()
    # 2. Create a UDP socket. Port 0 asks the OS for an available port.
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as server:
        server.bind(('', 0))  # Empty address listens on all local IPv4 interfaces.
        show_address(server)

        # 3. Receive one datagram at a time. UDP needs no listen or accept calls.
        while True:
            # recvfrom supplies both the message bytes and the sender's IP/port.
            data, address = server.recvfrom(MAX_MESSAGE + 1)
            # 4. Decode/validate JSON and request a poem over separate HTTPS.
            reply = reply_for(data, config)
            # 5. Send one reply datagram to the client that sent this request.
            server.sendto(reply, address)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('\nStopped.')
    except (OSError, ValueError) as error:
        print(f'Error: {error}')
        raise SystemExit(1)
