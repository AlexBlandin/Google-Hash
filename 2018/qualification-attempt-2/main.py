"""
Google Hash 2018 qualifier.

Copyright 2021 Alex Blandin
"""

from itertools import count
from math import ceil
from pathlib import Path
from random import randint, sample

import numpy as np
from tqdm import tqdm


def main() -> None:  # noqa: C901, D103, PLR0915
  # CyCloMaTiC CoMPleXiTy ToO HiGH
  files = list(Path().glob("*.in"))
  print(f"Found {len(files)} input files")  # noqa: T201
  for path in files:
    name, lines = path.stem, []
    with path.open(encoding="utf8") as o:
      lines = o.readlines()
    # rows, columns, fleet size, number of rides, bonus for starting on time, time range of sim (1..T inc.)
    rows, columns, fleet_size, ride_count, bonus, duration = map(int, lines[0].split())

    # rides[0] = a, b, x, y, s, f
    # a, b, x, y = start intersection row, start intersection column, end intersection row, end intersection column
    # s, f = earliest start, latest allowed finish (f <= T)
    (*rides,) = (list(map(int, a.split())) for a in lines[1:])
    for ride in rides:
      ride.append(abs(ride[0] - ride[2]) + abs(ride[1] - ride[3]))
    print(f"{name}: R, C, F, N, B, T = {rows, columns, fleet_size, ride_count, bonus, duration}")  # noqa: T201

    # "efficiency"
    np_int = np.int64
    if ride_count < 2**7:
      np_int = np.int8
    elif ride_count < 2**15:
      np_int = np.int16
    elif ride_count < 2**31:
      np_int = np.int32
    elif ride_count >= 2**63:
      msg = f"Too many rides N ({ride_count}), needs to be storable in an int64"
      raise ValueError(msg)
    fleet = np.negative(np.ones((fleet_size, ride_count), dtype=np_int))  # -1 is our "empty" value
    for ride in range(ride_count):
      for i, _ in enumerate(fleet):
        if ride % fleet_size == i:
          fleet[i, ride // fleet_size] = ride

    score, old_score, old_fleet = 0, 0, np.copy(fleet)
    try:  # gradient descent by analogy, seemed like a good idea at the time
      with tqdm(count(), unit="sim") as sims:
        for _ in sims:
          """
          Current timings on 8700k ~4.3GHz
          a_example: 166k sim/s
          b_should_be_easy: 5k sim/s
          c_no_hurry: 804 sim/s
          d_metropolis: 152 sim/s
          e_high_bonus: 175 sim/s
          """

          tf, gf = 4, 4
          take, give = fleet_size // tf if fleet_size // tf else 1, fleet_size // gf if fleet_size // gf else 1

          width = min(3, ride_count)
          radius = width // 2

          generations = 5
          for _ in range(generations):
            # modify columns in batches
            for column in range(ceil(fleet_size / width)):
              column = min(column * width + radius, ride_count - 1)  # noqa: PLW2901
              swaps = zip(sample(range(fleet_size), take), sample(range(fleet_size), take), strict=False)
              gives = zip(sample(range(fleet_size), give), sample(range(fleet_size), give), strict=False)
              # swap values
              for a, b in swaps:
                target = min(column + randint(-radius, radius), ride_count - 1)
                fleet[b, target], fleet[a, column] = fleet[a, column], fleet[b, target]
              # give away values
              for a, b in gives:
                if fleet[b, ride_count - 1] != -1:
                  fleet[b, fleet[b] == -1] = fleet[a, column]
                  fleet[a, column] = -1
                  np.roll(fleet[a, column:], -1)

            # simulate from start to finish for each car with independent internal clocks
            score = 0
            for car in fleet:
              time, x, y = 0, 0, 0
              for i in car[car >= 0]:
                ride, start_time = rides[i], time
                arrival = time + abs(ride[0] - x) + abs(ride[1] - y)
                time = max(arrival, ride[4])
                time += ride[6]  # we can go the distance
                x, y = ride[2], ride[3]
                score += (
                  ride[6] + (bonus if start_time == ride[4] else 0) if 0 < time < duration and time <= ride[5] else 0
                )

            if score > old_score:
              old_fleet, old_score = np.copy(fleet), score
              break
          else:
            fleet, score = np.copy(old_fleet), old_score

          sims.set_postfix_str(f"{score} score", refresh=False)

    except KeyboardInterrupt:
      print(f"Stopped by user, {score} score")  # noqa: T201

    with Path(f"{name}.out").open("w", encoding="utf8") as o:
      for car in fleet:
        assigned = list(map(str, car[car >= 0]))
        if len(assigned):
          o.write(f"{len(assigned)} ")
          o.write(" ".join(assigned))  # sorted list of rides, order in which THE CAR performs the ride
        else:
          o.write("0")
        o.write("\n")


if __name__ == "__main__":
  main()
