#!/usr/bin/env python3
import sys, csv
from datetime import datetime

DAYS = ["Lun", "Mar", "Mer", "Jeu", "Ven", "Sam", "Dim"]

for row in csv.reader(sys.stdin):
    try:
        if not row or row[0] == "VendorID":
            continue
        pickup = datetime.strptime(row[1], "%Y-%m-%d %H:%M:%S")
        dropoff = datetime.strptime(row[2], "%Y-%m-%d %H:%M:%S")
        distance = float(row[4])
        duration_h = (dropoff - pickup).total_seconds() / 3600
        if distance > 0 and duration_h > 0:
            speed = distance / duration_h
            if 0 < speed < 120:
                key = f"{DAYS[pickup.weekday()]}-{pickup.hour:02d}"
                print(f"{key}\t{distance}:{duration_h}:{speed}:1")
    except Exception:
        continue
