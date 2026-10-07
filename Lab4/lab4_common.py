"""Shared protocol and AI-service helpers; uses certifi for HTTPS certificate trust."""
import json
import os
from pathlib import Path
import socket
import ssl
import urllib.error
import urllib.parse
import urllib.request
import uuid

AI_URL = 'https://ai220.m84.us/v1/chat/completions'
MAX_MESSAGE = 4096
UDP_LIMIT = 1200
CLIENT_TIMEOUT = 120


def encode(value):
    return json.dumps(value, ensure_ascii=False, separators=(',', ':')).encode('utf-8')


def settings():
    path = Path(__file__).with_name('lab4_config.json')
    config = json.loads(path.read_text()) if path.exists() else {}
    key = os.environ.get('IST220_AI_KEY') or config.get('api_key', '')
    url = os.environ.get('IST220_AI_URL') or config.get('url', AI_URL)
    model = config.get('model', 'ist220-small')
    if not key or key == 'PASTE_CLASS_KEY_HERE':
        raise ValueError('Set api_key in lab4_config.json using the key from your instructor.')
    parsed = urllib.parse.urlparse(url)
    if parsed.scheme != 'https' and not (parsed.scheme == 'http' and parsed.hostname in ('127.0.0.1', 'localhost')):
        raise ValueError('AI URL must use HTTPS (HTTP is allowed only on loopback).')
    return url, key, model


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def ask_ai(name, hobby, config):
    try:
        import certifi
    except ImportError:
        raise ValueError('Install certifi in the Python environment running this server: python -m pip install certifi') from None
    context = ssl.create_default_context(cafile=certifi.where())
    url, key, model = config
    body = {'model': model, 'stream': False, 'max_tokens': 100, 'temperature': 0.7,
            'messages': [
                {'role': 'system', 'content': 'You write simple rhyming poems. Always respond with four lines of poetry.'},
                {'role': 'user', 'content': f'Write a four-line poem about a college student named {name} who enjoys {hobby}. Mention {name} and {hobby} in the poem. Make the poem about enjoying this hobby and learning new skills.'}]}
    request = urllib.request.Request(url, data=encode(body), headers={
        'Content-Type': 'application/json', 'Authorization': f'Bearer {key}',
        'User-Agent': 'IST220-Lab/1.0'})
    try:
        with urllib.request.build_opener(NoRedirect, urllib.request.HTTPSHandler(context=context)).open(request, timeout=110) as response:
            result = json.load(response)
        poem = result['choices'][0]['message']['content']
        if not isinstance(poem, str) or not poem.strip():
            raise ValueError('Empty poem')
        return poem, result
    except urllib.error.HTTPError as error:
        if error.code == 401:
            raise ValueError('AI service rejected the class key.') from None
        raise ValueError(f'AI service returned HTTP {error.code}; ask your instructor before trying again.') from None
    except urllib.error.URLError as error:
        if isinstance(error.reason, ssl.SSLCertVerificationError):
            raise ValueError('HTTPS certificate verification failed. Update certifi in the server Python environment; if it persists, contact your instructor.') from None
        raise ValueError('Could not connect to the AI service. Check Internet access and the service URL.') from None
    except ssl.SSLCertVerificationError:
        raise ValueError('HTTPS certificate verification failed. Update certifi in the server Python environment.') from None
    except (OSError, ValueError, KeyError, IndexError, TypeError):
        raise ValueError('AI service timed out, was unreachable, or returned an invalid response.') from None


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
        poem, _ = ask_ai(request['name'], request['hobby'], config)
        reply = {'request_id': request_id, 'ok': True, 'poem': poem}
        # Bound both transports to one small application response. JSON escaping counts.
        while len(encode(reply)) > UDP_LIMIT:
            reply['truncated'] = True
            reply['poem'] = reply['poem'][:-1]
        return encode(reply)
    except (ValueError, UnicodeError) as error:
        # Do not echo malformed input or service bodies (which may contain secrets).
        message = str(error) if not isinstance(error, (json.JSONDecodeError, UnicodeError)) else 'Invalid JSON request.'
        return encode({'request_id': request_id, 'ok': False, 'error': message})


def receive_line(connection):
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


def show_address(server):
    port = server.getsockname()[1]
    address = '127.0.0.1'
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as probe:
            probe.connect(('8.8.8.8', 80))
            address = probe.getsockname()[0]
    except OSError:
        pass
    print(f'Port: {port}\nSuggested LAN IP: {address}\nUse 127.0.0.1 for same-computer tests. Ctrl+C stops the server.', flush=True)


def run_server(transport):
    config = settings()
    kind = socket.SOCK_STREAM if transport == 'TCP' else socket.SOCK_DGRAM
    with socket.socket(socket.AF_INET, kind) as server:
        server.bind(('', 0))
        if transport == 'TCP':
            server.listen(5)
        show_address(server)
        while True:
            if transport == 'UDP':
                data, address = server.recvfrom(MAX_MESSAGE + 1)
                server.sendto(reply_for(data, config), address)
            else:
                connection, address = server.accept()
                with connection:
                    connection.settimeout(10)
                    try:
                        data = receive_line(connection)
                        if data is not None:
                            connection.sendall(reply_for(data, config) + b'\n')
                    except (OSError, ValueError) as error:
                        print(f'Connection ended: {error}', flush=True)


def run_client(transport):
    address = input('Server IPv4 address [127.0.0.1]: ').strip() or '127.0.0.1'
    socket.inet_pton(socket.AF_INET, address)
    port = int(input('Server port: '))
    if not 1 <= port <= 65535:
        raise ValueError('Port must be between 1 and 65535.')
    request = validate({'request_id': uuid.uuid4().hex,
                        'name': input('Your first name: ').strip(),
                        'hobby': input('Your hobby: ').strip()})
    kind = socket.SOCK_STREAM if transport == 'TCP' else socket.SOCK_DGRAM
    with socket.socket(socket.AF_INET, kind) as client:
        client.settimeout(CLIENT_TIMEOUT)
        client.connect((address, port))
        if transport == 'TCP':
            client.sendall(encode(request) + b'\n')
            raw = receive_line(client)
        else:
            # Connected UDP selects a peer; it does not perform a handshake.
            client.send(encode(request))
            raw = client.recv(MAX_MESSAGE)
        if raw is None:
            raise ValueError('Server closed without a response.')
        response = json.loads(raw)
        if response.get('request_id') != request['request_id']:
            raise ValueError('Response does not match this request.')
        if not response.get('ok'):
            raise ValueError(response.get('error', 'Server error'))
        print('\n' + response['poem'])
        if response.get('truncated'):
            print('[Poem shortened to fit the lab response limit.]')


def main(function, transport):
    try:
        function(transport)
    except KeyboardInterrupt:
        print('\nStopped.')
    except (OSError, ValueError) as error:
        print(f'Error: {error}')
        raise SystemExit(1)
