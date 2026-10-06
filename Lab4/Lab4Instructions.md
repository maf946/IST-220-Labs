# Lab 4: Poems over TCP and UDP

In this lab, you will send your first name and major to a Python server and receive a short AI-generated poem. You will compare UDP and TCP traffic in Wireshark, then use Nmap to discover a partner's TCP server port.

Your Python server forwards the request to a shared language model running on the instructor's computer. The model runs locally; no paid AI account is needed. The poem may be awkward or inaccurate. Its literary quality is not part of the assignment.

Complete your own lab and submit your own report. Work with a partner for the port-discovery activity, taking turns as client and server.

## Before you begin

You need Python 3.9 or newer, Wireshark (including Npcap on Windows), Nmap, the class API key from your instructor, and the Lab4 folder from this repository. Keep these files together in one folder:

- `TCPClient.py`, `TCPServer.py`, `UDPClient.py`, `UDPServer.py`
- `lab4_common.py`
- `lab4_config.example.json`

Open the folder as one project in your editor. You can also run everything from a terminal. Use `python3` on macOS; on Windows, use `py -3` in place of `python3` if necessary.

Copy `lab4_config.example.json` to **`lab4_config.json`** in the same folder. Replace `PASTE_CLASS_KEY_HERE` in the copy with the key provided by your instructor. Keep the quotation marks and the other settings. Do not include this file or the key in your report, screenshots, or Git commits. The repository ignores the local configuration file.

The **server** needs this configuration. The **client** does not need the key. Your computer needs Internet access when it runs a server because that server contacts the shared AI service.

## How the application works

There are two separate network conversations:

| Conversation | Protocol | What is sent |
|---|---|---|
| Your client ↔ your Python server | UDP or TCP, depending on the script | Name, major, request ID, and poem as readable JSON |
| Your Python server ↔ shared AI service | HTTPS | An authenticated poem request and the model's response |

The first conversation is the one you will inspect in this lab. HTTPS on the second conversation does **not** encrypt the first. Use a first name and a major; do not send sensitive information.

Each server asks the operating system for an available port and prints that port. Restarting it may change the port. Clients prompt for the server's IPv4 address and port before asking for your name and major.

Each client runs one request and exits. Servers keep running until you press **Ctrl+C**. Allow up to two minutes for a response. The shared model serves a small number of requests slowly; coordinate with your instructor before retrying. The programs do not automatically retry requests.

## Part 1: UDP on your own computer

1. Open a terminal in the Lab4 folder and run:

   ```bash
   python3 UDPServer.py
   ```

2. Record the printed port. Keep the server running.
3. In Wireshark, select the **loopback** interface: usually `lo0` on macOS, or the Npcap loopback capture adapter on Windows. Both programs will use `127.0.0.1`, so your Wi-Fi interface is not the correct interface for this test.
4. Start capturing. Enter a display filter using your actual server port, for example:

   ```text
   udp.port == 54321
   ```

5. In a second terminal in the same folder, run:

   ```bash
   python3 UDPClient.py
   ```

6. Accept the default server address `127.0.0.1`, enter the server's port, and enter your first name and major. Wait for the poem. Keep the output visible for your screenshot.
7. Stop capturing. Select the request packet, then choose **Follow → UDP Stream**. Select a readable text view such as UTF-8. The JSON request contains `name`, `major`, and `request_id`. The response contains the same request ID and a `poem`. Newlines inside a JSON string appear as `\n`; this is expected.
8. Examine the UDP headers of the request and response. Record both source and destination ports. Notice how the endpoints reverse direction.

**Question 1.** Include screenshots showing the UDP server's port and your client's inputs and poem. Explain which program is the client, which is the server, and why the client must know the server's address and port.

**Question 2.** Include a Follow UDP Stream screenshot showing your request and response. Identify the source and destination ports in each direction. Explain what the request ID does at the application layer, and why receiving this response does not mean UDP guarantees delivery. Can someone capturing this client–server traffic read your name and major? Support your answer with your capture.

Stop the UDP server with Ctrl+C when finished.

## Part 2: Find a partner's TCP port

Only scan your consenting partner's computer and the port range shared for this activity. Do not scan other devices or wider ranges.

1. Decide who will run the server first. The server partner runs:

   ```bash
   python3 TCPServer.py
   ```

2. The server partner shares their **LAN IPv4 address** and a block of at most 100 ports containing the printed server port. Do not reveal the exact port yet. For example, if the port is `54637`, share `54600–54699`. For a port near the top of the range, use `65500–65535`; no port exceeds 65535.
3. The client partner runs Nmap against that one address and range, substituting the actual values:

   ```bash
   nmap --unprivileged -sT -Pn -n -p 54600-54699 192.168.1.25
   ```

   `-sT` requests a TCP connect scan; it does not require an administrator terminal. `-Pn` skips host discovery, and `-n` skips name resolution. The range after `-p` limits the scan.

4. Identify the open port and check it with your partner. An Nmap service label is a guess based on port conventions; it does not establish what this Python application does. If multiple ports are open, have the server partner identify the lab port.
5. Keep the server running. Do not restart it between discovery and the next part.

**Question 3.** Provide your partner's name and course email, the exact Nmap command you ran, and a screenshot of its output. Identify the lab server's port and explain what Nmap's `open` result tells you. Explain why you cannot discover this TCP listener by scanning only UDP ports.

### If the partner connection is blocked

Being on the same Wi-Fi network does not guarantee that devices can reach each other. Check the LAN address and any prompt asking whether Python may accept incoming connections. Do not disable your firewall wholesale. If campus isolation or another restriction prevents the connection, ask your instructor to approve the fallback: run the TCP server locally and scan its announced range at `127.0.0.1`. Document the attempted partner test, the problem, and the approved fallback in your report.

## Part 3: Capture the TCP poem conversation

1. On the client computer, select the interface used to reach your partner: normally Wi-Fi or Ethernet. Use loopback only for the approved same-computer fallback.
2. Start a **new capture** after the Nmap scan so the scan's connections do not clutter your application capture. Apply a filter using the actual server port:

   ```text
   tcp.port == 54637
   ```

3. Run the client:

   ```bash
   python3 TCPClient.py
   ```

4. Enter your partner's LAN IPv4 address and the discovered port, followed by your name and major. Wait for the response, then stop capturing.
5. Select a packet in this connection and choose **Follow → TCP Stream**. Inspect the JSON request and poem. Close the stream window while keeping the selected stream filter to examine the packets in that connection.
6. Find the connection's SYN, SYN/ACK, and ACK packets. Locate the application data and examine how the connection closes. Packet counts and the placement of acknowledgments can vary; do not expect one fixed number of packets.
7. Switch roles so both partners run a client, discover a port, and capture their own exchange.

**Question 4.** Include a Follow TCP Stream screenshot showing your poem exchange and a packet-list screenshot showing the connection setup. In one or two paragraphs, compare this exchange with UDP: connection setup, delivery and ordering, and how the application knows it has a complete message. Explain why a long wait for a poem is not, by itself, evidence of packet loss. Use observations from your captures.

## Submit

Submit one report with labeled answers to Questions 1–4 and readable screenshots. Include enough packet-header detail to support your port comparisons. Do not submit the class key or `lab4_config.json`. Follow your instructor's directions for the report format and due date.

## Troubleshooting

| Symptom | What to check |
|---|---|
| Missing configuration or rejected class key | Check the local filename, JSON syntax, and key supplied by your instructor. Never paste the key into a help screenshot. |
| No matching packets | Check the capture interface, current server port, and whether capture started before running the client. |
| Connection refused | Check that the correct server is still running and that you used its current port. |
| Timeout, HTTP 503, or gateway error | The model may be loading or busy. Tell your instructor; avoid repeatedly submitting requests. |
| Nmap shows filtered ports | Check the address, network isolation, and firewall permissions with your instructor. |
| Poem has the wrong number of lines or odd wording | That is acceptable. The lab examines networking behavior, not model quality. |

For details about the code, see [SocketScriptsOverview.md](SocketScriptsOverview.md).
