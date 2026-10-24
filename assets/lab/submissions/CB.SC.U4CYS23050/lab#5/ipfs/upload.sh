#!/bin/bash
set -e

# Initialize the IPFS repo only if it hasn't been initialized already
if [ ! -d "$HOME/.ipfs" ]; then
    echo "Initializing IPFS repository..."
    ipfs init
fi

echo ""
echo "Uploading /app/sample.txt to IPFS..."

# Add the file to IPFS. -Q prints only the resulting hash (CID), nothing else
HASH=$(ipfs add -Q /app/sample.txt)

echo ""
echo "=========================================="
echo "File uploaded successfully!"
echo "IPFS Content Hash (CID): $HASH"
echo "=========================================="
echo ""
