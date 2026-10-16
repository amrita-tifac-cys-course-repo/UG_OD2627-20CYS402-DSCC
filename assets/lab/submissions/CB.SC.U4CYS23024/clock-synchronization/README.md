# Lab 6B - Berkeley Clock Synchronization Algorithm

**CB.SC.U4CYS23024**

One master (coordinator) and four clients, each in its own Docker container on the `clock-net` network. Every node keeps a logical clock (system clock + `CLOCK_OFFSET` seconds). The master polls the clients, averages the offsets, and sends each node a correction.

```text
                    +--------------------+
                    |   clock-master     |
                    |   offset 0 s       |
                    +---------+----------+
                              |  clock-net
       +-------------+--------+-----+--------------+
       |             |              |              |
 clock-client1  clock-client2  clock-client3  clock-client4
     -8 s           +6 s           -4 s          +10 s
```

## Project structure

```text
clock-synchronization/
├── docker-compose.yml
├── master/
│   ├── Dockerfile
│   └── master.py
├── client/
│   ├── Dockerfile
│   └── client.py
└── experiments/          # env files for Parts J and K
    ├── exp1.env
    ├── exp2.env
    ├── exp3.env
    ├── faulty.env
    └── faulty-excluded.env
```

## Algorithm

Messages are JSON over TCP on port 5000.

1. Master sends `CLOCK_REQUEST` to every client; each replies with its clock.
2. Offset of each client relative to the master, compensated for network delay:
   `offset_i = (client_clock + RTT / 2) - master_clock_at_reply`
3. `average = (0 + offset_1 + ... + offset_n) / (n + 1)` (the master's own offset is 0)
4. `correction_i = average - offset_i`, and the master's correction is `average`.
5. Master sends `CORRECTION` to each client and applies its own.
6. Master polls again and prints the final clocks and the remaining error.

Corrections are relative adjustments, not absolute times, so the delay of the correction message doesn't affect the result.

## Running

```bash
docker network create clock-net
docker network ls

docker compose up --build --abort-on-container-exit
```

In another terminal while it's running:

```bash
docker ps
docker network inspect clock-net
```

The master prints the report and exits; `--abort-on-container-exit` then stops the clients. Each client's log shows its clock before and after the correction. Clean up with `docker compose down`.

### Environment variables

| Variable | Service | Meaning |
|---|---|---|
| `CLIENT_ID` | client | Name shown in the output |
| `CLOCK_OFFSET` | all | Initial clock offset in seconds (negative = behind) |
| `CLIENTS` | master | Comma-separated `host:port` list of clients |
| `OUTLIER_THRESHOLD` | master | Exclude clients with `\|offset\| >` this many seconds from the average; `0` = off |
| `EXPERIMENT` | master | Label used in the output and the results table |

In `docker-compose.yml` these are set from `MASTER_OFFSET`, `CLIENT1_OFFSET` ... `CLIENT4_OFFSET`, `OUTLIER_THRESHOLD` and `EXPERIMENT`. The defaults are the lab's suggested offsets (0, -8, +6, -4, +10).

## Experiments

```bash
docker compose --env-file experiments/exp1.env up --build --abort-on-container-exit
docker compose --env-file experiments/exp2.env up --abort-on-container-exit
docker compose --env-file experiments/exp3.env up --abort-on-container-exit
docker compose --env-file experiments/faulty.env up --abort-on-container-exit
docker compose --env-file experiments/faulty-excluded.env up --abort-on-container-exit
```

| File | Master | Client 1 | Client 2 | Client 3 | Client 4 | Outlier removal |
|---|---:|---:|---:|---:|---:|---|
| `exp1.env` | 0 | -5 | +5 | -3 | +3 | off |
| `exp2.env` | 0 | -15 | +10 | -5 | +20 | off |
| `exp3.env` | +2 | -12 | +7.5 | -1.5 | +4 | off |
| `faulty.env` | 0 | -5 | +5 | +3 | +12600 (15:30:00 vs 12:00:00) | off |
| `faulty-excluded.env` | 0 | -5 | +5 | +3 | +12600 | threshold 60 s |

At the end of each run the master prints a Markdown results table (Part L). Paste those rows into the results section below.

### Outlier handling

**Outlier removal is an implementation enhancement and is not part of the basic Berkeley algorithm.** With `OUTLIER_THRESHOLD > 0`, a client whose `|offset|` exceeds the threshold is left out of the average. It still receives a correction, so it is brought back in line with the others.

Without it, the +12600 s clock pulls the average to about +2520 s, so every healthy clock jumps forward by about 42 minutes. With a 60 s threshold, the average stays at about +0.75 s and only the faulty clock moves a long way.

## Results

<!-- Paste the results tables printed by the master for each experiment here. -->

## Answers to the questions

1. **Why a coordinator?** Someone has to collect every clock, compute one agreed average and tell each node how much to adjust. A single coordinator makes this simple and avoids every node talking to every other node.
2. **Why no accurate external time server?** The goal is internal synchronization: the nodes agree with each other. The result is the group's average time, not UTC. This suits systems with no reference clock.
3. **Why offsets relative to the master?** The master needs one common reference to compare the clocks. Its own clock is the one it can read directly, so every difference is measured against it.
4. **Why the average offset?** Averaging spreads the error over all nodes. No single clock is trusted, and random errors partly cancel out.
5. **Why does the master adjust its own clock?** The master is just another participant. Its clock can be wrong too, and the agreed time is the average, which is usually not the master's time.
6. **What happens with a very large clock error?** That node drags the average toward itself. Every healthy node is then "corrected" away from the true time (about 42 minutes in `faulty.env`).
7. **How does an outlier affect the average?** The mean isn't robust: one value of +12600 s among small offsets moves the average by 12600 / 5 ≈ 2520 s.
8. **Why exclude faulty nodes?** The faulty clock no longer distorts the agreed time. It still receives a correction, so it gets fixed as well.
9. **What if a client doesn't respond?** The master should time out and leave that client out of the round. Here the master waits up to 30 s at startup and otherwise stops with an error. The client gets synchronized in a later round once it's back.
10. **What if the master fails?** No synchronization happens until a new coordinator is chosen, for example with an election algorithm such as Bully or Ring. The clocks keep drifting in the meantime.
11. **Difference from Cristian's algorithm?** Cristian's algorithm is client-driven (pull): each client asks an accurate time server and copies its time (plus RTT/2). Berkeley's is coordinator-driven (push): the master polls everyone, computes an average, and sends relative corrections. No node is assumed to be accurate.
12. **Effect of the number of clients?** More clients give a more stable average and soften random errors. But they also mean more messages per round (2n: one request and one correction per client), more load on the master, and a longer round, so clocks drift more during it.
