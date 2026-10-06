"""Run three simultaneous poem requests; never prints the class key."""
import concurrent.futures
import os
from pathlib import Path
import time
from lab4_common import ask_ai, settings


def main():
    key_file = Path.home() / 'llama-local/class-api-key.txt'
    if not os.environ.get('IST220_AI_KEY') and key_file.exists():
        os.environ['IST220_AI_KEY'] = key_file.read_text().strip()
    config = settings()

    def request(name):
        started = time.monotonic()
        try:
            poem, result = ask_ai(name, 'stargazing', config)
            return name, True, time.monotonic() - started, f"HTTP 200; {result.get('usage', {}).get('completion_tokens', '?')} tokens\n{poem}"
        except ValueError as error:
            return name, False, time.monotonic() - started, str(error)

    started = time.monotonic()
    successes = 0
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
        futures = [pool.submit(request, name) for name in ('Marc', 'Alex', 'Jordan')]
        for future in concurrent.futures.as_completed(futures):
            name, success, seconds, detail = future.result()
            successes += success
            print(f'\n{name}: {seconds:.1f} seconds — {detail}', flush=True)
    print(f'\nCompleted: {successes}/3; elapsed: {time.monotonic() - started:.1f} seconds')
    return 0 if successes == 3 else 1


if __name__ == '__main__':
    raise SystemExit(main())
