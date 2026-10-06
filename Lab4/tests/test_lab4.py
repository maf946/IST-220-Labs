import concurrent.futures
import http.server
import json
from pathlib import Path
import socket
import subprocess
import sys
import threading
import unittest
from unittest.mock import patch

LAB = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(LAB))
import lab4_common as lab


class ProtocolTests(unittest.TestCase):
    def test_fragmented_tcp_message(self):
        reader, writer = socket.socketpair()
        with reader, writer:
            def send():
                writer.sendall(b'{"name":')
                writer.sendall(b'"Alex"}\n')
            thread = threading.Thread(target=send)
            thread.start()
            self.assertEqual(lab.receive_line(reader), b'{"name":"Alex"}')
            thread.join()

    def test_empty_scan_connection(self):
        reader, writer = socket.socketpair()
        writer.close()
        with reader:
            self.assertIsNone(lab.receive_line(reader))

    def test_response_size_and_unicode(self):
        request = {'request_id': 'abc', 'name': 'Alex', 'hobby': 'painting'}
        with patch.object(lab, 'ask_ai', return_value=('🌟\n' * 1000, {})):
            raw = lab.reply_for(lab.encode(request), ('unused', 'SECRET', 'unused'))
        result = json.loads(raw)
        self.assertLessEqual(len(raw), 1200)
        self.assertTrue(result['truncated'])
        self.assertNotIn(b'SECRET', raw)

    def test_invalid_request_does_not_call_ai(self):
        with patch.object(lab, 'ask_ai') as ask:
            for data in (b'not json', b'[]', b'{}', b'\xff', b'x' * 4097):
                self.assertFalse(json.loads(lab.reply_for(data, None))['ok'])
            ask.assert_not_called()


class IntegrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.calls = []
        class Handler(http.server.BaseHTTPRequestHandler):
            def do_POST(self):
                body = json.loads(self.rfile.read(int(self.headers['Content-Length'])))
                cls.calls.append((self.headers.get('Authorization'), body))
                if self.headers.get('Authorization') != 'Bearer TEST-KEY':
                    self.send_error(401)
                    return
                payload = lab.encode({'choices': [{'message': {'content': 'Alex enjoys stargazing.\nA poem arrives.'}}], 'usage': {'completion_tokens': 10}})
                self.send_response(200)
                self.send_header('Content-Length', str(len(payload)))
                self.end_headers()
                self.wfile.write(payload)
            def log_message(self, *args):
                pass
        cls.http = http.server.ThreadingHTTPServer(('127.0.0.1', 0), Handler)
        cls.thread = threading.Thread(target=cls.http.serve_forever)
        cls.thread.start()
        cls.url = f'http://127.0.0.1:{cls.http.server_port}/v1/chat/completions'

    @classmethod
    def tearDownClass(cls):
        cls.http.shutdown()
        cls.http.server_close()
        cls.thread.join()

    def test_authentication_error(self):
        with self.assertRaisesRegex(ValueError, 'rejected the class key'):
            lab.ask_ai('Alex', 'painting', (self.url, 'wrong', 'test'))

    def test_both_real_servers_and_clients(self):
        import os
        import queue
        env = dict(os.environ, IST220_AI_KEY='TEST-KEY', IST220_AI_URL=self.url)
        for protocol in ('TCP', 'UDP'):
            with self.subTest(protocol=protocol):
                server = subprocess.Popen([sys.executable, '-u', str(LAB / f'{protocol}Server.py')], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, env=env)
                lines = queue.Queue()
                reader = threading.Thread(target=lambda: [lines.put(line) for line in server.stdout], daemon=True)
                reader.start()
                try:
                    first = lines.get(timeout=5)
                    self.assertTrue(first.startswith('Port: '), first)
                    port = int(first.split(':')[1])
                    if protocol == 'TCP':
                        with socket.create_connection(('127.0.0.1', port), timeout=2):
                            pass
                    result = subprocess.run([sys.executable, str(LAB / f'{protocol}Client.py')], input=f'127.0.0.1\n{port}\nAlex\nstargazing\n', capture_output=True, text=True, env=env, timeout=10)
                    self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                    self.assertIn('A poem arrives.', result.stdout)
                    self.assertNotIn('TEST-KEY', result.stdout)
                finally:
                    server.terminate()
                    server.wait(timeout=5)
                    reader.join(timeout=2)
                    server.stdout.close()

    def test_load_test(self):
        import os
        env = dict(os.environ, IST220_AI_KEY='TEST-KEY', IST220_AI_URL=self.url)
        result = subprocess.run([sys.executable, str(LAB / 'InstructorLoadTest.py')], capture_output=True, text=True, env=env, timeout=10)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn('Completed: 3/3', result.stdout)
        self.assertNotIn('TEST-KEY', result.stdout)


if __name__ == '__main__':
    unittest.main()
