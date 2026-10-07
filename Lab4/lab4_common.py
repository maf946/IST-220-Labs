"""AI-service configuration and HTTPS only; student sockets live in the four scripts."""
import json
import os
from pathlib import Path
import ssl
import urllib.error
import urllib.parse
import urllib.request

AI_URL = 'https://ai220.m84.us/v1/chat/completions'


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
