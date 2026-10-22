FROM ubuntu:22.04

LABEL maintainer="Jashwanth <Jashwanth>"


ENV DEBIAN_FRONTEND=noninteractive

ENV KUBO_VERSION=v0.42.0


ENV IPFS_PATH=/data/ipfs


RUN apt-get update && \
    apt-get install -y --no-install-recommends wget ca-certificates && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /tmp


RUN wget "https://dist.ipfs.tech/kubo/${KUBO_VERSION}/kubo_${KUBO_VERSION}_linux-amd64.tar.gz"

RUN tar -xvzf "kubo_${KUBO_VERSION}_linux-amd64.tar.gz"


RUN cd kubo && bash install.sh

RUN ipfs --version

RUN mkdir -p "$IPFS_PATH"

RUN ipfs init

WORKDIR /app
COPY Lab1.txt .


RUN ipfs add Lab1.txt

EXPOSE 4001 5001 8080

CMD ["sh", "-c", "echo 'CID (hash) of Lab1.txt:' && ipfs add -q /app/Lab1.txt"]