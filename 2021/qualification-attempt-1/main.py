"""
Google Hash 2021 qualifier.

Copyright 2021 Alex Blandin
"""

from dataclasses import dataclass
from math import log
from pathlib import Path


@dataclass(slots=True)
class Street:  # noqa: D101
  starts_at: int
  ends_at: int
  length: int
  weight: int


@dataclass
class Intersection:  # noqa: D101
  __slots__ = ["ID", "inputs", "order", "outputs"]
  ID: int
  inputs: list[Street]  # Streets that end here
  outputs: list[Street]  # Streets that start here
  order: list[tuple[str, int]]  # "order and duration" of green lights, list of (street name, time T) pairs

  def __str__(self) -> str:  # noqa: D105
    return f"{self.ID}\n{len(self.order)}\n{chr(10).join(f'{sn} {T}' for sn, T in self.order)}\n"  # chr(10) is "\n"


def read(name):  # noqa: ANN001, ANN201, D103
  with Path(f"{name}.txt").open(encoding="utf8") as f:
    lines = [line.split() for line in f]
  _d, _n, _s, _v, _f = map(int, lines[0])
  streets = {SN: Street(int(B), int(E), int(L), 0) for B, E, SN, L in lines[1 : _s + 1]}
  paths = [streets for _, *streets in lines[_s + 1 :]]
  intersections = [Intersection(i, [], [], []) for i in range(_n)]
  for streetname, street in streets.items():
    intersections[street.ends_at].inputs.append(streetname)
    intersections[street.starts_at].outputs.append(streetname)
  return _d, _n, _s, _v, _f, streets, paths, intersections


def solve(name, D, N, S, V, F, streets: dict[str, Street], paths: list[list[str]], intersections: list[Intersection]):  # noqa: ANN001, ANN201, ARG001, D103, N803, PLR0913
  # streets: name -> Street
  # paths: each path is an ordered list of streets
  # intersections: ID -> Intersection

  for path in paths:
    for street in path:
      streets[street].weight += 1
  max_weight = max([street.weight for street in streets.values()])
  min_weight = min([street.weight for street in streets.values()])

  def curve(t: int, weight: int) -> int:
    return min(
      max(
        round(
          (D - 1) * (log(weight + 1) - log(min_weight + 1)) / max((log(max_weight + 1) - log(min_weight + 1)) + 1, 1)
        )
        // 256,
        1,
      ),
      D,
    )  # logarithmic mapping of minWeight^2..maxWeight^2 to 1..D
    return min(
      max(round((D - 1) * ((weight**2) - (min_weight**2)) / max(((max_weight) - (min_weight)) + 1, 1)) // 64, 1),
      D,
    )  # quadratic mapping of minWeight^2..maxWeight^2 to 1..D
    return min(
      max(round((D - 1) * (weight - min_weight) / max((max_weight - min_weight) + 1, 1)) // 64, 1), D
    )  # linear mapping of minWeight..maxWeight to 1..D
    return t  # identity mapping (works ~~infuriatingly~~ surprisingly well)

  for intersection in intersections:
    intersection.order = [
      (street, curve(t, streets[street].weight, len(intersection.inputs)))
      for t, street in enumerate(sorted(intersection.inputs, key=lambda street: streets[street].weight), start=1)
    ]

  return intersections


if __name__ == "__main__":
  for name in "abcdef":
    intersections = solve(name, *read(name))
    with Path(f"{name}.out").open("w+", encoding="utf8") as f:
      f.write(f"{len(intersections)}\n")
      f.writelines(map(str, intersections))
