<!-----
NEW: Check the "Suppress top comment" option to remove this info from the output.

Conversion time: 2.655 seconds.


Using this Markdown file:

1. Paste this output into your source file.
2. See the notes and action items below regarding this conversion run.
3. Check the rendered output (headings, lists, code blocks, tables) for proper
   formatting and use a linkchecker before you publish this page.

Conversion notes:

* Docs to Markdown version 1.0β31
* Wed Oct 20 2021 06:50:47 GMT-0700 (PDT)
* Source doc: Instructions for Lab 4 (Python Socket Scripts)
* Tables are currently converted to HTML tables.
* This document has images: check for >>>>>  gd2md-html alert:  inline image link in generated source and store images to your server. NOTE: Images in exported zip file from Google Docs may not appear in  the same order as they do in your doc. Please check the images!

----->


<p style="color: red; font-weight: bold">>>>>>  gd2md-html alert:  ERRORs: 0; WARNINGs: 0; ALERTS: 5.</p>
<ul style="color: red; font-weight: bold"><li>See top comment block for details on ERRORs and WARNINGs. <li>In the converted Markdown or HTML, search for inline alerts that start with >>>>>  gd2md-html alert:  for specific instances that need correction.</ul>

<p style="color: red; font-weight: bold">Links to alert messages:</p><a href="#gdcalert1">alert1</a>
<a href="#gdcalert2">alert2</a>
<a href="#gdcalert3">alert3</a>
<a href="#gdcalert4">alert4</a>
<a href="#gdcalert5">alert5</a>

<p style="color: red; font-weight: bold">>>>>> PLEASE check and correct alert issues and delete this message and the inline alerts.<hr></p>



# Instructions for Lab 4 (Python Socket Scripts)

Create your own Lab 4 Report document in Microsoft Word, and clearly label your answers for each of the questions defined below.

By the end of this lab, you’ll be able to:



* Develop a greater understanding for how packets use sockets and ports to communicate with arbitrary devices
* Learn how to use Nmap for port scanning


## Section 1: Study Operation of UDP/TCP Client and Server

For this lab, you’ll be using four primary Python scripts:



1. UDPServer.py ([click to view](https://raw.githubusercontent.com/maf946/SocketScripts/master/UDPServer.py))
2. UDPClient.py ([click to view](https://raw.githubusercontent.com/maf946/SocketScripts/master/UDPClient.py))
3. TCPServer.py ([click to view](https://raw.githubusercontent.com/maf946/SocketScripts/master/TCPServer.py))
4. TCPClient.py ([click to view](https://raw.githubusercontent.com/maf946/SocketScripts/master/TCPClient.py))

I’ve provided those four source files, as well as extensive documentation, in a GitHub repository. [Click this link](https://github.com/maf946/SocketScripts), and start reading the documentation, which begins with the heading “Socket Programming: Creating Network Applications.” **If you do not carefully read the documentation linked above, you will not understand the rest of the lab**. Carefully reading the documentation will require your full attention, and may take quite some time. Get started now.

For this lab, you’ll be creating **four** PyCharm projects. Each project will have a main.py file. My suggestion is that you create the projects as follows:



1. A project called UDPServer. Replace the contents of main.py with the contents of UDPServer.py.
2. A project called UDPClient. Replace the contents of main.py with the contents of UDPClient.py. When prompted, I suggest opening the project in a New Window.
3. A project called TCPServer. Replace the contents of main.py with the contents of TCPServer.py. When prompted, I suggest opening the project in a New Window.
4. A project called TCPClient. Replace the contents of main.py with the contents of TCPClient.py. When prompted, I suggest opening the project in a New Window.

 


## **Section **2:** ** Inspecting** UDP Traffic Through Wireshark**

** **

As seen in the last few labs, Wireshark will listen and document hundreds of different networking protocols. So far, we’ve seen HTTP and DNS, but in this lab, we will be focusing on the TCP and UDP packets that are being exchanged between the client and the server. 

 

In this section, you’ll be launching Wireshark, then running UDPClient.py and UDPServer.py. 

**Step 0**: As a precaution to make sure you don’t have network adapter issues, reboot your virtual machine

 

**Step 1: **Launch Wireshark with _sudo wireshark_

 

**Step 2: **Start sniffing the ‘_any_’ interface. This will intercept all packet traffic (regardless of network interface) on your machine.

** **

**Step 3: **Run the UDPServer project in PyCharm. Keep it running. Make a note of the serverIP and serverPort values visible in the “Run” portion of the PyCharm window, as in the screenshot below:



<p id="gdcalert1" ><span style="color: red; font-weight: bold">>>>>>  gd2md-html alert: inline image link here (to images/image1.png). Store image on your image server and adjust path/filename/extension if necessary. </span><br>(<a href="#">Back to top</a>)(<a href="#gdcalert2">Next alert</a>)<br><span style="color: red; font-weight: bold">>>>>> </span></p>


![alt_text](images/image1.png "image_tooltip")


**Step 4**: While the UDPServer is still running, switch over to the UDPClient project in PyCharm. Replace the values for serverIP and serverPort in the source code with the values from the UDPServer. Make sure to keep the serverIP value in double quotes. Run the UDPClient, and send a message from the client to the server. You should receive a response in upper-case, as in the screenshot below:



<p id="gdcalert2" ><span style="color: red; font-weight: bold">>>>>>  gd2md-html alert: inline image link here (to images/image2.png). Store image on your image server and adjust path/filename/extension if necessary. </span><br>(<a href="#">Back to top</a>)(<a href="#gdcalert3">Next alert</a>)<br><span style="color: red; font-weight: bold">>>>>> </span></p>


![alt_text](images/image2.png "image_tooltip")


**Question 1**: Post a screenshot of the “Run” area in PyCharm for both UDPServer and UDPClient, after you have successfully sent a message between the two.

**Step 4: **Stop your Wireshark capture. Next, in Wireshark, identify the UDP packet(s) containing the message you sent in the prior step (i.e., the lowercase text). Explore the packet details area until you find the “data” corresponding to the message you sent. Using Wireshark, highlight the text corresponding to the message you sent, then take a screenshot of the entire Wireshark window.

**Question 2**: Post the screenshot described above.

** **


## Section 3: TCP Port Scanning with a Friend

In this section, you’ll be working with a friend (or at least a classmate… somebody other than yourself). You’ll use a port scan to find the TCP server on your friend’s virtual machine, then connect to it. (And the friend will do the same, vice-versa; this lab is still an individual assignment).

First, some table stakes:



* We’ll be using the **nmap** port scanner. Make sure to read the following sections of the textbook, which describe nmap:
    * In chapter 3.2, in a “Focus On Security: Port Scanning” section
    * The end of chapter 3.5.6
* Now that you’re trained in the art and science of nmap, it’s safe for you to install it. Go ahead and run `sudo apt install nmap`.** **


### When you’re acting as the server…

Depending on how your Internet connection is configured, it may be difficult for people to connect to your server because of NAT or firewall issues. To fix this, we’ll be using the (free) service, Packetriot, when running the server. I encourage you to review the official “[Getting Started with Packetriot](https://docs.packetriot.com)” documentation, which includes a video. However, what follows is a distillation of the key steps you must follow.

Please sign up for an account at [https://packetriot.com/signup](https://packetriot.com/signup). Use whatever email account you’d like; you’ll need to click a verification link sent to that account. Obviously, don’t forget the password you use to create the account.

After you click the verification link, click the “Free” plan, and “Skip” entering a credit card.

Next, we’ll set up the pktriot application on your virtual machine. Enter the following commands, as described in the [Packetriot Download page](https://packetriot.com/downloads). I strongly recommend copying and pasting these, rather than retyping. Note that command 3 below is in fact one command, though it’s quite lengthy.



1. `sudo apt-get install apt-transport-https gnupg -y`
2. `wget -qO - https://download.packetriot.com/linux/debian/pubkey.gpg | sudo apt-key add - `
3. `echo "`


```
deb [arch=amd64] https://download.packetriot.com/linux/debian/buster/stable/non-free/binary-amd64 / 
deb [arch=i386]  https://download.packetriot.com/linux/debian/buster/stable/non-free/binary-i386  / 
deb [arch=armhf] https://download.packetriot.com/linux/debian/buster/stable/non-free/binary-armhf / 
deb [arch=arm64] https://download.packetriot.com/linux/debian/buster/stable/non-free/binary-arm64 / 
" | sudo tee /etc/apt/sources.list.d/packetriot.list

```



4. `sudo apt-get update`
5. `sudo apt-get install pktriot`

 

Next, we’ll configure the pktriot client. Run `pktriot configure`. Enter “3” when prompted for a selection. Next, enter the email and password you used when creating your Packetriot account. Then, select whichever region you’d like (us-east certainly works).

Let’s start up the TCPServer. The server will accept requests on port 12000. We need to expose that port to the rest of the world (including your IST 220 friend) by creating an endpoint using Packetriot. Run the command `pktriot tcp 12000`. You will see a result like the screenshot below. Make note of the IPv4 and port values, highlighted by example in the screenshot.



<p id="gdcalert3" ><span style="color: red; font-weight: bold">>>>>>  gd2md-html alert: inline image link here (to images/image3.png). Store image on your image server and adjust path/filename/extension if necessary. </span><br>(<a href="#">Back to top</a>)(<a href="#gdcalert4">Next alert</a>)<br><span style="color: red; font-weight: bold">>>>>> </span></p>


![alt_text](images/image3.png "image_tooltip")


Provide your friend with the IPv4 address, but not the port number. Instead, make your friend earn it by giving them a range of 100 port numbers around the port number.[^1] For example:


<table>
  <tr>
   <td><strong>TCPServer.py port</strong>
   </td>
   <td><strong>Range to tell your friend</strong>
   </td>
  </tr>
  <tr>
   <td>22434
   </td>
   <td>22400-22499
   </td>
  </tr>
  <tr>
   <td>23569
   </td>
   <td>23500-23599
   </td>
  </tr>
  <tr>
   <td>25121
   </td>
   <td>25100-25199
   </td>
  </tr>
</table>



### Keep your TCP server running for the remainder of the exercise. 


### When you’re acting as the client…

**Phase 1**: Your friend is being a real pain and is not giving you a specific port number[^2], so you’ll need to snoop/scan around and find the open port in the range provided. nmap seems like it would be handy here, so let’s use that.

Observe the following example usage:


```
sudo nmap 159.203.126.35 -sS -p 22400-22499.
```


In a terminal window, run that command, replacing the IP address and port range as appropriate. The -sS option means you would like to run a stealth scan; a more detailed explanation of what this means is [available from the official nmap site](https://nmap.org/book/synscan.html).

It may take a few seconds, but before long you should see output which will tell you the open port, and you should see a result like the below. You want to find ports where the STATE is “open.” There may be several in the range (as in the screenshot), but one of them will be your friend’s. You may have to try each of them until you succeed.



<p id="gdcalert4" ><span style="color: red; font-weight: bold">>>>>>  gd2md-html alert: inline image link here (to images/image4.png). Store image on your image server and adjust path/filename/extension if necessary. </span><br>(<a href="#">Back to top</a>)(<a href="#gdcalert5">Next alert</a>)<br><span style="color: red; font-weight: bold">>>>>> </span></p>


![alt_text](images/image4.png "image_tooltip")


**Question 3**: Post a screenshot of the nmap command and output. Also include the full name and Penn State email address of the friend who was acting as the server.

** **

**Phase 2**: Now that you’ve found out how to sneak in to your very rude friend’s server, it’s time to go ahead and do that

**Step 1: **In Wireshark, start a capture on the ‘_any_’ interface

 

**Step 2: **Use the TCP client to connect to the TCP server on the appropriate port. You’ll need to modify the serverIP and serverPort values appropriately. 

**Step 3**: Send a message to the server, and observe the result coming back. You should see a result like the below:



<p id="gdcalert5" ><span style="color: red; font-weight: bold">>>>>>  gd2md-html alert: inline image link here (to images/image5.png). Store image on your image server and adjust path/filename/extension if necessary. </span><br>(<a href="#">Back to top</a>)(<a href="#gdcalert6">Next alert</a>)<br><span style="color: red; font-weight: bold">>>>>> </span></p>


![alt_text](images/image5.png "image_tooltip")


**Step 4: **Stop the Wireshark capture. Locate any of the packets corresponding to the TCP connection described here, and right-click it. Select “Follow,” then “TCP Stream.” A new window will open, which is mostly a large text area with encrypted text. 

**Step 5: **Close the new window, and observe that the Wireshark filter is set to a particular TCP stream (ex: “tcp.stream eq 0”). Based on what you now know about the TCP segment structure, explore this list of 10 or so packets.

**Question 4**: Post a screenshot of the Wireshark window with the appropriate filter set. In a well-written paragraph, explain what is happening across the course of the TCP stream. Hint: not all of the packets are for transporting the message you typed into the terminal. There is a lot of other plumbing that is happening behind the scenes, and which is now exposed to you in Wireshark.

** **


## Section 4: Extra Credit Opportunity

** **

This lab has given you an inside look as to how TCP and UDP operate. You observed that the messages you were sending were transmitted in plain text, where they could be easily captured and interpreted.

As an **_optional_ **extra credit problem, you add the barest modicum of cryptographic protection to your message by using the ROT13 substitution cipher. Essentially, we can replace each letter with the 13th letter after it in the alphabet, with “a” becoming “n,” “b” becoming “o”, and so on. For example, the ROT13 encrypted version of the plaintext message “tcp” would be “gpc.” To explore more, use the simple demo tool available at [https://rot13.com](https://rot13.com).

For up to 5 points of extra credit, make a copy of UDPServer.py and call it UDPServerROT13.py. Modify the source so that, rather than returning the uppercase version of the message sent by the client, it returns the ROT13 encrypted version. Provide the complete source code of UDPServerROT13.py, and a screenshot of your code in operation (from the client side).

Since this is extra credit, we leave the research on how to accomplish this to you. 

 


<!-- Footnotes themselves at the bottom. -->
## Notes

[^1]:
     Perhaps this is why I do not have more friends.

[^2]:
     You should find some new friends who really honor port transparency.
