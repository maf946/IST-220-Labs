"""Keep this server running while your client or partner connects."""
from lab4_common import main, run_server

if __name__ == '__main__':
    main(run_server, 'UDP')
