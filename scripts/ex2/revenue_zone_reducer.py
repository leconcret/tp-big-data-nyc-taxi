#!/usr/bin/env python3
import sys

current = None
count = 0
fare_sum = tip_sum = total_sum = 0.0

def emit(zone, count, fare_sum, tip_sum, total_sum):
    if count == 0:
        return
    avg_fare = fare_sum / count
    avg_tip = tip_sum / count
    avg_total = total_sum / count
    tip_rate = (tip_sum / fare_sum * 100) if fare_sum > 0 else 0
    print(f"{zone}\t{count}\t{avg_fare:.2f}\t{avg_tip:.2f}\t{avg_total:.2f}\t{tip_rate:.1f}")

for line in sys.stdin:
    line = line.strip()
    if not line:
        continue
    zone, values = line.split("\t")
    try:
        fare, tip, total, c = values.split(":")
        fare, tip, total, c = float(fare), float(tip), float(total), int(c)
    except Exception:
        continue
    if current is not None and zone != current:
        emit(current, count, fare_sum, tip_sum, total_sum)
        count = 0
        fare_sum = tip_sum = total_sum = 0.0
    current = zone
    count += c
    fare_sum += fare
    tip_sum += tip
    total_sum += total

if current is not None:
    emit(current, count, fare_sum, tip_sum, total_sum)
