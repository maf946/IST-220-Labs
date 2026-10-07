"""UDP poem client: prompt, encode, send, receive, and display.

Run the matching server first. Each client run sends one request.
The client needs no class key and does not contact the AI service directly.
"""
import json
import socket
import uuid

MAX_MESSAGE = 4096
CLIENT_TIMEOUT = 120


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


def main():
    # 1. Collect the destination and application data before creating a socket.
    address = input('Server IPv4 address [127.0.0.1]: ').strip() or '127.0.0.1'
    socket.inet_pton(socket.AF_INET, address)
    port = int(input('Server port: '))
    if not 1 <= port <= 65535:
        raise ValueError('Port must be between 1 and 65535.')
    request = validate({
        'request_id': uuid.uuid4().hex,
        'name': input('Your first name: ').strip(),
        'hobby': input('Your hobby: ').strip(),
    })

    # 2. Create an IPv4 UDP socket and select the peer for this exchange.
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as client:
        client.settimeout(CLIENT_TIMEOUT)
        # UDP connect selects a peer; it does NOT exchange a handshake.
        # The operating system chooses our local source port automatically.
        client.connect((address, port))

        # 3. Encode JSON as UTF-8 bytes and send one datagram.
        client.send(encode(request))
        print(
            '\nRequest sent. Waiting for your poem...\n'
            'The shared AI service may take a minute or two, especially when others are using it.\n'
            'Please leave this window open and wait for the poem or an error before trying again.',
            flush=True,
        )

        # 4. Wait for one response datagram from our selected peer. No retries.
        raw = client.recv(MAX_MESSAGE)
        # 5. Decode JSON, match the reply to our request, and print the result.
        response = json.loads(raw)
        if response.get('request_id') != request['request_id']:
            raise ValueError('Response does not match this request.')
        if not response.get('ok'):
            raise ValueError(response.get('error', 'Server error'))
        print('\n' + response['poem'])
        if response.get('truncated'):
            print('[Poem shortened to fit the lab response limit.]')
    # Leaving the with block closes the client socket.


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('\nStopped.')
    except (OSError, ValueError) as error:
        print(f'Error: {error}')
        raise SystemExit(1)
