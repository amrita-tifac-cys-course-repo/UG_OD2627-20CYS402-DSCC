#!/bin/sh

export IPFS_PATH=/data/ipfs

echo "Checking IPFS repository..."

# Initialize only if the config file does not exist
if [ ! -f "$IPFS_PATH/config" ]; then
    echo "Initializing IPFS..."
    ipfs init
fi

echo "Starting daemon..."
ipfs daemon &
PID=$!

echo "Waiting for daemon..."
sleep 8

echo "Uploading file..."

CID=$(ipfs add -Q /sample.txt)

echo "=============================="
echo "CID: $CID"
echo "=============================="

wait $PID