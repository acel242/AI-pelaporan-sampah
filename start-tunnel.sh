#!/bin/bash
PORT=$1
LOGFILE=$2
NAME=$3
echo "Starting $NAME tunnel to localhost:$PORT"
cloudflared tunnel --url http://localhost:$PORT > $LOGFILE 2>&1 &
TUNNEL_PID=$!
echo "Tunnel PID: $TUNNEL_PID"
sleep 8
TUNNEL_URL=$(grep -o 'https://[^ ]*trycloudflare.com' $LOGFILE | head -1)
echo "$NAME URL: $TUNNEL_URL"
echo "$TUNNEL_URL" > "$LOGFILE.url"
wait $TUNNEL_PID
