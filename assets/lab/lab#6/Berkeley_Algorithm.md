# 20CYS402 - Distributed Systems and Cloud Computing
![](https://img.shields.io/badge/Batch-23CYS-gold) ![](https://img.shields.io/badge/UG-blue) ![](https://img.shields.io/badge/Subject-DSCC-blue) <br/>

## Lab#6B - Berkeley Clock Synchronization Algorithm
![](https://img.shields.io/badge/Date-24_September-blue)

### 1. Objective

Implement the **Berkeley Clock Synchronization Algorithm** using multiple Docker containers representing distributed nodes.

The implementation must contain:

- **1 Master / Coordinator**
- **At least 3–4 Client containers**
- A dedicated Docker network
- Independent logical clocks with configurable offsets
- Master polling of all nodes
- Clock-offset calculation
- Average-offset calculation
- Correction messages
- Final synchronized clocks
- Experimental evaluation with different clock offsets and an optional faulty node


### 2. Expected Architecture

```text
                       +----------------------+
                       |   MASTER /          |
                       |   COORDINATOR       |
                       |   Logical Clock     |
                       +----------+-----------+
                                  |
                         Docker Network
                             clock-net
                                  |
             +--------------------+--------------------+
             |                    |                    |
             v                    v                    v
       +-----------+        +-----------+        +-----------+
       | Client 1  |        | Client 2  |        | Client 3  |
       |   -8 sec  |        |   +6 sec  |        |   -4 sec  |
       +-----------+        +-----------+        +-----------+
                                                       |
                                                       v
                                                 +-----------+
                                                 | Client 4  |
                                                 |  +10 sec  |
                                                 +-----------+
```

### 3. Learning Outcomes

After completing this experiment, students should be able to:

1. Deploy multiple distributed nodes using Docker.
2. Implement Berkeley's clock synchronization algorithm.
3. Understand coordinator-based clock synchronization.
4. Calculate clock offsets.
5. Calculate the average offset of participating nodes.
6. Send clock corrections to distributed clients.
7. Study the effect of incorrect/outlier clocks.
8. Compare synchronized clocks before and after correction.


### Part A — Docker Environment

#### 4. Create the Docker Network

```bash
docker network create clock-net
```

Verify:

```bash
docker network ls
```

---

#### 5. Required Containers

Create at least five containers:

| Container | Role | Suggested Initial Offset |
|---|---|---:|
| `clock-master` | Coordinator | 0 seconds |
| `clock-client1` | Client | -8 seconds |
| `clock-client2` | Client | +6 seconds |
| `clock-client3` | Client | -4 seconds |
| `clock-client4` | Client | +10 seconds |

The offsets should be configurable through environment variables.

Example:

```text
CLOCK_OFFSET=-8
CLIENT_ID=client1
```

### Part B — Project Structure

Create:

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

---

### Part C — Master / Coordinator

#### 6. Master Responsibilities

The master acts as the **coordinator**, not necessarily as an authoritative time server.

The master must:

1. Maintain its own logical clock.
2. Contact every client.
3. Request each client's current clock.
4. Receive clock values from all participating nodes.
5. Calculate the offset of every node relative to the master.
6. Calculate the average offset.
7. Determine the correction for every node.
8. Send the correction to each client.
9. Apply its own correction.
10. Display the clocks before and after synchronization.

---

### Part D — Client

#### 7. Client Responsibilities

Each client must:

1. Start with a configurable logical clock offset.
2. Maintain its logical clock.
3. Respond to the master's clock request.
4. Send its current clock value.
5. Receive a correction value from the master.
6. Apply the correction.
7. Display its clock before and after synchronization.

### Part E — Berkeley Algorithm

#### 8. Algorithm

The Berkeley algorithm can be implemented as follows.

##### Step 1 — Master polls all nodes

The master sends:

```text
MASTER → Client 1: CLOCK_REQUEST
MASTER → Client 2: CLOCK_REQUEST
MASTER → Client 3: CLOCK_REQUEST
MASTER → Client 4: CLOCK_REQUEST
```

Each client responds:

```text
Client 1 → MASTER: 11:59:52
Client 2 → MASTER: 12:00:06
Client 3 → MASTER: 11:59:56
Client 4 → MASTER: 12:00:10
```

The master also knows its own clock:

```text
Master = 12:00:00
```

---

#### 9. Calculate Clock Offsets

Use the master's clock as the reference for calculating offsets.

Example:

```text
Master       = 12:00:00  →  0 seconds
Client 1     = 11:59:52  → -8 seconds
Client 2     = 12:00:06  → +6 seconds
Client 3     = 11:59:56  → -4 seconds
Client 4     = 12:00:10  → +10 seconds
```


#### 10. Calculate Average Offset

Include the master and all participating clients.

```text
Average Offset =
    (Master Offset
     + Client 1 Offset
     + Client 2 Offset
     + Client 3 Offset
     + Client 4 Offset) / 5
```

Using the example:

```text
Average Offset =
    (0 - 8 + 6 - 4 + 10) / 5

= 4 / 5

= +0.8 seconds
```


#### 11. Calculate Corrections

Each node's correction is:

```text
Correction =
    Average Offset - Node Offset
```

Therefore:

```text
Master:
    +0.8 - 0 = +0.8 seconds

Client 1:
    +0.8 - (-8) = +8.8 seconds

Client 2:
    +0.8 - (+6) = -5.2 seconds

Client 3:
    +0.8 - (-4) = +4.8 seconds

Client 4:
    +0.8 - (+10) = -9.2 seconds
```

### Part F — Applying Corrections

The master sends:

```text
MASTER → Client 1: +8.8 sec
MASTER → Client 2: -5.2 sec
MASTER → Client 3: +4.8 sec
MASTER → Client 4: -9.2 sec
```

The master applies:

```text
Master Correction = +0.8 sec
```

After correction, all nodes should approximately converge to:

```text
12:00:00.8
```


### Part G — Docker Compose

Create a `docker-compose.yml` containing:

- One master service
- Four client services
- A common Docker network
- Environment variables for client IDs
- Environment variables for clock offsets


### Part H — Running the Experiment

Build and start the containers:

```bash
docker compose up --build
```

Verify:

```bash
docker ps
```

Inspect the network:

```bash
docker network inspect clock-net
```


### Part I — Required Output

The master should display output similar to:

```text
========== BERKELEY ALGORITHM ==========

Initial Clocks

Master       : 12:00:00
Client 1     : 11:59:52
Client 2     : 12:00:06
Client 3     : 11:59:56
Client 4     : 12:00:10

------------------------------------------

Clock Offsets

Master       : +0 sec
Client 1     : -8 sec
Client 2     : +6 sec
Client 3     : -4 sec
Client 4     : +10 sec

Average Offset: +0.8 sec

------------------------------------------

Corrections

Master       : +0.8 sec
Client 1     : +8.8 sec
Client 2     : -5.2 sec
Client 3     : +4.8 sec
Client 4     : -9.2 sec

------------------------------------------

Final Clocks

Master       : 12:00:00.8
Client 1     : 12:00:00.8
Client 2     : 12:00:00.8
Client 3     : 12:00:00.8
Client 4     : 12:00:00.8
```

Exact values will depend on the implementation.

### Part J — Experiment 1: Different Clock Offsets

Perform at least three experiments.

#### Experiment 1

```text
Client 1 = -5 sec
Client 2 = +5 sec
Client 3 = -3 sec
Client 4 = +3 sec
```

#### Experiment 2

```text
Client 1 = -15 sec
Client 2 = +10 sec
Client 3 = -5 sec
Client 4 = +20 sec
```

#### Experiment 3

Use your own offsets.

Record:

- Initial clocks
- Clock offsets
- Average offset
- Corrections
- Final clocks
- Final synchronization error


### Part K — Experiment 2: Faulty / Outlier Clock

Introduce one abnormal clock.

Example:

```text
Master       = 12:00:00
Client 1     = 11:59:55
Client 2     = 12:00:05
Client 3     = 12:00:03
Client 4     = 15:30:00   ← faulty/outlier
```

First run Berkeley's algorithm **without excluding the outlier**.

Observe the effect on the average.

Then implement an optional outlier-handling mechanism.

For example:

```text
if abs(offset) > threshold:
    exclude node
```

Run the experiment again and compare the results.

> Clearly document that outlier removal is an implementation enhancement and is not simply part of the basic Berkeley algorithm.


### Part L — Results Table

Submit a table similar to:

| Experiment | Node | Initial Clock | Offset | Average Offset | Correction | Final Clock | Error |
|---|---|---:|---:|---:|---:|---:|---:|
| 1 | Master | | | | | | |
| 1 | Client 1 | | | | | | |
| 1 | Client 2 | | | | | | |
| 1 | Client 3 | | | | | | |
| 1 | Client 4 | | | | | | |


### Part M — Questions to Answer

1. Why does Berkeley's algorithm use a coordinator?
2. Why does Berkeley's algorithm not require an externally accurate time server?
3. Why are clock offsets calculated relative to the master?
4. Why is the average offset calculated?
5. Why does the master also adjust its own clock?
6. What happens when one node has a very large clock error?
7. How does an outlier affect the average?
8. What is the purpose of excluding faulty nodes?
9. What happens if one client does not respond?
10. What happens if the master fails?
11. How is Berkeley's algorithm different from Cristian's algorithm?
12. How does the number of clients affect the synchronization process?
