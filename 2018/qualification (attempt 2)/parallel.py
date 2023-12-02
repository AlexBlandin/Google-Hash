from multiprocessing import Pool
from random import sample, randint
from itertools import count
from math import ceil
from tqdm import tqdm
import numpy as np


def main(queue, lines):
  # rows, columns, fleet size, number of rides, bonus for starting on time, time range of sim (1..T inc.)
  R, C, F, N, B, T = map(int, lines[0].split())

  # rides[0] = a, b, x, y, s, f
  # a, b, x, y = start intersection row, start intersection column, end intersection row, end intersection column
  # s, f = earliest start, latest allowed finish (f <= T)
  (*rides,) = map(lambda a: list(map(int, a.split())), lines[1:])
  for ride in rides:
    ride.append(abs(ride[0] - ride[2]) + abs(ride[1] - ride[3]))
  # print(f"{name}: R, C, F, N, B, T = {R, C, F, N, B, T}")

  # "efficiency"
  np_int = np.int64
  if 2**7 > N:
    np_int = np.int8
  elif 2**15 > N:
    np_int = np.int16
  elif 2**31 > N:
    np_int = np.int32
  elif 2**63 <= N:
    raise ValueError(f"Too many rides N ({N}), needs to be storable in an int64")
  fleet = np.negative(np.ones((F, N), dtype=np_int))  # -1 is our "empty" value
  for ride in range(N):
    for i, car in enumerate(fleet):
      if ride % F == i:
        fleet[i, ride // F] = ride

  score, old_score, old_fleet = 0, 0, np.copy(fleet)
  # gradient descent by analogy, seemed like a good idea at the time
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
      take, give = F // tf if F // tf else 1, F // gf if F // gf else 1

      width = min(3, N)
      radius = width // 2

      generations = 5
      for _ in range(generations):
        # modify columns in batches
        for column in range(ceil(F / width)):
          column = min(column * width + radius, N - 1)
          swaps = zip(sample(range(F), take), sample(range(F), take))
          gives = zip(sample(range(F), give), sample(range(F), give))
          # swap values
          for a, b in swaps:
            target = min(column + randint(-radius, radius), N - 1)
            fleet[b, target], fleet[a, column] = fleet[a, column], fleet[b, target]
          # give away values
          for a, b in gives:
            if fleet[b, N - 1] != -1:
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
            time = arrival if arrival >= ride[4] else ride[4]
            time += ride[6]  # we can go the distance
            x, y = ride[2], ride[3]
            score += ride[6] + (B if start_time == ride[4] else 0) if 0 < time < T and time <= ride[5] else 0

        if score > old_score:
          old_fleet, old_score = np.copy(fleet), score
          break
      else:
        fleet, score = np.copy(old_fleet), old_score

      # synchronise top score
      ...

      sims.set_postfix_str(f"{score} score", refresh=False)


if __name__ == "__main__":
  try:
    files = ["a_example.in", "b_should_be_easy.in", "c_no_hurry.in", "d_metropolis.in", "e_high_bonus.in"]
    path = files[3]
    with open(path) as o:
      lines = o.readlines()
    with Pool() as p:
      p.starmap(main, zip([path] * 8, [lines] * 8))
  except KeyboardInterrupt:
    print(f"Stopped by user, top score is {top_score}")
  """
  File format
  The submission file must contain F lines, one for each vehicle in the fleet.
  Each line describing the rides of a vehicle must contain the following integers separated by single spaces:
  ● M – number of rides assigned to the vehicle (0 ≤ M ≤ N)
  ● R 0 , R 1 , ..., R M-1 – ride numbers assigned to the vehicle, in the order in which the vehicle will perform
  them (0 ≤ Ri < N)
  Any ride can be assigned to a vehicle at most once . That is, it is not allowed to assign the same ride to
  two or more different vehicles. It is also not allowed to assign the same ride to one vehicle more than once.
  It is not required to assign all rides to vehicles – some rides can be skipped.
  Example
  1 0      this vehicle is assigned 1 ride: [0]
  2 2 1    this vehicle is assigned 2 rides: [2, 1]

  Validation
  In order for the submission to be accepted, it must follow the format requirements described above.

  Scoring
  Each ride completed before its latest finish earns the number of points equal to the distance between the
  start intersection and the finish intersection.
  Additionally, each ride which started exactly in its earliest allowed start step gets an additional timeliness
  bonus of B.
  The total score of the submission is the sum of all points earned by all rides completed by all vehicles.
  For example, with the example input file and the example submission file above, there are two vehicles.
  Vehicle 0 handles one ride:
  ● ride 0, start at step 2, finish at step 6. Earns points: 4 (distance) + 2 (bonus) = 6
  Vehicle 1 handle two rides:
  ● ride 2, start at step 2, finish at step 4. Earns points: 2 (distance) + 0 (no bonus) = 2
  ● ride 1, start at step 5, finish at step 7. Earns points: 2 (distance) + 0 (no bonus) = 2
  The total score for this submission is 6 + 2 + 2 = 10.
  """

  with open("d_metropolis.out") as r:
    lines = r.readlines()
    for line in map(str.strip, lines):
      count, *rides = line.split()  # handles "0" case anyway

  if top_score > recorded_score:
    with open("d_metropolis.out", "w") as o:
      for car in top_fleet:
        assigned = list(map(str, car[car >= 0]))
        if len(assigned):
          o.write(f"{len(assigned)} ")
          o.write(" ".join(assigned))  # sorted list of rides, order in which THE CAR performs the ride
        else:
          o.write("0")
        o.write("\n")
