#!/bin/bash

# Kill any running instances of the application
echo "Killing any running instances of the application..."
pkill -f "python3 run.py" || true
killall -9 Python || true

echo "All instances killed."
