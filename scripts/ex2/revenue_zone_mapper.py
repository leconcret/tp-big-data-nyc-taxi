#!/usr/bin/env python3
import sys, csv

for row in csv.reader(sys.stdin):
    try:
        if not row or row[0] == "VendorID":
            continue
        zone = row[7]
        fare = float(row[10])
        tip = float(row[13])
        total = float(row[16])
        if zone and 0 < fare < 500 and tip >= 0 and 0 < total < 500:
            print(f"{zone}\t{fare}:{tip}:{total}:1")
    except Exception:
        continue
