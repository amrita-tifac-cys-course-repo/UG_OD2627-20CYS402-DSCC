# Raft Consensus in Docker

A 5-node Raft cluster that keeps a replicated key-value store. Each node is a container that talks to the others over HTTP/JSON. It is written in plain Python with no dependencies.

It implements the two core parts of Raft:

- **Leader election**: random election timeouts, `RequestVote`, majority vote, terms, and stepping down on a higher term. Votes go only to candidates whose log is at least as up to date as the voter's.
- **Log replication**: the leader appends client commands to its log and sends them with `AppendEntries`, which also serves as the heartbeat. Followers run the consistency check on `prev_log_index`/`prev_log_term`, remove conflicting entries, and accept the rest. An entry is committed once a majority stores it (current term only), then applied to the key-value store.

## Run

```bash
docker compose up --build
```

Watch the logs. Within a few seconds one node times out, becomes a candidate, collects 3 of 5 votes and becomes leader.

In a **second terminal**:

```bash
docker compose run --rm client status          # table of all nodes
docker compose run --rm client set x 5         # write through the leader
docker compose run --rm client set y hello
docker compose run --rm client del x
docker compose run --rm client watch           # live view, Ctrl+C to stop
```

## Demo scenarios

**1. Leader crash and re-election**
```bash
docker compose run --rm client status          # note the leader, e.g. node3
docker stop node3
docker compose run --rm client status          # new leader, higher term, data intact
docker compose run --rm client set z 42        # writes still work with 4/5 nodes
```

**2. Node rejoins and catches up**
```bash
docker start node3                             # starts empty (in-memory state)
docker compose run --rm client status          # node3 now has the full log
```

**3. Freeze a node (keeps its memory)**
```bash
docker pause node2      # node2 misses heartbeats and writes
docker compose run --rm client set a 1
docker unpause node2    # node2 gets the missing entries from the leader
```

**4. Lose the majority**
```bash
docker stop node1 node2 node4                  # only 2 of 5 alive
docker compose run --rm client set w 1         # fails: no leader can be elected
docker start node1 node2 node4                 # cluster recovers
```

## Talk to a node directly

Each node is also exposed on the host at ports 8001 to 8005:

```bash
curl localhost:8001/status
curl -X POST localhost:8003/submit -H "Content-Type: application/json" -d '{"command":"SET k v"}'
```

`submit` only works on the leader. A follower replies with `not the leader` and names the leader.

## Settings (environment variables)

| Variable | Default | Meaning |
|---|---|---|
| `ELECTION_MIN_MS` / `ELECTION_MAX_MS` | 1500 / 3000 | Random election timeout range |
| `HEARTBEAT_MS` | 500 | Leader heartbeat interval |
| `RPC_TIMEOUT_MS` | 400 | Timeout for calls to other nodes |

The timings are slower than real Raft so the logs are easy to follow.

## Simplifications

- Term, vote and log are kept in memory, not on disk. A node restarted with `docker stop`/`start` comes back empty and gets the log again from the leader. Real Raft persists these, and losing a node's vote record can break safety in rare cases. Use `docker pause` when you want a node to keep its state.
- Not included: log compaction (snapshots) and cluster membership changes.
- On a log mismatch the leader backs up `next_index` one entry at a time.

## Push to Docker Hub

```bash
docker build -t <your-username>/raft-demo:latest .
docker push <your-username>/raft-demo:latest
```
Then change `image: raft-demo:latest` in `docker-compose.yml` to `<your-username>/raft-demo:latest` and remove the `build: .` line.

## Without Docker

```bash
NODE_ID=node1 PORT=9001 PEERS=localhost:9002,localhost:9003 python raft_node.py
NODE_ID=node2 PORT=9002 PEERS=localhost:9001,localhost:9003 python raft_node.py
NODE_ID=node3 PORT=9003 PEERS=localhost:9001,localhost:9002 python raft_node.py
NODES=localhost:9001,localhost:9002,localhost:9003 python client.py status
```
