"""TCP poem server: bind, receive, generate a reply, and send it back.

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


def receive_line(connection):
    """Read the application's newline delimiter, not just one TCP chunk."""
    data = bytearray()
    while b'\n' not in data:
        chunk = connection.recv(1024)
        if not chunk:
            if not data:
                return None  # A port scan can connect without sending an application request.
            raise ValueError('Connection ended before the complete message arrived.')
        data.extend(chunk)
        if len(data) > MAX_MESSAGE:
            raise ValueError('Message is too large.')
    return bytes(data).split(b'\n', 1)[0]


def main():
    # 1. Load the key and URL for the separate HTTPS call to the AI service.
    config = settings()
    # 2. Create the listening socket. Port 0 asks the OS for an available port.
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
        server.bind(('', 0))  # Empty address listens on all local IPv4 interfaces.
        server.listen(5)     # Allow a small queue of pending connections.
        show_address(server)

        # 3. Accept one client at a time. The listening socket remains open.
        while True:
            connection, address = server.accept()
            # accept returns a NEW socket for communicating with this client.
            with connection:
                connection.settimeout(10)
                try:
                    # 4. Collect the full request. A scan may send no data at all.
                    data = receive_line(connection)
                    if data is not None:
                        # 5. Decode/validate JSON and request a poem over HTTPS.
                        reply = reply_for(data, config)
                        # 6. Send the complete response plus its delimiter.
                        connection.sendall(reply + b'\n')
                except (OSError, ValueError) as error:
                    print(f'Connection ended: {error}', flush=True)
            # Close this client connection, then return to accept the next one.


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('\nStopped.')
    except (OSError, ValueError) as error:
        print(f'Error: {error}')
        raise SystemExit(1)
