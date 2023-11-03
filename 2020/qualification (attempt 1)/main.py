from operator import itemgetter, attrgetter
from pathlib import Path
from time import time

class struct(dict):
  __getattr__, __setattr__ = dict.__getitem__, dict.__setitem__

pb = {
  "a_example": 21,
  "b_read_on": 5831900,
  "c_incunabula": 2361663,
  "d_tough_choices": 5033860,
  "e_so_many_books": 4511113,
  "f_libraries_of_the_world": 4998006
}

def main():
  for path in sorted(list(Path().glob("*.txt"))):
    Libs, name = [], path.stem
    with open(path) as o:
      lines = o.readlines()
      BookScores, B, L, D = list(map(int, lines[1].split())), *map(int, lines[0].split())
      for i, NTMbooks in enumerate(zip(lines[2::2], lines[3::2])):
        lib, NTM, books = struct(), *NTMbooks
        lib.i, lib.send, lib.N, lib.T, lib.M = i, [], *map(int, NTM.split())
        lib.books = sorted(
          list(map(lambda b: (b, BookScores[b]), map(int, books.split()))), key = itemgetter(1), reverse = True
        )
        Libs.append(lib)
    print(f"\n{name}:")
    starttime = time()
    
    Libs.sort(key = attrgetter("T")) # Timesort
    
    if name not in ["a_example", "b_read_on", "d_tough_choices"]:
      Libs.sort(key = lambda lib: sum(map(itemgetter(1), lib.books)) / (lib.T * lib.M), reverse = True)
    
    if name in ["d_tough_choices"]:
      Libs.sort(key = attrgetter("N"), reverse = True)
    
    # Choose the selection strategy (order of library signup sorted by the highest to lowest under this)
    selection_strategy = lambda lib: sum(map(itemgetter(1), lib.books)) / (lib.T * lib.M)
    
    sent, sign_up, queue = set(), Libs[0], dict(map(lambda lib: (lib.i, lib), Libs))
    t, dt = 0, sign_up.T
    while t < D and len(queue):
      t += dt
      rem, can_send, lenbooks = D - t, sign_up.M * (D - t) + 1, len(sign_up.books)
      sign_up.books = sign_up.books[:can_send if can_send < lenbooks else lenbooks]
      sign_up.send = [b[0] for b in sign_up.books]
      sent.update(sign_up.send)
      
      for lib in queue.values(): # Clear the shelves
        lib.books = [b for b in lib.books if b[0] not in sent]
        can_send, lenbooks = lib.M * (rem - lib.T) + 1, len(lib.books)
        lib.books = lib.books[:can_send if can_send < lenbooks else lenbooks]
      queue = {i: lib for i, lib in queue.items() if len(lib.books)}
      
      if len(queue):
        sign_up = max(queue.values(), key = selection_strategy)
        dt = sign_up.T
        if t + dt > D:
          break
    
    print(f"{len(sent)}/{B} books sent (from {L-len(queue)}/{L} libraries)")
    print(f"{sum(map(lambda b: BookScores[b], sent))} score (vs {pb[name]}) in {time()-starttime:.2f}s")
    
    # Write them out to the files
    Libs = [lib for lib in Libs if len(lib.send)]
    with open(f"{name}.out", "w") as o:
      o.write(f"{len(Libs)}\n")
      for lib in Libs:
        o.write(f"{lib.i} {len(lib.send)}\n")
        o.write(f"{' '.join(map(str, lib.send))}\n")

main()
