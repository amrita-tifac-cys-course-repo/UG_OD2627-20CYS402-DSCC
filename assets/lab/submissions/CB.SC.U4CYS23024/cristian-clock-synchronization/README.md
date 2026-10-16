# Lab 6A - Cristian's Clock Synchronization Algorithm

**CB.SC.U4CYS23024**

One master (time server) and four clients, each in its own Docker container on the `clock-net` network. Every node keeps a logical clock (system clock + `CLOCK_OFFSET` seconds). Each client asks the master for the time, measures the round-trip time and corrects its own clock.

```text
                    +----------------------+
                    |   clock-master       |
                    |   Time Server :5000  |
                    +----------+-----------+
                               |  clock-net
       +--------------+--------+------+--------------+
       |              |               |              |
 clock-client1  clock-client2   clock-client3  clock-client4
     -8 s           +6 s            -4 s          +10 s
```

## Project structure

```text
cristian-clock-synchronization/
├── docker-compose.yml
├── master/
│   ├── Dockerfile
│   └── master.py
├── client/
│   ├── Dockerfile
│   └── client.py
└── experiments/          # env files for Part J
    ├── exp1.env  ...  exp4.env
    ├── asym-request.env
    └── asym-response.env
```

## Algorithm

Messages are JSON over TCP on port 5000.

```text
T1                = client clock just before sending TIME_REQUEST
Client → Master   : TIME_REQUEST
Master → Client   : MASTER_TIME
T2                = client clock just after receiving the reply
RTT               = T2 - T1
Estimated Delay   = RTT / 2
Synchronized Time = MASTER_TIME + RTT / 2
```

The client sets its logical clock so that it reads the synchronized time at the moment T2 was taken. Only the logical clock changes; the operating-system clock is never modified.

**Final Error** is the client's clock minus the master's clock after synchronization. All containers share the host's system clock, so this is the difference of their offsets. For that the master also sends its offset, which a real client would not know. The theoretical accuracy bound is `± RTT / 2`.

## Running

```bash
docker network create clock-net
docker network ls

docker compose up --build
```

Each client prints its result and exits; the master keeps running and logs every request. Stop with `Ctrl+C`, then `docker compose down`.

In another terminal while the master is running:

```bash
docker ps
docker network inspect clock-net
```

To print just one client's output again: `docker logs clock-client2`.

### Environment variables

| Variable | Service | Meaning |
|---|---|---|
| `CLIENT_ID` | client | Name shown in the output |
| `CLOCK_OFFSET` | all | Initial clock offset in seconds (negative = behind) |
| `MASTER_HOST` / `MASTER_PORT` | client | Address of the time server (default `clock-master:5000`) |
| `EXPERIMENT` | client | Label used in the output and the results row |
| `ARTIFICIAL_DELAY_MS` | master | Artificial delay per request |
| `DELAY_MODE` | master | `symmetric` (half before reading the clock, half after), `request` (all before) or `response` (all after) |

In `docker-compose.yml` the offsets are set from `MASTER_OFFSET` and `CLIENT1_OFFSET` ... `CLIENT4_OFFSET`. The defaults are the lab's suggested offsets (0, -8, +6, -4, +10).

## Network delay experiments (Part J)

Run `docker compose down` between experiments so the clients run again.

```bash
docker compose --env-file experiments/exp1.env up --build
docker compose --env-file experiments/exp2.env up
docker compose --env-file experiments/exp3.env up
docker compose --env-file experiments/exp4.env up
```

| File | Artificial delay | Split |
|---|---:|---|
| `exp1.env` | 0 ms | - |
| `exp2.env` | 100 ms | 50 ms request + 50 ms reply |
| `exp3.env` | 200 ms | 100 + 100 |
| `exp4.env` | 500 ms | 250 + 250 |
| `asym-request.env` | 200 ms | all on the request path |
| `asym-response.env` | 200 ms | all on the reply path |

The two asymmetric runs are an extra. They show what happens when the RTT/2 assumption is wrong. With 200 ms only on the request path, every client ends up about 100 ms ahead; with it only on the reply path, about 100 ms behind.

Each client prints a line starting with `RESULT |`. Collect them for the results table:

```bash
docker compose logs | grep "RESULT |"
```

## Results (Part K)

| Experiment | Client | Initial Clock | RTT | Estimated Delay | Corrected Clock | Final Error |
|---|---|---:|---:|---:|---:|---:|
<!-- Paste the RESULT rows from each experiment here (drop the leading "RESULT"). -->

## Answers to the questions

1. **Why does Cristian's algorithm require a time server?** The clients need one reference time to copy. The server is assumed to have the correct time (for example from a UTC receiver), and every client synchronizes to it.
2. **Why is RTT divided by two?** The master's time was read somewhere between T1 and T2. The client doesn't know exactly when, so it assumes the middle: the reply took half the round trip. By the time it arrives, the master's clock has moved on by about RTT/2.
3. **What assumption is made about network delay?** The request and the reply take the same time (symmetric delay), and the server's processing time is small or evenly split.
4. **What happens when the network delay increases?** RTT grows, and so does the accuracy bound of ± RTT/2. If the delay stays symmetric the correction is still close (exp2–exp4). But real delays are rarely perfectly symmetric, so the expected error grows with RTT.
5. **What if the request and response delays are asymmetric?** The RTT/2 estimate is wrong by half the difference between the two delays. With 200 ms only on the request path, the client ends up about +100 ms off; with it only on the reply path, about −100 ms (`asym-*.env`).
6. **Why not modify the actual OS clock?** Changing the system clock needs root privileges. Containers share the host's kernel clock, so changing it would affect every container and the host, and could break other programs (logs, certificates, timers). A logical clock lets each node have its own offset safely.
7. **What if the master becomes unavailable?** Clients can't synchronize and their clocks keep drifting. The master is a single point of failure; real systems use several time servers (as NTP does).
8. **Initial vs. corrected logical clock?** The initial clock is the master's time plus the client's starting offset (for example −8 s). The corrected clock is the master's time plus RTT/2, so the offset drops to roughly the delay-estimate error (milliseconds).
9. **How does the number of clients affect the master?** Each client sends its own request, so the load grows linearly. Many simultaneous requests increase the processing and queuing time, which increases RTT and makes the delay less symmetric.
10. **Limitations in a real system?** It relies on one trusted, accurate server (a single point of failure and a bottleneck). It assumes symmetric delays and can be badly off when they aren't. It has no protection against a faulty or malicious server. And clocks drift between synchronizations, so it must be repeated; setting the clock backwards can also break programs that expect time to only move forward.
