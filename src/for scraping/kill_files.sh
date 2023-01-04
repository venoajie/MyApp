#!/bin/bash
if pgrep process_name 2>/dev/null; then
echo "Terminating process_name"
pkill process_name
fi