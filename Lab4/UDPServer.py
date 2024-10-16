import socket
import random

def scramble_word(word):
    """
    Scrambles all characters of a word completely.
    """
    word_list = list(word)
    random.shuffle(word_list)
    return ''.join(word_list)

def scramble_text(text):
    """
    Scrambles the letters of each word in the text.
    """
    return ' '.join(scramble_word(word) for word in text.split())

def get_ip_address():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        return s.getsockname()[0]
    finally:
        s.close()

def main():
    serverSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    serverSocket.bind(('', 0))
    serverIP = get_ip_address()
    serverPort = serverSocket.getsockname()[1]
    print(f"Server IP:\t{serverIP}")
    print(f"Server Port:\t{serverPort}")
    print("Press Ctrl+C to quit. Listening...")

    try:
        while True:
            message, clientAddress = serverSocket.recvfrom(2048)
            if message:
                clientIP, clientPort = clientAddress
                print(f"Received from {clientIP}#{clientPort}: {message.decode()}")
                modifiedMessage = scramble_text(message.decode())
                serverSocket.sendto(modifiedMessage.encode(), clientAddress)
    except KeyboardInterrupt:
        print("\nServer shutdown gracefully.")
    except socket.error as err:
        print(f"Server error: {err}")
    finally:
        serverSocket.close()

if __name__ == "__main__":
    main()