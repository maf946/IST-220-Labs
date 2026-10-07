# Instructor notes: shared local poem service

The student programs default to `https://ai220.m84.us/v1/chat/completions`, model alias `ist220-small`. They use Python’s standard library plus certifi for HTTPS certificate verification. Install requirements into the interpreter running the student server or load test with `python3 -m pip install --upgrade -r requirements.txt` from Lab4. The shared service is a local llama.cpp server on Avar behind Caddy and Cloudflare; no paid AI provider is involved.

## Existing Avar configuration

Avar is a 2017 Intel iMac with an i5-7500 and 32 GiB RAM. The tested executable is llama.cpp b11429 and the model is Qwen2.5-0.5B-Instruct Q4_K_M. The larger model is not needed for this activity.

The model is at `~/llama-local/models/qwen2.5-0.5b-instruct-q4_k_m.gguf`. The server listens on `127.0.0.1:8220` with alias `ist220-small`, four CPU threads, context size 2048, one parallel slot, and no GPU layers. It reads its key from `~/llama-local/class-api-key.txt`.

The LaunchAgent `~/Library/LaunchAgents/us.m84.ist220-ai.plist` keeps it running while the Avar user is logged in. Logs are in `~/llama-local/logs/`. Keep Avar awake. Do not start a second server on the same port while the LaunchAgent is running.

Caddy exposes only POST `/v1/chat/completions` for `ai220.m84.us`, forwarding to loopback port 8220. The separate `220.m84.us` site is unchanged. Requests without a valid key have returned HTTP 401; authenticated public requests have returned poems successfully.

## Test before class

From this repository's Lab4 directory **on Avar**, run:

```bash
python3 InstructorLoadTest.py
```

The script reads the existing Avar key file and sends exactly three concurrent requests to the public endpoint. It prints each result and elapsed time without printing the key. Alternatively, it reads `IST220_AI_KEY` or `lab4_config.json` if no Avar key file is available. On Avar the existing key file takes precedence over the JSON key; an environment key takes precedence over both.

A successful run exits with status 0 and reports `Completed: 3/3`. Check elapsed times as well as success: a three-request pass is a small readiness check, not proof that a whole class can submit simultaneously. On October 6, 2026, three concurrent public requests completed successfully at about 30, 51, and 82 seconds. Local requests also passed, and manual TCP and UDP student exchanges using Avar’s LAN address returned poems. These live checks used the earlier major prompt; the current activity asks for a hobby. Campus peer discovery and Wireshark captures still need a classroom check. A single inference slot means concurrent requests can queue and encounter upstream timeouts. If this test fails or becomes too slow, stagger student groups rather than repeatedly retrying.

Then configure one student server using a copy of `lab4_config.example.json`, run each server/client pair locally, and verify a Wireshark capture. Test one partner connection on the actual classroom network. Campus client isolation can block peer traffic even when the public AI endpoint works.

Requests include `User-Agent: IST220-Lab/1.0`. The earlier default Python requests received HTTP 403 from the public endpoint; a manual request with this application header and the updated public load test succeeded. Keep the updated helper when distributing the lab.

A Windows PyCharm environment could not verify the service certificate using its default trust store. A connection test using certifi succeeded on October 7; the shared helper now explicitly uses this bundle while retaining certificate and hostname verification.

## Distribution

The student instructions currently link to the ZIP for the `lab4-ai-poems` branch. Before deleting that branch after a merge, update both the direct ZIP link and the repository/branch directions to the branch or release students should use.

Give students the entire Lab4 folder and distribute the class key through your course's private channel. Do not commit the actual configuration or key. The key grants access to this local service; rotate it if it is exposed. Student clients do not need it, but each student running a server does.

The new instructions preserve four report questions: UDP operation, UDP packet evidence, partner TCP port discovery, and TCP/UDP comparison. Poems are intentionally short, and errors or imperfect wording are not a reason to tune the model during the lab.

## Automated checks

From the repository root:

```bash
python3 -m unittest discover -s Lab4/tests -v
```

These checks use a local mock AI endpoint and real loopback sockets. They do not measure Avar's performance or prove campus-network reachability.
