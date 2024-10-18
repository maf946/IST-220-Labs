#!/usr/bin/env python
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
    serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    serverSocket.bind(('', 0))
    serverIP = get_ip_address()
    serverPort = serverSocket.getsockname()[1]
    serverSocket.listen(1)
    print(f"Server IP: {serverIP}")
    print(f"Server Port: {serverPort}")
    print("Listening...")
    
    try:
        while True:
            try:
                connectionSocket, addr = serverSocket.accept()
                clientIP, clientPort = addr
                print(f"Connected to {clientIP}#{clientPort}")
                
                with connectionSocket:
                    message = connectionSocket.recv(1024).decode()
                    if message:
                        print(f"Received from {clientIP}#{clientPort}: {message}")
                        modifiedMessage = scramble_text(message)
                        connectionSocket.send(modifiedMessage.encode())
            except Exception as e:
                print(f"Error handling connection: {e}")
    except KeyboardInterrupt:
        print("\nServer shutdown gracefully.")
    except socket.error as err:
        print(f"Server error: {err}")
    finally:
        serverSocket.close()

if __name__ == "__main__":
    main()