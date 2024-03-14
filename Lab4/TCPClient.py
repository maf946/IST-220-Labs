import socket

serverIP = "104.39.31.51"  # replace this number; keep the quotes
serverPort = 64998  # replace this number; do not add quotes

while True:
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
            client_socket.settimeout(5)
            client_socket.connect((serverIP, serverPort))
            message = input("Input lowercase text (type 'quit' to exit): ")
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
