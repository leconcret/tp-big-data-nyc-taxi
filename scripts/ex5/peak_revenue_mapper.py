#!/usr/bin/env python3
import sys, csv
from datetime import datetime

DAYS = ["LUNDI", "MARDI", "MERCREDI", "JEUDI", "VENDREDI", "SAMEDI", "DIMANCHE"]

for row in csv.reader(sys.stdin):
    try:
        if not row or row[0] == "VendorID":
            continue
        pickup = datetime.strptime(row[1], "%Y-%m-%d %H:%M:%S")
        fare = float(row[10])
        tip = float(row[13])
        total = float(row[16])
        if fare > 0 and 0 < total < 500:
            key = f"{DAYS[pickup.weekday()]}-{pickup.hour:02d}"
            print(f"{key}\t{fare:.2f}:{tip:.2f}:1")
    except Exception:
        continue
