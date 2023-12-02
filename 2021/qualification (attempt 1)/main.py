from dataclasses import dataclass
from math import log


@dataclass
class Street:
  __slots__ = ["startsAt", "endsAt", "length", "weight"]
  startsAt: int
  endsAt: int
  length: int
  weight: int


@dataclass
class Intersection:
  __slots__ = ["ID", "inputs", "outputs", "order"]
  ID: int
  inputs: list[Street]  # Streets that end here
  outputs: list[Street]  # Streets that start here
  order: list[(str, int)]  # "order and duration" of green lights, list of (street name, time T) pairs

  def __str__(self):
    return f"{self.ID}\n{len(self.order)}\n{chr(10).join(f'{sn} {T}' for sn, T in self.order)}\n"  # chr(10) is "\n"


def read(name):
  with open(f"{name}.txt") as f:
    lines = [line.split() for line in f.readlines()]
  D, I, S, V, F = map(int, lines[0])
  streets = {SN: Street(int(B), int(E), int(L), 0) for B, E, SN, L in lines[1: S + 1]}
  paths = [streets for _, *streets in lines[S + 1:]]
  intersections = [Intersection(i, [], [], []) for i in range(I)]
  for streetname, street in streets.items():
    intersections[street.endsAt].inputs.append(streetname)
    intersections[street.startsAt].outputs.append(streetname)
  return D, I, S, V, F, streets, paths, intersections


def solve(name, D, I, S, V, F, streets, paths, intersections):
  streets: dict[str, Street]  # street name -> Street
  paths: list[list[str]]  # each path is an ordered list of streets
  intersections: list[Intersection]  # ID -> Intersection

  for path in paths:
    for street in path:
      streets[street].weight += 1
  maxWeight = max([street.weight for street in streets.values()])
  minWeight = min([street.weight for street in streets.values()])

  def curve(t: int, weight: int, inputCount: int) -> int:
    return min(
      max(round((D - 1) * (log(weight + 1) - log(minWeight + 1)) / max((log(maxWeight + 1) - log(minWeight + 1)) + 1, 1)) // 256, 1), D
    )  # logarithmic mapping of minWeight^2..maxWeight^2 to 1..D
    return min(
      max(round((D - 1) * ((weight**2) - (minWeight**2)) / max(((maxWeight) - (minWeight)) + 1, 1)) // 64, 1), D
    )  # quadratic mapping of minWeight^2..maxWeight^2 to 1..D
    return min(max(round((D - 1) * (weight - minWeight) / max((maxWeight - minWeight) + 1, 1)) // 64, 1), D)  # linear mapping of minWeight..maxWeight to 1..D
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
    with open(f"{name}.out", "w+") as f:
      f.write(f"{len(intersections)}\n")
      f.writelines(map(str, intersections))
