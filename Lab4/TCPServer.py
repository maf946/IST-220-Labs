import socket

def get_ip_address():
	s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	s.connect(("8.8.8.8", 80))
	return s.getsockname()[0]
	
serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
serverSocket.bind(('', 0))

serverIP = get_ip_address()
serverPort = serverSocket.getsockname()[1]

serverSocket.listen(1)

print ("serverIP: " + serverIP)
print ("serverPort:     " + str(serverPort))
print ("Press Ctrl+Z to quit. Listening...")

while 1:
	connectionSocket, addr = serverSocket.accept()
	clientIP = str(addr[0])
	clientPort = str(addr[1])
	message = connectionSocket.recv(1024).decode()
	if message:
		print ("Received from " + clientIP + "#" + clientPort + ": " + message)
		modifiedMessage = message.upper()
		connectionSocket.send(modifiedMessage.encode())
		connectionSocket.close()
