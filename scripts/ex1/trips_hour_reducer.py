#!/usr/bin/env python3
import sys

current = None
count = 0

for line in sys.stdin:
    line = line.strip()
    if not line:
        continue
    hour, value = line.split("\t")
    if current is not None and hour != current:
        print(f"{current}\t{count}")
        count = 0
    current = hour
    count += int(value)

if current is not None:
    print(f"{current}\t{count}")
