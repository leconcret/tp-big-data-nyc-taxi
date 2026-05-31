#!/usr/bin/env python3
import sys, csv
from datetime import datetime

for row in csv.reader(sys.stdin):
    try:
        if not row or row[0] == "VendorID":
            continue
        pickup = datetime.strptime(row[1], "%Y-%m-%d %H:%M:%S")
        print(f"{pickup.hour:02d}\t1")
    except Exception:
        continue
