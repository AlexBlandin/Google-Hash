"""
Google Hash 2018 qualifier.

Copyright 2021 Alex Blandin
"""

from pathlib import Path

import numpy as np

##
# Quick simulation test to ensure it was correct (I caught a few bugs :P and also use more efficient numpy arrays if we can)  # noqa: E501
##

lines = []
with Path("a_example.in").open(encoding="utf8") as o:
  lines = o.readlines()
# rows, columns, fleet size, number of rides, bonus for starting on time, time range of sim (1..T inc.)
R, C, F, N, B, T = list(map(int, lines[0].split()))

# rides[0] = a, b, x, y, s, f
# a, b, x, y = start intersection row, start intersection column, end intersection row, end intersection column
# s, f = earliest start, latest allowed finish (f <= T)
rides = [list(map(int, a.split())) for a in lines[1:]]
for ride in rides:
  ride.append(abs(ride[0] - ride[2]) + abs(ride[1] - ride[3]))

fleet, np_int = None, np.int64
if N < 2**7:
  np_int = np.int8
elif N < 2**15:
  np_int = np.int16
elif N < 2**31:
  np_int = np.int32
elif N >= 2**63:
  print(f"Too many rides ({N}) for numpy, needs to be storable in an int64")  # noqa: T201
fleet = np.negative(np.ones((F, N), dtype=np_int))
fleet[0, 0] = 2
fleet[1, 0], fleet[1, 1] = 0, 1

score = 0
for car in fleet:
  time, x, y = 0, 0, 0
  for i in car:
    if i >= 0:
      ride, start_time = rides[i], time
      arrival = time + abs(ride[0] - x) + abs(ride[1] - y)
      time = max(arrival, ride[4])
      time += ride[6]  # we can go the distance
      x, y = ride[2], ride[3]
      score += ride[6] + (B if start_time == ride[4] else 0) if 0 < time < T and time <= ride[5] else 0
print(score)  # noqa: T201

with Path("a_example.out").open("w", encoding="utf8") as o:
  for car in fleet:
    assigned = list(map(str, filter(lambda x: x >= 0, car)))
    if assigned:
      o.write(f"{len(assigned)} ")
      o.write(" ".join(assigned))
      # must be a sorted list of rides, sorted by the order THE CAR performs the ride (ie, if the car does ride X before ride Y, then X is before Y in car)  # noqa: E501
    else:
      o.write("0")
    o.write("\n")
