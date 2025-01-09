"""
Google Hash 2021 qualifier.

Copyright 2021 Alex Blandin
"""

from math import log
from pathlib import Path


class Struct(dict):  # noqa: D101
  __getattr__, __setattr__ = dict.__getitem__, dict.__setitem__


def read(name):  # noqa: ANN001, ANN201, D103
  with Path(f"{name}.txt").open(encoding="utf8") as f:
    lines = list(map(str.split, f.readlines()))
  _d, _n, _s, _v, _f = map(int, lines[0])
  streets = {SN: Struct(startsAt=int(B), endsAt=int(E), length=int(L), weight=0) for B, E, SN, L in lines[1 : _s + 1]}
  paths, intersections = (
    [streets for _, *streets in lines[_s + 1 :]],
    [Struct(ID=i, inputs=[], outputs=[], order=[]) for i in range(_n)],
  )
  for streetname, street in streets.items():
    intersections[street.endsAt].inputs.append(streetname)
    intersections[street.startsAt].outputs.append(streetname)
  return _d, _n, _s, _v, _f, streets, paths, intersections


def solve(name, _d, _n, _s, _v, _f, streets, paths, intersections):  # noqa: ANN001, ANN201, ARG001, D103
  for path in paths:
    for street in path:
      streets[street].weight += 1
  min_weight, max_weight = (
    min([street.weight for street in streets.values()]),
    max([street.weight for street in streets.values()]),
  )

  def curve(t, weight):  # noqa: ANN001, ANN202, ARG001
    # logarithmic mapping of minWeight^2..maxWeight^2 to 1..D
    return min(
      max(
        round(
          (_d - 1) * (log(weight + 1) - log(min_weight + 1)) / max((log(max_weight + 1) - log(min_weight + 1)) + 1, 1)
        )
        // 256,
        1,
      ),
      _d,
    )
    # quadratic map of minWeight^2..maxWeight^2 to 1..D
    # return min(max(round((D-1)*((weight**2)-(minWeight**2))/max(((maxWeight)-(minWeight)) + 1, 1))//64,1), D)
    # linear mapping of minWeight..maxWeight to 1..D
    # return min(max(round((D-1)*(weight-minWeight)/max((maxWeight-minWeight) + 1, 1))//64,1), D)
    # # identity mapping (works ~~infuriatingly~~ surprisingly well)
    # return t

  for intersection in intersections:
    intersection.order = [
      (street, curve(t, streets[street].weight))
      for t, street in enumerate(sorted(intersection.inputs, key=lambda street: streets[street].weight), start=1)
    ]
  return intersections


if __name__ == "__main__":
  for name in "abcdef":
    intersections = solve(name, *read(name))
    with Path(f"{name}.out").open("w+", encoding="utf8") as f:
      f.write(f"{len(intersections)}\n")
      f.writelines(
        [f"{self.ID}\n{len(self.order)}\n{'\n'.join(f'{sn} {T}' for sn, T in self.order)}\n" for self in intersections]
      )
