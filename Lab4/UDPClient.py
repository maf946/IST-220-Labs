import socket

serverIP = "127.0.0.1" #replace this number
serverPort = 5000 #replace this number

print("I'm configured to send UDP packets to " + serverIP + " on port " + str(serverPort))
print ("Press Ctrl+Z to quit.")

while 1:	
	clientSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)		
	message = input("Input lowercase text: ")
	clientSocket.sendto(message.encode(), (serverIP, serverPort))
	modifiedMessage, serverAddress = clientSocket.recvfrom(2048)
	print ("Returned from server: " + modifiedMessage.decode())
	clientSocket.close()