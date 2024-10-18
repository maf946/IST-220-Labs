# Instructions for Lab 4 (Python Socket Scripts)

Create your own Lab 4 Report document in Microsoft Word, and clearly label your answers for each of the questions defined below.

By the end of this lab, you’ll be able to:

* Develop a greater understanding for how packets use sockets and ports to communicate with arbitrary devices
* Learn how to use Nmap for port scanning


## Section 1: Study Operation of UDP/TCP Client and Server

For this lab, you’ll be using four primary Python scripts:



1. [UDPServer.py](https://github.com/maf946/IST-220-Labs/blob/main/Lab4/UDPServer.py)
2. [UDPClient.py](https://github.com/maf946/IST-220-Labs/blob/main/Lab4/UDPClient.py)
3. [TCPServer.py](https://github.com/maf946/IST-220-Labs/blob/main/Lab4/TCPServer.py) 
4. [TCPClient.py](https://github.com/maf946/IST-220-Labs/blob/main/Lab4/TCPClient.py) 

For this lab, you’ll be creating **four** PyCharm projects. Each project will have a main.py file. My suggestion is that you create the projects as follows:

1. A project called UDPServer. Replace the contents of main.py with the contents of UDPServer.py.
2. A project called UDPClient. Replace the contents of main.py with the contents of UDPClient.py. When prompted, I suggest opening the project in a New Window.
3. A project called TCPServer. Replace the contents of main.py with the contents of TCPServer.py. When prompted, I suggest opening the project in a New Window.
4. A project called TCPClient. Replace the contents of main.py with the contents of TCPClient.py. When prompted, I suggest opening the project in a New Window.

## Section 2: Inspecting UDP Traffic Through Wireshark

As seen in the last few labs, Wireshark will listen and document hundreds of different networking protocols. So far, we’ve seen HTTP and DNS, but in this lab, we will be focusing on the TCP and UDP packets that are being exchanged between the client and the server. 

In this section, you’ll be launching Wireshark, then running UDPClient.py and UDPServer.py. 

**Step 1:** Launch Wireshark.

**Step 2**: Start sniffing the **loopback/lo0** interface.

**Step 3**: Run the UDPServer project in PyCharm. Keep it running. Make a note of the serverIP and serverPort values visible in the “Run” portion of the PyCharm window, as in the screenshot below:

![alt_text](https://github.com/maf946/IST-220-Labs/blob/main/Lab4/Images/ServerIPandPortOutput.png?raw=true)

**Step 4**: While the UDPServer is still running, switch over to the UDPClient project in PyCharm. Replace the values for serverIP and serverPort in the source code with the values from the UDPServer. Make sure to keep the serverIP value in double quotes. Run the UDPClient, and send a message from the client to the server. You should receive a response in upper-case, as in the screenshot below:

![alt_text](https://github.com/maf946/IST-220-Labs/blob/main/Lab4/Images/UDPServerResponse.png?raw=true)


**Question 1**: Post a screenshot of the “Run” area in PyCharm for both UDPServer and UDPClient, after you have successfully sent a message between the two.

**Step 5**: Stop your Wireshark capture. Next, in Wireshark, identify the UDP packet(s) containing the message you sent in the prior step (i.e., the lowercase text). Right-click one of the two packets, and select Follow, then UDP Stream. Take a screenshot of the resulting Wireshark window.

**Question 2**: Post the screenshot described above.

## Section 3: TCP Port Scanning with a Friend

In this section, you’ll be working with a friend (or at least a classmate… somebody other than yourself). You’ll use a port scan to find the TCP server on your friend’s machine, then connect to it. (And the friend will do the same, vice-versa; this lab is still an individual assignment).

First, some table stakes:

* We’ll be using the **nmap** port scanner. Make sure to read the following overview: [What is Nmap and How to Use It](https://www.freecodecamp.org/news/what-is-nmap-and-how-to-use-it-a-tutorial-for-the-greatest-scanning-tool-of-all-time/).
* Now that you’re trained in the art and science of nmap, it’s safe for you to install it. Go ahead and install it:
	* If you're on the Mac, [download nmap](https://nmap.org/download.html#macosx), run the installer by right-clicking it and selecting "Open", and then use nmap from the terminal.
	* If you're on Windows, either:
		* (easier) run `choco install nmap` in a Command Prompt or PowerShell window with administrator privileges
   		* [download nmap](https://nmap.org/download.html#windows), run the installer, and install both nmap and Npcap. You can uncheck the box asking if you want to create a shortcut on your desktop.


### When you’re acting as the server…

Follow one of the two subsections below.

##### If you and your partner are both connected to the PSU Wi-Fi network

Great, everything should work fine.

##### If you and your partner are not both connected to the PSU Wi-Fi network

In this situation, things are a bit more complicated. Please let me know if this applies to you, and I'll walk you through a few different approaches to dealing with the problem.

<hr />

Provide your friend with the IPv4 address, but not the port number. Instead, make your friend earn it by giving them a range of 100 port numbers around the port number.[^1] For example:

TCPServer.py port | Range to tell your friend 
------ | ------
22434  | 22400-22499    
23569  | 23500-23599   
25121  | 25100-25199      

Keep your TCP server running for the remainder of the exercise. 

### When you’re acting as the client…

**Phase 1**: Your friend is being a real pain and is not giving you a specific port number[^2], so you’ll need to snoop/scan around and find the open port in the range provided. nmap seems like it would be handy here, so let’s use that.

Observe the following example usages:

OS | Command
-----|-----
macOS (run in Terminal) | `sudo nmap 159.203.126.35 -sS -p 22400-22499`
Windows (run in Command Prompt as administrator; see more instructions below) | `nmap 159.203.126.35 -sS -p 22400-22499`

	Windows Users: Opening the Command Prompt as Administrator
	
	1. Press the Windows Start button at the bottom left.
	2. Type in "Command Prompt".
	3. Right click on Command Prompt and click "Run as administrator".
	4. Click Yes if the User Account Control prompt is displayed.

Run that command, replacing the IP address and port range as appropriate. The -sS option means you would like to run a stealth scan; a more detailed explanation of what this means is [available from the official nmap site](https://nmap.org/book/synscan.html).

It may take a few seconds, but before long you should see output which will tell you the open port, and you should see a result like the below. You want to find ports where the STATE is “open.” There may be several in the range (as in the screenshot), but one of them will be your friend’s. You may have to try each of them until you succeed.

![nmap output](https://github.com/maf946/IST-220-Labs/blob/main/Lab4/Images/nmap.png?raw=true)

**Question 3**: Post a screenshot of the nmap command and output. Also include the full name and Penn State email address of the friend who was acting as the server.

**Phase 2**: Now that you’ve found out how to sneak in to your very rude friend’s server, it’s time to go ahead and do that

**Step 1:** In Wireshark, start a capture on your primary interface (not the loopback interface).

**Step 2:** Use the TCP client to connect to the TCP server on the appropriate port. You’ll need to modify the serverIP and serverPort values appropriately. 

**Step 3**: Send a message to the server, and observe the result coming back. You should see a result like the below:

![TCP Remote Client](https://raw.githubusercontent.com/maf946/IST-220-Labs/refs/heads/main/Lab4/Images/TCPRemoteClient.png)

**Step 4:** Stop the Wireshark capture. Locate any of the packets corresponding to the TCP connection described here, and right-click it. Select “Follow,” then “TCP Stream.” A new window will open, which is mostly a large text area with encrypted text. 

A tip for finding one of the TCP packets: In Wireshark, select "Edit" at the top of the screen, then "Find Packet…". Change the first pulldown to "Packet bytes" and the third to "String," as shown in the image below. Enter a search term that you know will be found, i.e., one of the words from the message that you sent in lower/upper case, and then hit "Find."

![Using Find Packet…](https://raw.githubusercontent.com/maf946/IST-220-Labs/main/Lab4/Images/findPacket.png)

**Step 5:** Close the new window, and observe that the Wireshark filter is set to a particular TCP stream (ex: “tcp.stream eq 0”). Based on what you now know about the TCP segment structure, explore this list of 10 or so packets.

**Question 4**: Post a screenshot of the Wireshark window with the appropriate filter set. In a well-written paragraph, explain what is happening across the course of the TCP stream. Hint: not all of the packets are for transporting the message you typed into the terminal. There is a lot of other plumbing that is happening behind the scenes, and which is now exposed to you in Wireshark.

[^1]:
     Perhaps this is why I do not have more friends.

[^2]:
     You should find some new friends who really honor port transparency.
