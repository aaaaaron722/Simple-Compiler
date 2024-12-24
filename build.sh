#!/bin/bash

# Check the parameter
if [ "$#" -ne 1 ]; then
    echo "Syntax: $0 <FileName>"
    exit 1
fi

# Retrieve
FILE="$1"

# Check file exist or not
if [ ! -f "$FILE" ]; then
    echo "Error: File '$FILE' not exist。"
    exit 1
fi

# Executing
python3 main.py "$FILE"
python3 out.py