#!/usr/bin/env python3
import sys

current = None
count = 0
distance_sum = duration_sum = speed_sum = 0.0
min_speed = max_speed = None

def emit(key):
    global count, distance_sum, duration_sum, speed_sum, min_speed, max_speed
    if count == 0:
        return
    avg_distance = distance_sum / count
    avg_duration_min = (duration_sum / count) * 60
    avg_speed = speed_sum / count
    print(f"{key}\t{count}\t{avg_distance:.2f}\t{avg_duration_min:.1f}\t{avg_speed:.1f}\t{min_speed:.1f}\t{max_speed:.1f}")

for line in sys.stdin:
    line = line.strip()
    if not line:
        continue
    key, values = line.split("\t")
    try:
        d, dur, sp, c = values.split(":")
        d, dur, sp, c = float(d), float(dur), float(sp), int(c)
    except Exception:
        continue
    if current is not None and key != current:
        emit(current)
        count = 0
        distance_sum = duration_sum = speed_sum = 0.0
        min_speed = max_speed = None
    current = key
    count += c
    distance_sum += d
    duration_sum += dur
    speed_sum += sp
    min_speed = sp if min_speed is None else min(min_speed, sp)
    max_speed = sp if max_speed is None else max(max_speed, sp)

if current is not None:
    emit(current)
