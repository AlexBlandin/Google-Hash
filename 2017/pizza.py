from functools import partial
from math import sqrt
from tqdm import tqdm
"""
 ██████╗ ██╗███████╗███████╗ █████╗     ███████╗██╗     ██╗ ██████╗███████╗██████╗
 ██╔══██╗██║╚══███╔╝╚══███╔╝██╔══██╗    ██╔════╝██║     ██║██╔════╝██╔════╝██╔══██╗
 ██████╔╝██║  ███╔╝   ███╔╝ ███████║    ███████╗██║     ██║██║     █████╗  ██████╔╝
 ██╔═══╝ ██║ ███╔╝   ███╔╝  ██╔══██║    ╚════██║██║     ██║██║     ██╔══╝  ██╔══██╗
 ██║     ██║███████╗███████╗██║  ██║    ███████║███████╗██║╚██████╗███████╗██║  ██║
 ╚═╝     ╚═╝╚══════╝╚══════╝╚═╝  ╚═╝    ╚══════╝╚══════╝╚═╝ ╚═════╝╚══════╝╚═╝  ╚═╝
"""

# Scores 100% on example.in and small.in (fit)
# 96.6% on medium.in (fill, 30s) or 96.9% (fit, 54m)
# 88.2% on big.in (fill)

# slice = (x1, x2, y1, y2, area)

total_score = 0
for path in ["example.in", "small.in", "medium.in", "big.in"][2:3]:
  print()
  print(f"{path}")
  source, ext = path.split(sep = ".")
  with open(path) as p:
    lines = p.readlines()
    rows, columns, minimum_ingredients, maximum_area = map(int, lines[0].split())
    pizza = [[1 if c == "T" else 0 for c in line.strip()] for line in lines[1:]]
  assert (len(pizza) == rows)
  assert (len(pizza[0]) == columns)
  total_area, minimum_area = rows * columns, minimum_ingredients * 2
  inverse = [set() for _ in range(total_area)] # len(inverse[at(x,y)]) is how many slices cover, if 0 then uncoverable
  print(f"Rows: {rows} rows, {columns} columns, {minimum_ingredients} ingredients minimum, {maximum_area} area maximum")
  
  def at(x, y, rows = rows):
    "Linear mapping into inverse"
    return y * rows + x
  
  def conjoint(quad):
    "all others that are conjoint to quad"
    x1, x2, y1, y2, _ = quad
    cj = {quad}
    for y in range(y1, y2 + 1):
      for x in range(x1, x2 + 1):
        cj |= inverse[at(x, y)]
    return cj
  
  def quadsum(quad):
    "Returns the sum of all values within a quad"
    x1, x2, y1, y2, _ = quad
    return sum(sum(row[x1:x2 + 1]) for row in pizza[y1:y2 + 1])
  
  def quadarea(quad):
    "Returns only the area of a quad"
    # _, _, _, _, area = quad
    return quad[-1]
  
  def sufficient(quad, mi = minimum_ingredients, ma = maximum_area):
    "Finds if a quadrangle has sufficient ingredients"
    tomatoes, area = quadsum(quad), quadarea(quad)
    mushrooms = area - tomatoes
    return tomatoes >= mi and mushrooms >= mi and area <= ma
  
  def disjoint(quad1, quad2):
    x1, x2, y1, y2, _ = quad1
    a1, a2, b1, b2, _ = quad2
    return x1 > a2 or x2 < a1 or y1 > b2 or y2 < b1 # idk, micro-opt but maybe this is faster
    # return not (x1 <= a2 and x2 >= a1 and y1 <= b2 and y2 >= b1)
  
  def disjoint_from(quad, quads): # TODO: speedup majorly bc ~5000 in medium is real slow (and big? oh my)
    return all(disjoint(quad, other) for other in quads)
  
  # Calculates appropriate sizes of quadrangle slices
  slice_sizes = set()
  for n in range(minimum_area, maximum_area + 1):
    for i in range(1, int(sqrt(n)) + 1):
      div, mod = divmod(n, i)
      if mod == 0:
        slice_sizes.add((div, i))
        slice_sizes.add((i, div))
  
  # Calculates all legal slices
  candidates = []
  for y1 in range(rows):
    for x1 in range(columns):
      for size in slice_sizes:
        size_x, size_y = size # size of slice
        x2, y2 = x1 + size_x - 1, y1 + size_y - 1 # offset from x1,y1
        if y2 < rows and x2 < columns:
          quad = (x1, x2, y1, y2, (x2 - x1 + 1) * (y2 - y1 + 1))
          if sufficient(quad):
            candidates.append(quad)
            for y in range(y1, y2 + 1):
              for x in range(x1, x2 + 1):
                inverse[at(x, y)].add(quad) # inverse peaks at 2.7GB on big.in
  assert (len(candidates))
  coverable_area = sum(map(bool, map(len, inverse))) # TODO: HECKIN BUG HERE SOMETHING'S OFF WE'RE UNDERESTIMATING
  viable_area = coverable_area - quadarea(candidates[-1]) # so based on smallest slice
  
  if coverable_area != total_area:
    print(f"Only {coverable_area} of {total_area} area is coverable")
    # empty = sorted(map(itemgetter(0), filter(lambda ix: ix[1]==0, map(lambda ix: (divmod(ix[0],rows),len(ix[1])),enumerate(inverse)))))
    # for y,x in empty: assert(len(inverse[at(x,y)])==0)
    # print(" ".join(map(str, empty)))
    # only big.in should have uncoverable spots, the others shouldn't (but do :BUG:)
    """
    Only 999936 of 1000000 area is coverable
    (445, 0) (952, 0) (189, 13) (838, 18) (325, 26) (697, 53) (285, 54) (87, 60) (998, 61) (999, 62) (559, 146) (823, 153) (893, 167) (549, 176) (0, 202) (0, 203) (781, 214) (9, 239) (239, 253) (1, 262) (716, 296) (999, 333) (70, 336) (179, 349) (179, 350) (271, 359) (0, 362) (797, 366) (433, 390) (142, 395) (65, 402) (382, 411) (384, 411) (616, 412) (865, 413) (488, 429) (207, 470) (347, 472) (347, 473) (571, 473) (584, 481) (798, 502) (798, 504) (0, 530) (998, 541) (0, 575) (605, 592) (635, 614) (604, 629) (493, 651) (746, 669) (922, 721) (558, 725) (803, 765) (363, 779) (461, 809) (34, 838) (273, 838) (138, 863) (587, 908) (867, 908) (500, 917) (3, 924) (234, 957)
    """
  else:
    print(f"We can cover all {coverable_area} area")
  print(f"Viable area is {viable_area}")
  # Ordered, largest slices first
  candidates.sort(key = quadarea, reverse = True)
  candidate_count = len(candidates)
  print(f"{candidate_count} candidates")
  
  # Search for best solution
  use = "fill" or "fill" or "fit" or "SAT"
  use = "fit" if path in ["example.in", "small.in"] and use == "fill" else use # force "fit" when trivial
  fast_fill = use == "fill" # fast_fill is a single iteration of first_fit (so max-first)
  first_fit = use == "fit"
  SAT = use == "SAT"
  by_size = False # runs by smallest as well as by largest
  
  best_slices, best_area = [], 0
  print(f"Solving by {use}")
  if SAT: # fill by largest first
    for starting_slice in tqdm(candidates[:100]):
      chosen_slices, area = [starting_slice], quadarea(starting_slice)
      scand = {c for c in candidates if c not in conjoint(starting_slice)}
      while len(scand) and area <= viable_area:
        candidate = max(scand, key = quadarea)
        chosen_slices.append(candidate)
        area += quadarea(candidate)
        scand -= conjoint(candidate)
      if area > best_area: best_area, best_slices = area, chosen_slices
  
  # "Fast-fit" packing -- single iteration of first-fit
  if fast_fill:
    starting_slice = candidates[0]
    chosen_slices, area, djs = [starting_slice], quadarea(starting_slice), partial(disjoint, starting_slice)
    for candidate in tqdm(tuple(filter(djs, candidates))):
      cq = quadarea(candidate)
      if area + cq <= coverable_area and disjoint_from(candidate, chosen_slices):
        chosen_slices.append(candidate)
        area += cq
      if area > viable_area: break
    if area > best_area: best_area, best_slices = area, chosen_slices
  
  # First-fit packing
  if first_fit:
    for starting_slice in tqdm(candidates[:100]):
      chosen_slices, area, djs = [starting_slice], quadarea(starting_slice), partial(disjoint, starting_slice)
      for candidate in filter(djs, candidates):
        cq = quadarea(candidate)
        if area + cq <= coverable_area and disjoint_from(candidate, chosen_slices):
          chosen_slices.append(candidate)
          area += cq
        if area > viable_area: break
      if area > best_area: best_area, best_slices = area, chosen_slices
  
  # Also try by smallest
  if by_size:
    candidates.reverse()
  if fast_fill and by_size:
    starting_slice = candidates[0]
    chosen_slices, area, djs = [starting_slice], quadarea(starting_slice), partial(disjoint, starting_slice)
    for candidate in tqdm(tuple(filter(djs, candidates))):
      cq = quadarea(candidate)
      if area + cq <= coverable_area and disjoint_from(candidate, chosen_slices):
        chosen_slices.append(candidate)
        area += cq
      if area > viable_area: break
    if area > best_area: best_area, best_slices = area, chosen_slices
  
  if first_fit and by_size:
    for starting_slice in tqdm(candidates[:100]):
      chosen_slices, area, djs = [starting_slice], quadarea(starting_slice), partial(disjoint, starting_slice)
      for candidate in filter(djs, candidates):
        cq = quadarea(candidate)
        if area + cq <= coverable_area and disjoint_from(candidate, chosen_slices):
          chosen_slices.append(candidate)
          area += cq
        if area > viable_area: break
      if area > best_area: best_area, best_slices = area, chosen_slices
  
  print(f"Best Area: {best_area}/{total_area} ({best_area/total_area:.1%})")
  total_score += best_area
  
  # Save solution to .out
  # with open(source + ".out", "w") as o:
  #   o.write(str(len(best_slices)) + "\n")
  #   best_slices.sort(key=itemgetter(0))
  #   for q in best_slices:
  #     x1, x2, y1, y2 = q
  #     (x1, y1), (x2, y2) = min((x1,y1),(x2,y2)), max((x1,y1),(x2,y2)) # Liam... they're meant to be in any order...
  #     o.write(f"{y1} {x1} {y2} {x2}\n")
print()
print(f"Total score: {total_score}")
