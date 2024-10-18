#! /opt/homebrew/bin/python3.11 

import socket

serverIP = "104.39.114.91"  # replace this number; keep the quotes
serverPort = 58504  # replace this number; do not add quotes

print("I'm configured to send TCP packets to " + serverIP + " on port " + str(serverPort))
print ("Press Ctrl+C to quit.")

while True:
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
            client_socket.settimeout(5)
            client_socket.connect((serverIP, serverPort))
            message = input("Input text to scramble: ")
            if message.lower() == 'quit':
                break
            try:
                client_socket.send(message.encode())
                modified_message = client_socket.recv(1024).decode()
                print("Returned from server:", modified_message)
            except socket.timeout:
                print("Request timed out")
    except socket.error as e:
        print("Error:", e)
