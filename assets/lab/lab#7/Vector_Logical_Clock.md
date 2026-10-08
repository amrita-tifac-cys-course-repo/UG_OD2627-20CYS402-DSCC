# 20CYS402 - Distributed Systems and Cloud Computing
![](https://img.shields.io/badge/Batch-23CYS-gold) ![](https://img.shields.io/badge/UG-blue) ![](https://img.shields.io/badge/Subject-DSCC-blue) <br/>

## Lab#8 - Vector Clock
![](https://img.shields.io/badge/Date-October-blue)

### 1. Objective

Implement **Vector Clock** to track causal relationships between events in a distributed system and identify **concurrent events**.

The implementation must contain:

- At least **3 simulated distributed processes**
- A vector clock maintained by each process
- Local events
- Inter-process message passing
- Send and receive events
- Vector timestamp calculation
- Causal ordering
- Detection of concurrent events
- Comparison of vector timestamps

Students may implement the experiment using **any programming language of their choice**.

> **Note:** Docker is not required for this experiment. The distributed processes may be simulated using functions, classes, objects, threads, or separate program instances.

### 2. Expected Architecture

The distributed system should contain at least three processes:

```text
                 Distributed System

        +-----------------------+
        |       Process P1      |
        |    Vector Clock V1    |
        |                       |
        | Local / Send / Receive|
        +----------+------------+
                   |
                   | Message M1
                   | Vector: [2,0,0]
                   v
        +-----------------------+
        |       Process P2      |
        |    Vector Clock V2    |
        |                       |
        | Local / Send / Receive|
        +----------+------------+
                   |
                   | Message M2
                   | Vector: [2,3,0]
                   v
        +-----------------------+
        |       Process P3      |
        |    Vector Clock V3    |
        |                       |
        | Local / Send / Receive|
        +-----------------------+
```

For three processes:

```text
P1 → [C1, C2, C3]
P2 → [C1, C2, C3]
P3 → [C1, C2, C3]
```

Initially:

```text
P1 → [0,0,0]
P2 → [0,0,0]
P3 → [0,0,0]
```

Each position in the vector represents the knowledge of events at the corresponding process.

### 3. Learning Outcomes

After completing this experiment, students should be able to:

1. Understand the concept of vector time in distributed systems.
2. Implement Vector Clock algorithms.
3. Maintain vector timestamps for distributed processes.
4. Update vector clocks for local, send, and receive events.
5. Determine causal relationships between events.
6. Detect concurrent events.
7. Compare Vector Clocks with Lamport Logical Clocks.
8. Understand the space and communication overhead associated with Vector Clocks.


### Part A — Distributed Process Simulation

#### 4. Create Distributed Processes

Implement at least three processes:

| Process | Initial Vector Clock |
|---|---|
| `P1` | `[0,0,0]` |
| `P2` | `[0,0,0]` |
| `P3` | `[0,0,0]` |

Each process must maintain its own vector clock.

For example:

```text
P1 → [C1, C2, C3]

P2 → [C1, C2, C3]

P3 → [C1, C2, C3]
```

The processes do not need to run on separate physical machines.

They may be implemented using:

- Classes
- Objects
- Functions
- Threads
- Separate program instances
- Message queues
- Sockets
- Any other suitable programming construct

### Part B — Vector Clock

#### 5. Vector Clock Representation

For `N` processes, each process maintains a vector of size `N`.

For three processes:

```text
P1 → [0,0,0]
P2 → [0,0,0]
P3 → [0,0,0]
```

The positions have a fixed meaning:

```text
Position 0 → P1
Position 1 → P2
Position 2 → P3
```

Therefore:

```text
[4,3,2]
```

means:

```text
P1 knows about 4 events at P1
P2 knows about 3 events at P2
P3 knows about 2 events at P3
```

#### 6. Rule 1 — Local Event

Before executing a local event at process `Pi`, increment the component corresponding to `Pi`.

For example, initially:

```text
P1 = [0,0,0]
```

P1 performs a local event:

```text
P1 = [1,0,0]
```

Another local event at P1:

```text
P1 = [2,0,0]
```

Similarly, if P2 performs a local event:

```text
P2 = [0,1,0]
```

#### 7. Rule 2 — Send Event

Before sending a message, the sender increments its own component.

For example:

```text
P1 = [1,0,0]
```

P1 sends a message to P2.

First:

```text
P1 = [2,0,0]
```

The vector timestamp `[2,0,0]` is attached to the message.

Example:

```text
Message ID        : M1
Sender            : P1
Receiver          : P2
Vector Timestamp  : [2,0,0]
```

#### 8. Rule 3 — Receive Event

When a process receives a message containing vector timestamp `T`, it must:

1. Take the component-wise maximum of its current vector and the received vector.
2. Increment its own component.

For example:

```text
P2 Current Vector = [0,0,0]

Received Vector   = [2,0,0]
```

First calculate the component-wise maximum:

```text
max([0,0,0], [2,0,0])
= [2,0,0]
```

Then increment P2's component:

```text
P2 = [2,1,0]
```

Therefore, the receive event gets:

```text
[2,1,0]
```

### Part C — Vector Clock Rules

#### 9. Summary of Rules

For a process `Pi`:

#### Local Event

```text
VC[i] = VC[i] + 1
```

#### Send Event

```text
VC[i] = VC[i] + 1

Attach VC to the message
```

#### Receive Event

```text
FOR every process j:

    VC[j] = max(VC[j], received_VC[j])

VC[i] = VC[i] + 1
```

The receive operation is therefore:

\[
VC_i[j] = \max(VC_i[j], M[j])
\]

for every component `j`, followed by:

\[
VC_i[i] = VC_i[i] + 1
\]


### Part D — Event Types

#### 10. Required Event Types

The implementation must support at least:

| Event Type | Description |
|---|---|
| `LOCAL` | Event occurring within a process |
| `SEND` | Process sends a message |
| `RECEIVE` | Process receives a message |

Example:

```text
LOCAL(P1)

SEND(P1, P2)

RECEIVE(P2, P1)
```

### Part E — Exercise Scenario

#### 11. Implement the Following Event Sequence

Use three processes:

```text
P1
P2
P3
```

Initially:

```text
P1 = [0,0,0]
P2 = [0,0,0]
P3 = [0,0,0]
```

Execute the following sequence:

```text
1. P1 performs a local event E1.

2. P1 sends a message M1 to P2.

3. P2 receives M1 from P1.

4. P2 performs a local event E4.

5. P2 sends a message M2 to P3.

6. P1 performs a local event E6.

7. P1 sends a message M3 to P3.

8. P3 receives M2 from P2.

9. P3 receives M3 from P1.
```

The vector timestamps must be **calculated by your program**.

Do not hard-code the expected timestamps.


### Part E — Expected Vector Clock Calculation

#### 13. Calculate the Vector Timestamps

The following values illustrate the expected progression.

#### E1 — P1 Local Event

```text
P1 = [1,0,0]
```

#### E2 — P1 Sends M1 to P2

```text
P1 = [2,0,0]
```

Message M1 contains:

```text
[2,0,0]
```

#### E3 — P2 Receives M1

Before receiving:

```text
P2 = [0,0,0]
```

After component-wise maximum:

```text
[2,0,0]
```

Increment P2's component:

```text
P2 = [2,1,0]
```

#### E4 — P2 Local Event

```text
P2 = [2,2,0]
```

#### E5 — P2 Sends M2 to P3

```text
P2 = [2,3,0]
```

Message M2 contains:

```text
[2,3,0]
```

#### E6 — P1 Local Event

P1 currently has:

```text
[2,0,0]
```

After E6:

```text
P1 = [3,0,0]
```

#### E7 — P1 Sends M3 to P3

```text
P1 = [4,0,0]
```

Message M3 contains:

```text
[4,0,0]
```

#### E8 — P3 Receives M2

Before receiving:

```text
P3 = [0,0,0]
```

M2 contains:

```text
[2,3,0]
```

Component-wise maximum:

```text
[2,3,0]
```

Increment P3:

```text
P3 = [2,3,1]
```

#### E9 — P3 Receives M3

Current:

```text
P3 = [2,3,1]
```

Received:

```text
[4,0,0]
```

Component-wise maximum:

```text
[4,3,1]
```

Increment P3:

```text
P3 = [4,3,2]
```

### Part F — Required Output

#### 14. Event Log

The program should produce a clear event log similar to:

```text
========================================================
                 VECTOR CLOCK
========================================================

Process    Event    Type        Vector Timestamp
--------------------------------------------------------
P1         E1       LOCAL       [1,0,0]
P1         E2       SEND        [2,0,0]
P2         E3       RECEIVE     [2,1,0]
P2         E4       LOCAL       [2,2,0]
P2         E5       SEND        [2,3,0]
P1         E6       LOCAL       [3,0,0]
P1         E7       SEND        [4,0,0]
P3         E8       RECEIVE     [2,3,1]
P3         E9       RECEIVE     [4,3,2]
--------------------------------------------------------
```

Your program must calculate the vector timestamps dynamically.


### Part G — Vector Timestamp Comparison

#### 15. Comparing Two Vector Clocks

Given two vector timestamps:

```text
V1 = [2,3,1]

V2 = [4,3,2]
```

We say:

\[
V_1 \leq V_2
\]

if:

\[
V_1[i] \leq V_2[i]
\]

for every component `i`.

For example:

```text
[2,3,1] ≤ [4,3,2]
```

because:

```text
2 ≤ 4
3 ≤ 3
1 ≤ 2
```

and at least one component is strictly smaller.

Therefore:

```text
V1 < V2
```

and the event associated with `V1` happened before the event associated with `V2`.

### Part H — Causal Ordering

#### 16. Determine Causal Relationship

Vector clocks can be used to determine whether one event causally happened before another.

For two vector timestamps `A` and `B`:

```text
A < B
```

if:

1. Every component of `A` is less than or equal to the corresponding component of `B`.
2. At least one component of `A` is strictly less than the corresponding component of `B`.

Formally:

\[
A < B
\]

if:

\[
A[i] \leq B[i] \quad \forall i
\]

and:

\[
A[j] < B[j]
\]

for at least one `j`.

### Part I — Concurrent Events

#### 17. Detect Concurrent Events

Two events are concurrent when neither vector timestamp is less than the other.

For example:

```text
A = [3,0,0]

B = [2,2,0]
```

Compare:

```text
A ≤ B ?

3 ≤ 2  → FALSE
```

Therefore:

```text
A ≰ B
```

Now:

```text
B ≤ A ?

2 ≤ 3  → TRUE
2 ≤ 0  → FALSE
```

Therefore:

```text
B ≰ A
```

Since neither vector is less than the other:

```text
A || B
```

The events are **concurrent**.

Your implementation must detect at least **one pair of concurrent events**.

### Part J — Required Comparison Function

#### 18. Implement Vector Clock Comparison

Implement a function equivalent to:

```text
compare(V1, V2)
```

The function should determine whether:

```text
V1 happened before V2
```

or:

```text
V2 happened before V1
```

or:

```text
V1 and V2 are concurrent
```

The output may be:

```text
V1 → V2

V2 → V1

V1 || V2
```

where:

```text
→  = happened-before
||  = concurrent
```

---

# Part M — Required Experiment

#### 19. Demonstrate the Following

Your implementation must demonstrate:

#### Case 1 — Same Process Ordering

Example:

```text
P1 E1 → P1 E2
```

Show that:

```text
VC(E1) < VC(E2)
```

#### Case 2 — Message-Based Causality

Example:

```text
P1 SEND → P2 RECEIVE
```

Show that:

```text
VC(SEND) < VC(RECEIVE)
```

#### Case 3 — Transitive Causality

Example:

```text
P1 → P2 → P3
```

Show that the causal relationship propagates through the vector clock.

#### Case 4 — Concurrent Events

Create two events where there is no causal relationship and demonstrate:

```text
VC(A) ≰ VC(B)

AND

VC(B) ≰ VC(A)
```

Therefore:

```text
A || B
```

### Part K — Message Representation

#### 20. Message Structure

Every message should contain at least:

```text
Message ID
Sender
Receiver
Vector Timestamp
```

For example:

```text
Message ID        : M1
Sender            : P1
Receiver          : P2
Vector Timestamp  : [2,0,0]
```

Students may use any suitable data structure:

```text
Class
Structure
Object
Dictionary / Map
JSON
Record
```

### Part L — Required Operations

#### 21. Local Event

Implement an operation equivalent to:

```text
local_event(P1)
```

It should:

1. Increment the local process's vector component.
2. Assign the resulting vector timestamp.
3. Record the event.
4. Display the event.

---

### 22. Send Message

Implement an operation equivalent to:

```text
send_message(P1, P2)
```

It should:

1. Increment the sender's vector component.
2. Attach the vector timestamp to the message.
3. Deliver the message to the destination process.
4. Record the send event.

---

### 23. Receive Message

Implement an operation equivalent to:

```text
receive_message(P2, message)
```

It should:

1. Read the received vector.
2. Perform component-wise maximum.
3. Increment the receiver's vector component.
4. Record the receive event.
5. Display the updated vector timestamp.

---

### 24. Vector Comparison

Implement an operation equivalent to:

```text
compare_vectors(V1, V2)
```

It should return one of:

```text
V1 happened before V2

V2 happened before V1

V1 and V2 are concurrent

V1 and V2 represent the same timestamp
```

### Part M — Programming Language

#### 25. Language Choice

Students may use **any programming language of their choice**.

Examples include:

- Python
- C
- C++
- Java
- JavaScript
- TypeScript
- Go
- Rust
- C#
- Kotlin

The programming language itself will not be the primary evaluation criterion.

The implementation must correctly demonstrate the Vector Clock algorithm.

---

### Part M — Communication / Simulation

#### 26. Process Communication

Since this experiment does not require Docker, students may simulate communication using any suitable mechanism.

Examples:

```text
Function calls
Objects / Classes
Shared data structures
Queues
Threads
Sockets
REST APIs
Message-passing mechanisms
```

At minimum, the implementation must clearly demonstrate that the vector timestamp is transferred from the sending process to the receiving process.

### Part N — Required Results

#### 27. Results Table

Submit a table similar to:

| Event | Process | Type | Message | Vector Timestamp |
|---|---|---|---|---|
| E1 | P1 | LOCAL | – | |
| E2 | P1 | SEND | P1 → P2 | |
| E3 | P2 | RECEIVE | P1 → P2 | |
| E4 | P2 | LOCAL | – | |
| E5 | P2 | SEND | P2 → P3 | |
| E6 | P1 | LOCAL | – | |
| E7 | P1 | SEND | P1 → P3 | |
| E8 | P3 | RECEIVE | P2 → P3 | |
| E9 | P3 | RECEIVE | P1 → P3 | |

Fill in the vector timestamps obtained from your implementation.


### Part O — Causal Relationship Table

#### 28. Analyze Event Relationships

Identify at least five pairs of events and classify their relationship.

| Event A | Event B | Vector A | Vector B | Relationship |
|---|---|---|---|---|
| E1 | E2 | | | |
| E2 | E3 | | | |
| E5 | E8 | | | |
| E6 | E4 | | | |
| E7 | E5 | | | |

The relationship should be one of:

```text
A → B

B → A

A || B
```

### Part P — Questions to Answer

#### 29. Lab Questions

1. What problem does a Vector Clock solve?

2. Why does every process maintain a vector instead of a single integer?

3. What does each position in a vector represent?

4. What happens to the vector during a local event?

5. What happens to the vector before sending a message?

6. What happens when a process receives a message?

7. Why is a component-wise maximum used during message reception?

8. How can Vector Clocks determine whether one event causally precedes another?

9. How can Vector Clocks detect concurrent events?

10. Can two concurrent events have different vector timestamps?

11. Can two different events have the same vector timestamp?

12. What happens to the size of a vector as the number of processes increases?

13. What are the disadvantages of Vector Clocks?

14. How do Vector Clocks differ from Lamport Logical Clocks?

15. Why can Vector Clocks detect concurrency while Lamport Clocks cannot?


### Part Q — Comparison with Lamport Clock

#### 30. Compare Lamport and Vector Clocks

Complete the following table:

| Feature | Lamport Clock | Vector Clock |
|---|---|---|
| Timestamp structure | | |
| Number of values maintained | | |
| Represents causal ordering | | |
| Detects concurrency | | |
| Message overhead | | |
| Storage overhead | | |
| Suitable for large distributed systems | | |
| Implementation complexity | | |
| Can distinguish concurrent events? | | |

