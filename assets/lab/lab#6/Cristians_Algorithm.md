# 20CYS402 - Distributed Systems and Cloud Computing
![](https://img.shields.io/badge/Batch-23CYS-gold) ![](https://img.shields.io/badge/UG-blue) ![](https://img.shields.io/badge/Subject-DSCC-blue) <br/>

## Lab#6A - Cristian's Clock Synchronization Algorithm
![](https://img.shields.io/badge/Date-24_September-blue)

### 1. Objective

Implement **Cristian's Clock Synchronization Algorithm** using multiple Docker containers representing distributed nodes.

The implementation must contain:

- **1 Master / Time Server**
- **At least 3–4 Client containers**
- A dedicated Docker network
- Logical clocks with configurable offsets
- Client–server communication
- RTT measurement and clock correction
- Experimental evaluation under different network delays


### 2. Expected Architecture

```text
                    +----------------------+
                    |    Master / Server   |
                    |    Time Server       |
                    |    Port: 5000        |
                    +----------+-----------+
                               |
                    Docker Network: clock-net
                               |
          +--------------------+--------------------+
          |                    |                    |
          v                    v                    v
   +-------------+      +-------------+      +-------------+
   |   Client 1  |      |   Client 2  |      |   Client 3  |
   |  Clock: -8s |      |  Clock: +6s |      |  Clock: -4s |
   +-------------+      +-------------+      +-------------+
                                                    |
                                                    v
                                             +-------------+
                                             |   Client 4  |
                                             |  Clock: +10s|
                                             +-------------+
```


### 3. Learning Outcomes

After completing this experiment, students should be able to:

1. Implement Cristian's algorithm.
2. Measure round-trip time (RTT).
3. Estimate one-way network delay.
4. Correct a client's logical clock.
5. Study the effect of network latency on synchronization accuracy.
6. Calculate synchronization error experimentally.


### Part A — Docker Environment

#### 4. Create the Docker Network

Create a network named `clock-net`:

```bash
docker network create clock-net
```

Verify:

```bash
docker network ls
```

#### 5. Required Containers

Create at least five containers:

| Container | Role | Suggested Initial Offset |
|---|---|---:|
| `clock-master` | Time Server | 0 seconds |
| `clock-client1` | Client | -8 seconds |
| `clock-client2` | Client | +6 seconds |
| `clock-client3` | Client | -4 seconds |
| `clock-client4` | Client | +10 seconds |

The offsets should be configurable using environment variables.

For example:

```text
CLOCK_OFFSET=-8
CLIENT_ID=client1
```

### Part B — Project Structure

Create the following project structure:

```text
clock-synchronization/
│
├── docker-compose.yml
│
├── master/
│   ├── Dockerfile
│   └── master.py
│
└── client/
    ├── Dockerfile
    └── client.py
```

### Part C — Master / Time Server

#### 6. Master Responsibilities

The master must:

1. Start a server.
2. Listen for client requests.
3. Maintain its own logical clock.
4. Return the current logical time when a client requests it.
5. Optionally introduce an artificial processing/network delay.
6. Display requests received from clients.

Example interaction:

```text
Client → Master: TIME_REQUEST
Master → Client: MASTER_TIME = 12:00:15.300
```

### Part D — Client

#### 7. Client Responsibilities

Each client must:

1. Start with a configurable logical clock offset.
2. Record the time immediately before sending a request.
3. Send a `TIME_REQUEST` to the master.
4. Receive the master's current time.
5. Record the time immediately after receiving the response.
6. Calculate RTT.
7. Estimate one-way network delay.
8. Calculate the corrected clock.
9. Display the synchronization result.


### Part E — Cristian's Algorithm

#### 8. Algorithm

For each synchronization request:

##### Step 1 — Record request time

```text
T1 = Client time immediately before request
```

##### Step 2 — Send request

```text
Client → Master: TIME_REQUEST
```

##### Step 3 — Receive master time

```text
Master → Client: MASTER_TIME
```

##### Step 4 — Record response time

```text
T2 = Client time immediately after receiving response
```

##### Step 5 — Calculate RTT

```text
RTT = T2 - T1
```

##### Step 6 — Estimate network delay

Assuming approximately symmetric network delay:

```text
Estimated Delay = RTT / 2
```

##### Step 7 — Calculate synchronized time

```text
Synchronized Time =
    Master Time + RTT/2
```

The client should use this value as its corrected logical time.


### Part F — Example Calculation

Assume:

```text
T1           = 10:00:00.100
Master Time  = 10:00:00.250
T2           = 10:00:00.350
```

Then:

```text
RTT = T2 - T1
    = 0.350 - 0.100
    = 0.250 seconds
```

Estimated one-way delay:

```text
Delay = RTT / 2
      = 0.125 seconds
```

Estimated synchronized client time:

```text
Master Time + Delay
= 10:00:00.250 + 0.125
= 10:00:00.375
```

### Part G — Docker Compose

Create a `docker-compose.yml` that contains:

- One master service
- Four client services
- A common `clock-net` network
- Environment variables for client IDs and clock offsets


### Part H — Running the Experiment

Build and start all containers:

```bash
docker compose up --build
```

Verify running containers:

```bash
docker ps
```

Verify the network:

```bash
docker network inspect clock-net
```

### Part I — Required Output

Each client should display output similar to:

```text
========== CRISTIAN'S ALGORITHM ==========

Client ID       : Client-2
Initial Clock   : 12:00:08.000

T1              : 12:00:15.120
Master Time     : 12:00:15.300
T2              : 12:00:15.520

RTT             : 400 ms
Estimated Delay : 200 ms

Corrected Clock : 12:00:15.500
Final Error     : 0 ms
```

The exact values will depend on the implementation and network conditions.

### Part J — Network Delay Experiments

The master should optionally introduce artificial delay.

For example:

```python
time.sleep(0.2)
```

Perform at least four experiments:

| Experiment | Artificial Delay |
|---|---:|
| 1 | 0 ms |
| 2 | 100 ms |
| 3 | 200 ms |
| 4 | 500 ms |

For every experiment, record:

- Client clock before synchronization
- T1
- Master time
- T2
- RTT
- Estimated delay
- Corrected clock
- Final synchronization error

### Part K — Results Table

Submit a table similar to:

| Experiment | Client | Initial Clock | RTT | Estimated Delay | Corrected Clock | Final Error |
|---|---|---:|---:|---:|---:|---:|
| 1 | Client 1 | | | | | |
| 1 | Client 2 | | | | | |
| 1 | Client 3 | | | | | |
| 1 | Client 4 | | | | | |
| 2 | Client 1 | | | | | |
| 2 | Client 2 | | | | | |


### Part L — Questions to Answer

1. Why does Cristian's algorithm require a time server?
2. Why is RTT divided by two?
3. What assumption is made about network delay?
4. What happens when the network delay increases?
5. What happens if the request and response delays are asymmetric?
6. Why should the actual operating-system clock not be modified for this experiment?
7. What happens if the master becomes unavailable?
8. What is the difference between the client's initial logical clock and its corrected logical clock?
9. How does the number of clients affect the master?
10. What are the limitations of Cristian's algorithm in a real distributed system?
