## Socket Programming: Creating Network Applications

*Note: This document is based heavily on Chapter 2.7 of our textbook. I have updated it to provide some new features, as well as compatibility with the latest version of Python, but the principles are the same as those in the textbook.*

Now that we’ve looked at a number of important network applications, let’s explore how network application programs are actually created. Recall from Section 2.1 that a typical network application consists of a pair of programs—a client program and a server program—residing in two different end systems. When these two programs are executed, a client process and a server process are created, and these processes communicate with each other by reading from, and writing to, sockets. When creating a network application, the developer’s main task is therefore to write the code for both the client and server programs.

There are two types of network applications. One type is an implementation whose operation is specified in a protocol standard, such as an RFC or some other standards document; such an application is sometimes referred to as “open,” since the rules specifying its operation are known to all. For such an implementation, the client and server programs must conform to the rules dictated by the RFC. For example, the client program could be an implementation of the client side of the HTTP protocol, described in Section 2.2 and precisely defined in RFC 2616; similarly, the server program could be an implementation of the HTTP server protocol, also precisely defined in RFC 2616. If one developer writes code for the client program and another developer writes code for the server program, and both developers carefully follow the rules of the RFC, then the two programs will be able to interoperate. Indeed, many of today’s network applications involve communication between client and server programs that have been created by independent developers—for example, a Google Chrome browser communicating with an Apache Web server, or a BitTorrent client communicating with BitTorrent tracker.

The other type of network application is a proprietary network application. In this case the client and server programs employ an application-layer protocol that has not been openly published in an RFC or elsewhere. A single developer (or development team) creates both the client and server programs, and the developer has complete control over what goes in the code. But because the code does not implement an open protocol, other independent developers will not be able to develop code that interoperates with the application.

In this section, we’ll examine the key issues in developing a client-server application, and we’ll “get our hands dirty” by looking at code that implements a very simple client-server application. During the development phase, one of the first decisions the developer must make is whether the application is to run over TCP or over UDP. Recall that TCP is connection oriented and provides a reliable byte-stream channel through which data flows between two end systems. UDP is connectionless and sends independent packets of data from one end system to the other, without any guarantees about delivery. Recall also that when a client or server program implements a protocol defined by an RFC, it should use the well-known port number associated with the protocol; conversely, when developing a proprietary application, the developer must be careful to avoid using such well-known port numbers. (Port numbers were briefly discussed in Section 2.1. They are covered in more detail in Chapter 3.)

We introduce UDP and TCP socket programming by way of a simple UDP application and a simple TCP application. We present the simple UDP and TCP applications in Python 3. We could have written the code in Java, C, or C++, but we chose Python mostly because Python clearly exposes the key socket concepts. With Python there are fewer lines of code, and each line can be explained to the novice programmer without difficulty. But there’s no need to be frightened if you are not familiar with Python. You should be able to easily follow the code if you have experience programming in Java, C, or C++.

If you are interested in client-server programming with Java, you are encouraged to see the Companion Website for this textbook; in fact, you can find there all the examples in this section (and associated labs) in Java. For readers who are interested in client-server programming in C, there are several good references available [Donahoo 2001; Stevens 1997; Frost 1994; Kurose 1996]; our Python examples below have a similar look and feel to C.

### Socket Programming with UDP

In this subsection, we’ll write simple client-server programs that use UDP; in the following section, we’ll write similar programs that use TCP.

Recall from Section 2.1 that processes running on different machines communicate with each other by sending messages into sockets. We said that each process is analogous to a house and the process’s socket is analogous to a door. The application resides on one side of the door in the house; the transport-layer protocol resides on the other side of the door in the outside world. The application developer has control of everything on the application-layer side of the socket; however, it has little control of the transport-layer side.

Now let’s take a closer look at the interaction between two communicating processes that use UDP sockets. Before the sending process can push a packet of data out the socket door, when using UDP, it must first attach a destination address to the packet. After the packet passes through the sender’s socket, the Internet will use this destination address to route the packet through the Internet to the socket in the receiving process. When the packet arrives at the receiving socket, the receiving process will retrieve the packet through the socket, and then inspect the packet’s contents and take appropriate action.

So you may be now wondering, what goes into the destination address that is attached to the packet? As you might expect, the destination host’s IP address is part of the destination address. By including the destination IP address in the packet, the routers in the Internet will be able to route the packet through the Internet to the destination host. But because a host may be running many network application processes, each with one or more sockets, it is also necessary to identify the particular socket in the destination host. When a socket is created, an identifier, called a port number, is assigned to it. So, as you might expect, the packet’s destination address also includes the socket’s port number. In summary, the sending process attaches to the packet a destination address, which consists of the destination host’s IP address and the destination socket’s port number. Moreover, as we shall soon see, the sender’s source address—consisting of the IP address of the source host and the port number of the source socket—are also attached to the packet. However, attaching the source address to the packet is typically not done by the UDP application code; instead it is automatically done by the underlying operating system.

We’ll use the following simple client-server application to demonstrate socket programming for both UDP and TCP:

1. The client reads a line of characters (data) from its keyboard and sends the data to the server.
2. The server receives the data and converts the characters to uppercase.
3. The server sends the modified data to the client.
4. The client receives the modified data and displays the line on its screen.

**Figure 1** highlights the main socket-related activity of the client and server that communicate over the UDP transport service.

![Figure 1: The client-server application using UDP](https://github.com/maf946/SocketScripts/blob/master/Figure1.png)

Now let’s get our hands dirty and take a look at the client-server program pair for a UDP implementation of this simple application. We also provide a detailed, line-by-line analysis after each program. We’ll begin with the UDP client, which will send a simple application-level message to the server. In order for the server to be able to receive and reply to the client’s message, it must be ready and running—that is, it must be running as a process before the client sends its message.

The client program is called UDPClient.py, and the server program is called UDPServer.py. In order to emphasize the key issues, we intentionally provide code that is minimal. “Good code” would certainly have a few more auxiliary lines, in particular for handling error cases. For this application, the server port number will be automatically selected each time the server is started.

#### Interaction Model

We will run the client and server as follows.

Create a PyCharm project and replace main.py with the code from UDPServer.py. You should see something like the following as the output (you will almost certainly have a different IP address and port number):

	serverIP: 		192.168.0.118
	serverPort: 	49957
	Press Ctrl+Z to quit. Listening...
	
Make note of the serverIP and serverPort values.

Next, create a second PyCharm project (I suggest opening it in a new window) for the UDP client; alternatively, work with a friend or classmate and have them run this on their machine, instead. This is designed to work on the Internet so any two Internet-connected machines should work!

In the UDPClient.py source, make sure to replace the serverIP and serverPort values at the top with the values from UDPServer.py. You should see something like the following as the output:

	I'm configured to send UDP packets to 192.168.0.118 on port 49957
	Press Ctrl+Z to quit.
	Input lowercase text: 

Once you enter some lowercase text, such as "udp is lazy", press Return and you should see the following outputs:

From the client side: 

	Returned from server: UDP IS LAZY
	Input lowercase text: 
	
From the server side:

	Received from 192.168.67.1#56855: udp is lazy

You can continue to run the client and server for as long as you wish. Press Ctrl+Z to quit either one.

#### UDPClient.py

Now let’s take a look at the various lines of code in UDPClient.py.

	import socket

The socket module forms the basis of all network communications in Python. By including this line, we will be able to create sockets within our program. 

	serverIP = "127.0.0.1" #replace this number
	serverPort = 5000 #replace this number

These lines will be used to create the socket.

	print("I'm configured to send UDP packets to " + str(serverIP) + " on port " + serverPort)
	print ("Press Ctrl+Z to quit.")
	
Print messages to the user. Note that we use the `str()` function to convert the serverPort value to be a string, rather than an integer (earlier, we specified that the port number must be an integer; we do not want to specify that for the IP address, since it contains `.` characters, which are not integers).

	while 1:
	
This line, and everything below it which is indented by a tab, is part of an infinite loop. Once the client is configured correctly, we want to continually prompt the user for input, then communicate over the network (recall that the user can quit by pressing Ctrl+Z, or just closing PyCharm). Note that **indentation in Python is very important**. Use tab characters with care, when warranted, and only when warranted.

		clientSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)	

This line creates the client’s socket, called `clientSocket`. The first parameter indicates the address family; in particular, `AF_INET` indicates that the underlying network is using IPv4. (Do not worry about this now; we will discuss IPv4 in Chapter 4.) The second parameter indicates that the socket is of type `SOCK_DGRAM`, which means it is a UDP socket (rather than a TCP socket). Note that we are not specifying the port number of the client socket when we create it; we are instead letting the operating system do this for us. Now that the client process’s door has been created, we will want to create a message to send through the door.

		message = input("Input lowercase text: ")
		
`input()` is a built-in function in Python. When this command is executed, the user at the client is prompted with the words “Input lowercase text: ” The user then uses her keyboard to input a line, which is put into the variable `message`. Now that we have a socket and a message, we will want to send the message through the socket to the destination host.

		clientSocket.sendto(message.encode(), (serverIP, serverPort))

In the above line, we first convert the message from string type to byte type, as we need to send bytes into a socket; this is done with the `encode()` method. The method `sendto()` attaches the destination address (`serverName`, `serverPort`) to the message and sends the resulting packet into the process’s socket, `clientSocket`. (As mentioned earlier, the source address is also attached to the packet, although this is done automatically rather than explicitly by the code.) Sending a client-to-server message via a UDP socket is that simple! After sending the packet, the client waits to receive data from the server.

		modifiedMessage, serverAddress = clientSocket.recvfrom(2048)
		
With the above line, when a packet arrives from the Internet at the client’s socket, the packet’s data is put into the variable `modifiedMessage` and the packet’s source address is put into the variable `serverAddress`. The variable `serverAddress` contains both the server’s IP address and the server’s port number. The program UDPClient doesn’t actually need this server address information, since it already knows the server address from the outset; but this line of Python provides the server address nevertheless. The method `recvfrom` also takes the buffer size 2048 as input. (This buffer size works for most purposes.)

		print ("Returned from server: " + modifiedMessage.decode())
		
This line prints out the text "Returned from server: " and then `modifiedMessage` on the user’s display, after converting the message from bytes to string. It should be the original line that the user typed, but now capitalized. 

		clientSocket.close()
		
This line closes the socket. Since we are at the end of the `while 1:` block, we will loop back up to the top and create a new `clientSocket`. Thus, a new socket is being created each time the user enters input into UDPClient.py.

#### UDPServer.py

Let’s now take a look at the server side of the application. As with UDPClient.py, we begin by importing the socket module.

		def get_ip_address():
			s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
			s.connect(("8.8.8.8", 80))
			return s.getsockname()[0]

These lines of code create a new function, `get_ip_address`, which returns the IP address of the machine on which the server is running (in other words, its own IP address). There are a few ways to do this in Python, but for reasons somewhat outside the scope of our concern right now, this is a good way to do it. Don't worry about the details here; just know that we will use the `get_ip_address` function later, so that we can print out the IP address to the terminal.

	serverSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

Just as with UDPClient.py, this creates a socket of type SOCK_DGRAM (a UDP socket). 

	serverSocket.bind(('', 0))

The above line binds (that is, assigns) the port number to the server’s socket. We could have selected a specific port number (in the same way that the designers of HTTP picked the number 80) and hard-coded it here. However, for our purposes it's better to just randomly select an available port number on the server machine. By specifying a port of 0, we're inviting the operating system to do that for us. Suppose that port 49957 is selected; when anyone sends a packet to port 49957 at the IP address of the server, that packet will be directed to this socket. 

	serverIP = get_ip_address()
	serverPort = serverSocket.getsockname()[1]

We need to know the server's IP address, as well as the port number we just selected. `serverIP` is set based on the value returned from the `get_ip_address()` function, while `serverPort` is set based on inspecting the `serverSocket` we created just a few lines above.

	print ("serverIP:\t" + serverIP)
	print ("serverPort:\t" + str(serverPort))
	print ("Press Ctrl+Z to quit. Listening...")
	
Display useful information to the user; the `\t` symbol inserts a `tab` character, to help line the values up nicely. Note that the prompt says "Listening..."; this server will run indefinitely, based on the `while 1:` loop we will create next. 

	while 1: 

UDPServer.py is going to do what servers do: sit around, run (hopefully) indefinitely, and wait for clients to connect. In the while loop, UDPServer waits for a packet to arrive.

		message, clientAddress = serverSocket.recvfrom(2048)
	
This line of code is similar to what we saw in UDPClient. When a packet arrives at the server’s socket, the packet’s data is put into the variable `message` and the packet’s source address is put into the variable clientAddress. The variable `clientAddress` contains both the client’s IP address and the client’s port number. Here, UDPServer _will_ make use of this address information, as it provides a return address, similar to the return address with ordinary postal mail. With this source address information, the server now knows to where it should direct its reply.

		if message: 
		
Sometimes we may receive a "blank" message, such as if a user sends a blank message, or if a port-scanning tool like `nmap` is scanning for open ports by sending 0-length packets. The `if` line here checks if the message is _not_ empty; as long as it's not empty, all of the lines that are below it and indented (i.e., the rest of the script), will run. Otherwise, it just loops back to the top of the `while` block.

			clientIP = str(clientAddress[0])
			clientPort = str(clientAddress[1])

These lines aren't strictly necessary in order to send a reply packet, but we're including them here because it will be nice for us to be able to print the `clientIP` and `clientPort` values to the terminal window. Here, we are extracting those two parts from the `clientAddress` array, converting them to strings, and storing them in new variables.

			print ("Received from " + clientIP + "#" + clientPort + ": " + message.decode())
		
Again, it's not strictly necessary, but it's nice to be able to show a "server log" of what is being sent to the server, and from where. An example of the output from this line is `Received from 192.168.67.1#56855: udp is lazy`. The `#` sign is used by convention as a separator between the IP address and port number. We need to use the `.decode()` function to convert the arriving message to a string.

			modifiedMessage = message.upper()

This line is the heart of our simple application. It takes the line sent by the client and, after converting the message to a string, uses the method upper() to capitalize it.

			serverSocket.sendto(modifiedMessage, clientAddress)

This last line attaches the client’s address (IP address and port number) to the capitalized message and sends the resulting packet into the server’s socket. (As mentioned earlier, the server address is also attached to the packet, although this is done automatically rather than explicitly by the code.) The Internet will then deliver the packet to this client address. After the server sends the packet, it remains in the while loop, waiting for another UDP packet to arrive (from any client running on any host).

### Socket Programming with TCP

Unlike UDP, TCP is a connection-oriented protocol. This means that before the client and server can start to send data to each other, they first need to handshake and establish a TCP connection. One end of the TCP connection is attached to the client socket and the other end is attached to a server socket. When creating the TCP connection, we associate with it the client socket address (IP address and port number) and the server socket address (IP address and port number). With the TCP connection established, when one side wants to send data to the other side, it just drops the data into the TCP connection via its socket. This is different from UDP, for which the server must attach a destination address to the packet before dropping it into the socket.

Now let’s take a closer look at the interaction of client and server programs in TCP. The client has the job of initiating contact with the server. In order for the server to be able to react to the client’s initial contact, the server has to be ready. This implies two things. First, as in the case of UDP, the TCP server must be running as a process before the client attempts to initiate contact. Second, the server program must have a special door—more precisely, a special socket—that welcomes some initial contact from a client process running on an arbitrary host. Using our house/door analogy for a process/socket, we will sometimes refer to the client’s initial contact as “knocking on the welcoming door.”

With the server process running, the client process can initiate a TCP connection to the server. This is done in the client program by creating a TCP socket. When the client creates its TCP socket, it specifies the address of the welcoming socket in the server, namely, the IP address of the server host and the port number of the socket. After creating its socket, the client initiates a three-way handshake and establishes a TCP connection with the server. The three-way handshake, which takes place within the transport layer, is completely invisible to the client and server programs.

During the three-way handshake, the client process knocks on the welcoming door of the server process. When the server “hears” the knocking, it creates a new door—more precisely, a new socket that is dedicated to that particular client. In our example below, the welcoming door is a TCP socket object that we call `serverSocket`; the newly created socket dedicated to the client making the connection is called `connectionSocket`. Students who are encountering TCP sockets for the first time sometimes confuse the welcoming socket (which is the initial point of contact for all clients wanting to communicate with the server), and each newly created server-side connection socket that is subsequently created for communicating with each client.

From the application’s perspective, the client’s socket and the server’s connection socket are directly connected by a pipe. As shown in Figure 2, the client process can send arbitrary bytes into its socket, and TCP guarantees that the server process will receive (through the connection socket) each byte in the order sent. TCP thus provides a reliable service between the client and server processes. Furthermore, just as people can go in and out the same door, the client process not only sends bytes into but also receives bytes from its socket; similarly, the server process not only receives bytes from but also sends bytes into its connection socket.

![Figure 2: The TCPServer process has two sockets](https://github.com/maf946/SocketScripts/blob/master/Figure2.png)

We use the same simple client-server application to demonstrate socket programming with TCP: The client sends one line of data to the server, the server capitalizes the line and sends it back to the client. Figure 3 highlights the main socket-related activity of the client and server that communicate over the TCP transport service.

![Figure 3: The client-server application using TCP](https://github.com/maf946/SocketScripts/blob/master/Figure3.png)

#### TCPClient.py

Let’s now take a look at the various lines in the code that differ significantly from the UDP implementation. The first such line is the creation of the client socket.

		clientSocket = socket(AF_INET, SOCK_STREAM)

This line creates the client’s socket, called `clientSocket`. The first parameter again indicates that the underlying network is using IPv4. The second parameter indicates that the socket is of type `SOCK_STREAM`, which means it is a TCP socket (rather than a UDP socket). Note that we are again not specifying the port number of the client socket when we create it; we are instead letting the operating system do this for us. Now the next line of code is very different from what we saw in UDPClient:

		clientSocket.connect((serverIP, serverPort))
		
Recall that before the client can send data to the server (or vice versa) using a TCP socket, a TCP connection must first be established between the client and server. The above line initiates the TCP connection between the client and server. The parameter of the `connect()` method is the address of the server side of the connection. After this line of code is executed, the three-way handshake is performed and a TCP connection is established between the client and server.

		message = input("Input lowercase text: ")
		clientSocket.send(message.encode())

The first line, as before, prompts the user for a message. The second line sends the `message` through the client’s socket and into the TCP connection. Note that the program does not explicitly create a packet and attach the destination address to the packet, as was the case with UDP sockets. Instead the client program simply drops the bytes in the string sentence into the TCP connection. The client then waits to receive bytes from the server.

		modifiedMessage = clientSocket.recv(1024)

When characters arrive from the server, they get placed into the string `modifiedMessage`. Characters continue to accumulate in modifiedMessage until the line ends with a carriage return character. After printing the capitalized message, we close the client’s socket:

		clientSocket.close()
		
This last line closes the socket and, hence, closes the TCP connection between the client and the server. It causes TCP in the client to send a TCP message to TCP in the server (see Section 3.5).

#### TCPServer.py

Now let's take a look at the server program.

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
		
Let’s now take a look at the lines that differ significantly from UDPServer and TCPClient. As with TCPClient, the server creates a TCP socket with:

	serverSocket=socket(AF_INET, SOCK_STREAM)	
	
Similar to UDPServer, we associate a randomly-selected port number with this socket:

	serverSocket.bind(('', 0))

But with TCP, serverSocket will be our welcoming socket. After establishing this welcoming door, we will wait and listen for some client to knock on the door:

	serverSocket.listen(1)	

This line has the server listen for TCP connection requests from the client. The parameter specifies the maximum number of queued connections (at least 1).

		connectionSocket, addr = serverSocket.accept()
	
When a client knocks on this door, the program invokes the `accept()` method for serverSocket, which creates a new socket in the server, called­`connectionSocket`, dedicated to this particular client. The client and server then complete the handshaking, creating a TCP connection between the client’s `clientSocket` and the server’s `connectionSocket`. With the TCP connection established, the client and server can now send bytes to each other over the connection. With TCP, all bytes sent from one side not are not only guaranteed to arrive at the other side but also guaranteed arrive in order.

		connectionSocket.close()

In this program, after sending the modified message to the client, we close the connection socket. But since `serverSocket` remains open, another client can now knock on the door and send the server a sentence to modify.