from collections import defaultdict
from pathlib import Path
from statistics import mode
from typing import Any


def splat(d: dict[Any, set]):
  """Take these maps of sets and splat them out as k*|v| and flatten."""
  r = []
  for k, v in d.items():
    r += [k] * len(v)
  return r


def dictsplat(d: dict[Any, set]):
  return {k: len(v) for k, v in d.items()}


def lenmode(d: dict[Any, set]):
  """The lemonade function."""
  return mode(splat(d)) if len(d) else None


def lenmax(d: dict[Any, set]):
  """The host with the most."""
  return max(d, key=lambda k: len(d[k]))


def lensort(d: dict[Any, set], reverse=False) -> dict[Any, set]:
  """Sort it by the cardinality of the internal set, smallest to largest by default."""
  return dict(sorted(d.items(), key=lambda kv: len(kv[1]), reverse=reverse))


SCORE = 0
for p in Path("data/").glob("*.in.txt"):
  p_name = p.name.split(".")[0]
  # a and b are solvable by hand, "4 cheese mushrooms peppers tomatoes" and "6 akuof byyii dlust luncl vxglq xveqd"
  if p_name not in {"a_an_example", "b_basic"}:
    lines = list(map(str.split, p.read_text().splitlines()))
    count = int(lines[0][0])  # not _actually_ needed but might as well
    liked_by, disliked_by = defaultdict(set), defaultdict(set)
    client_likes, client_dislikes = defaultdict(set), defaultdict(set)
    for client, (likes, dislikes) in enumerate(zip(lines[1::2], lines[2::2], strict=False)):
      likes, dislikes = likes[1:], dislikes[1:]  # noqa: PLW2901
      for like in likes:
        liked_by[like].add(client)
        client_likes[client].add(like)
      for d in dislikes:
        disliked_by[d].add(client)
        client_dislikes[client].add(d)

    ingredient_pool = set(liked_by) | set(disliked_by)
    liked_by, disliked_by = lensort(liked_by), lensort(disliked_by)

    def score(pizza: set, client_likes=client_likes, client_dislikes=client_dislikes):
      score = 0
      for client, likes in client_likes.items():
        if len(likes & pizza) == len(likes) and len(client_dislikes[client] & pizza) == 0:
          score += 1
      return score

    if True:  # that's a lot of printing

      def writestats(which, d, p_name=p_name):
        with open(f"{p_name}.{which}.txt", "w+", encoding="utf8", newline="\n") as f:
          ds = dictsplat(d)
          ls = list(ds.values())
          f.write("occurences:\n")
          f.write("\n".join([f"{i}: {ls.count(i)}" for i in range(ls[0], ls[-1] + 1)]))
          f.write("\n\ningredient popularity\n")
          f.write("\n".join(f"{ab[0]}: {ab[1]}" for ab in ds.items()))

      writestats("likes", liked_by)
      writestats("dislikes", disliked_by)

      print("file:", p_name)
      print("total potential clients:", count)
      print("clients that do like:", len(client_likes))
      print("clients that dislike:", len(client_dislikes))
      print("clients that like and do not dislike:", len(set(client_likes) - set(client_dislikes)))
      print("clients that dislike and do not like:", len(set(client_dislikes) - set(client_likes)))
      print("clients that like as well as dislike:", len(set(client_likes) & set(client_dislikes)))
      print("clients that neither like or dislike:", count - len(set(client_likes) | set(client_dislikes)))
      print("available ingredients:", len(ingredient_pool))
      print("liked ingredients:", len(liked_by))
      print("disliked ingredients:", len(disliked_by))
      print("ingredients that are liked and are not disliked:", len(set(liked_by) - set(disliked_by)))
      print("ingredients that are disliked and are not liked:", len(set(disliked_by) - set(liked_by)))
      print("ingredients that are liked yet also disliked:", len(set(liked_by) & set(disliked_by)))
      print("ingredients that are neither liked nor disliked:", len(ingredient_pool) - len(set(liked_by) | set(disliked_by)))
      if len(liked_by):
        print("most frequently liked:", lenmax(liked_by), "with", len(liked_by[lenmode(liked_by)]), "likes")
      if len(disliked_by):
        print("most frequently disliked:", lenmax(disliked_by), "with", len(disliked_by[lenmode(disliked_by)]), "dislikes")
      print("top", min(5, len(liked_by)), "frequently liked:", list(liked_by.keys())[-5:])
      print("top", min(5, len(disliked_by)), "frequently disliked:", list(disliked_by.keys())[-5:])
      if len(liked_by):
        print("stat. mode liked:", lenmode(liked_by), splat(liked_by).count(lenmode(liked_by)))
      if len(disliked_by):
        print("stat. mode disliked:", lenmode(disliked_by), splat(disliked_by).count(lenmode(disliked_by)))

    # the trivial start, liked things that are not disliked, basically freebies
    on_the_pizza = set(liked_by) - set(disliked_by)

    # TODO: figure out what comes next

    # there's a natural interpretation as looking for "maximumum coverage" of a CNF
    # so if c_1 = {A, B}, and c_2 = {C, !D}, and c_3 = {E, F, !C}
    # then clearly C and !C are in conflict, and so they cannot simultaneously hold/resolve
    # since we're looking for "coverage" this might mean "find the deepest you can go?" in one sense
    # where we want to add another client at a time, and are adding their set of likes to the union
    # so long as the union doesn't contain what they don't like, a depth first search is exhaustive and
    # very slow, especially without heuristics or pruning / propagation, while a breadth first search
    # will end up finding the optimal given sufficient memory
    # so this year's practice problem is SAT in a not very good disguise, though the coverage
    # aspect is fairly interesting, as it relates more to testing rather than verification
    # the trivial start is preprocessing away a bunch of variables, reducing the problem by about 20%
    # which is not insignificant given that's inside the exponent
    # of course, the optimal coverage is unlikely
    # something we can do is reduce it further, aka do more preprocessing
    # so we can simplify the terms to conflicts with who and how (more SMT than SAT but oh well)
    # naturally, c_1 and c_3 are non-interacting, and so we can ignore them, and instead weigh it
    # based on how much of an "impact" do you have
    # so c_2 and c_3 add one, but also take one from the final score
    # so they are the variable we care for, and how much they remove from the final score is part
    # of their own score, but in a way that means we still take one of c_2 or c_3, it just doesn't
    # matter which as ultimately they end up at 2 and cannot reach 3 since they block that
    # so everything has a weight in terms of their impact on the theoretical score, and you pick
    # whatever has the lowest weight, since you know their first order weight in terms of what
    # they directly block, since one being favoured can block many, though at the same time
    # the fact that they share means there's also a positive contribution
    # second order is then the network effect, what fun

    # output
    SCORE += score(on_the_pizza)
    if len(on_the_pizza) < 10:
      print(sorted(on_the_pizza), "scored:", score(on_the_pizza), "/", len(client_likes))
    else:
      print("a pizza with", len(on_the_pizza), "ingredients scored:", score(on_the_pizza), "/", len(client_likes))
    print()
    with open(f"{p_name}.out.txt", "w+", encoding="utf8", newline="\n") as f:
      f.write(str(len(on_the_pizza)))
      f.write(" ")
      f.write(" ".join(on_the_pizza))

print("total score for this run:", SCORE)
