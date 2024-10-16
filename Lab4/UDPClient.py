import socket

serverIP = "192.168.0.19" #replace this number
serverPort = 54667 #replace this number

print("I'm configured to send UDP packets to " + serverIP + " on port " + str(serverPort))
print ("Press Ctrl+C to quit.")

while 1:	
	clientSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)		
	message = input("Input text to scramble: ")
	clientSocket.sendto(message.encode(), (serverIP, serverPort))
	modifiedMessage, serverAddress = clientSocket.recvfrom(2048)
	print ("Returned from server: " + modifiedMessage.decode())
	clientSocket.close()
