class struct(dict):
  __getattr__, __setattr__ = dict.__getitem__, dict.__setitem__

def read(name):
  with open(f"{name}.txt", "r") as f:
    lines = list(map(str.split, f.readlines()))
  D, I, S, V, F = map(int, lines[0])
  streets = {
    SN: struct(startsAt = int(B), endsAt = int(E), length = int(L), weight = 0)
    for B, E, SN, L in lines[1:S + 1]
  }
  paths, intersections = [streets for _, *streets in lines[S + 1:]
                          ], [struct(ID = i, inputs = [], outputs = [], order = []) for i in range(I)]
  for streetname, street in streets.items():
    intersections[street.endsAt].inputs.append(streetname)
    intersections[street.startsAt].outputs.append(streetname)
  return D, I, S, V, F, streets, paths, intersections

from math import log

def solve(name, D, I, S, V, F, streets, paths, intersections):
  for path in paths:
    for street in path:
      streets[street].weight += 1
  minWeight, maxWeight = min([street.weight
                              for street in streets.values()]), max([street.weight for street in streets.values()])
  
  def curve(t, weight):
    return min(
      max(
        round((D - 1) *
              (log(weight + 1) - log(minWeight + 1)) / max((log(maxWeight + 1) - log(minWeight + 1)) + 1, 1)) // 256, 1
      ), D
    ) # logarithmic mapping of minWeight^2..maxWeight^2 to 1..D
    # return min(max(round((D-1)*((weight**2)-(minWeight**2))/max(((maxWeight)-(minWeight)) + 1, 1))//64,1), D) # quadratic mapping of minWeight^2..maxWeight^2 to 1..D
    # return min(max(round((D-1)*(weight-minWeight)/max((maxWeight-minWeight) + 1, 1))//64,1), D) # linear mapping of minWeight..maxWeight to 1..D
    # return t # identity mapping (works ~~infuriatingly~~ surprisingly well)
  
  for intersection in intersections:
    intersection.order = [
      (street, curve(t, streets[street].weight))
      for t, street in enumerate(sorted(intersection.inputs, key = lambda street: streets[street].weight), start = 1)
    ]
  return intersections

if __name__ == "__main__":
  for name in "abcdef":
    intersections = solve(name, *read(name))
    with open(f"{name}.out", "w+") as f:
      f.write(f"{len(intersections)}\n")
      f.writelines([
        f"{self.ID}\n{len(self.order)}\n{'\n'.join(f'{sn} {T}' for sn,T in self.order)}\n" for self in intersections
      ])
