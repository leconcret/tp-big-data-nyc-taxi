#!/usr/bin/env python3
import sys

current = None
count = 0
fare_sum = tip_sum = 0.0

def emit(key):
    global count, fare_sum, tip_sum
    if count == 0:
        return
    fare_avg = fare_sum / count
    tip_avg = tip_sum / count
    tip_rate = (tip_sum / fare_sum * 100) if fare_sum > 0 else 0
    print(f"{key}\t{count}\t{fare_avg:.2f}\t{tip_avg:.2f}\t{tip_rate:.1f}\t{fare_sum:.2f}")

for line in sys.stdin:
    line = line.strip()
    if not line:
        continue
    key, values = line.split("\t")
    try:
        fare, tip, c = values.split(":")
        fare, tip, c = float(fare), float(tip), int(c)
    except Exception:
        continue
    if current is not None and key != current:
        emit(current)
        count = 0
        fare_sum = tip_sum = 0.0
    current = key
    count += c
    fare_sum += fare
    tip_sum += tip

if current is not None:
    emit(current)
