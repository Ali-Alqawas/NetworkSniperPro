#!/bin/bash
# Network Sniper Pro - Launcher
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
exec sudo python3 "$DIR/main.py"
