import socket

serverIP = "127.0.0.1" #replace this number
serverPort = 5000 #replace this number

print("I'm configured to send TCP packets to " + serverIP + " on port " + str(serverPort))
print ("Press Ctrl+Z to quit.")

while 1:
	clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	clientSocket.connect((serverIP, serverPort))
	message = input("Input lowercase text: ")
	clientSocket.send(message.encode())
	modifiedMessage = clientSocket.recv(1024)
	print("Returned from server: " + modifiedMessage.decode())
	clientSocket.close()