"""
Google Hash 2020 qualifier.

Copyright 2020 Alex Blandin
"""

from operator import attrgetter, itemgetter
from pathlib import Path
from time import time


class Struct(dict):  # noqa: D101
  __getattr__, __setattr__ = dict.__getitem__, dict.__setitem__  # type: ignore  # noqa: PGH003


pb = {
  "a_example": 21,
  "b_read_on": 5831900,
  "c_incunabula": 2361663,
  "d_tough_choices": 5033860,
  "e_so_many_books": 4511113,
  "f_libraries_of_the_world": 4998006,
}


def main() -> None:  # noqa: C901, D103
  for path in sorted(Path().glob("*.txt")):
    libraries, name = [], path.stem
    with path.open(encoding="utf8") as o:
      lines = o.readlines()
      book_scores, _b, _l, _d = list(map(int, lines[1].split())), *map(int, lines[0].split())
      for i, ntm_books in enumerate(zip(lines[2::2], lines[3::2], strict=False)):
        lib, ntm, books = Struct(), *ntm_books
        lib.i, lib.send, lib.N, lib.T, lib.M = i, [], *map(int, ntm.split())
        lib.books = sorted(((b, book_scores[b]) for b in map(int, books.split())), key=itemgetter(1), reverse=True)
        libraries.append(lib)
    print(f"\n{name}:")
    starttime = time()

    libraries.sort(key=attrgetter("T"))  # Timesort

    if name not in {"a_example", "b_read_on", "d_tough_choices"}:
      libraries.sort(key=lambda lib: sum(map(itemgetter(1), lib.books)) / (lib.T * lib.M), reverse=True)

    if name == "d_tough_choices":
      libraries.sort(key=attrgetter("N"), reverse=True)

    # Choose the selection strategy (order of library signup sorted by the highest to lowest under this)
    def selection_strategy(lib):  # noqa: ANN001, ANN202
      return sum(map(itemgetter(1), lib.books)) / (lib.T * lib.M)

    sent, sign_up, queue = set(), libraries[0], {lib.i: lib for lib in libraries}
    t, dt = 0, sign_up.T
    while t < _d and len(queue):
      t += dt
      rem, can_send, lenbooks = _d - t, sign_up.M * (_d - t) + 1, len(sign_up.books)
      sign_up.books = sign_up.books[: min(lenbooks, can_send)]
      sign_up.send = [b[0] for b in sign_up.books]
      sent.update(sign_up.send)

      for lib in queue.values():  # Clear the shelves
        lib.books = [b for b in lib.books if b[0] not in sent]
        can_send, lenbooks = lib.M * (rem - lib.T) + 1, len(lib.books)
        lib.books = lib.books[: min(lenbooks, can_send)]
      queue = {i: lib for i, lib in queue.items() if len(lib.books)}

      if len(queue):
        sign_up = max(queue.values(), key=selection_strategy)
        dt = sign_up.T
        if t + dt > _d:
          break

    print(f"{len(sent)}/{_b} books sent (from {_l - len(queue)}/{_l} libraries)")
    print(f"{sum(book_scores[b] for b in sent)} score (vs {pb[name]}) in {time() - starttime:.2f}s")

    # Write them out to the files
    libraries = [lib for lib in libraries if len(lib.send)]
    with Path(f"{name}.out").open("w", encoding="utf8") as o:
      o.write(f"{len(libraries)}\n")
      for lib in libraries:
        o.write(f"{lib.i} {len(lib.send)}\n")
        o.write(f"{' '.join(map(str, lib.send))}\n")


main()
