from operator import itemgetter

for path in ["a_example", "b_should_be_easy", "c_no_hurry", "d_metropolis", "e_high_bonus"]:
  rides = []
  rows, columns, fleet_size, ride_count, bonus, sim_length = 0, 0, 0, 0, 0, 0

  # Harley's function
  def score(car, ride):
    ride_length = abs(ride["a"] - ride["x"]) + abs(ride["b"] - ride["y"])
    start_time = abs(ride["a"] - car["last_x"]) - abs(ride["b"] - car["last_y"]) + car["next_free"]
    points = 0
    if ride_length + start_time <= ride["f"]:
      points = ride_length + (bonus if start_time <= ride["s"] else 0)
    return points

  with open(f"{path}.in") as f:
    lines = f.readlines()
    rows, columns, fleet_size, ride_count, bonus, sim_length, *_ = map(int, (lines[0]).split(" "))

    for i, line in enumerate(lines[1:]):
      a, b, x, y, s, f = (int(x) for x in line.split(" "))  # start row, start columns, end row, end column, start time, end time
      ride_length = abs(a - x) + abs(b - y)
      # assert(ride_length <= abs(f-s))
      rides.append({"i": i, "a": a, "b": b, "x": x, "y": y, "s": s, "f": f, "r": ride_length, "q": []})

    print(rows, "*", columns, "area,", sim_length, "steps,", fleet_size, "cars,", ride_count, "rides,", len(rides), "viable,", bonus, "bonus")

  rides.sort(key=itemgetter("f"))
  fleet = [{"i": i, "next_free": 0, "last_x": 0, "last_y": 0, "history": []} for i in range(fleet_size)]

  for ride in rides:
    for car in fleet:
      if car["next_free"] < ride["f"]:
        ride["q"].append(car["i"])
    if len(ride["q"]) != 0:
      ride["q"].sort(key=lambda i: score(fleet[i], ride), reverse=True)
      ride["q"] = ride["q"][0]
      car = fleet[ride["q"]]
      car["history"].append(ride["i"])
      ride_length = ride["r"]  # abs(ride["a"] - ride["x"]) + abs(ride["b"] - ride["y"])
      start_time = abs(ride["a"] - car["last_x"]) - abs(ride["b"] - car["last_y"]) + car["next_free"]
      car["next_free"] = ride_length + max(start_time, ride["s"])

  with open(f"{path}.out", mode="w") as o:
    for car in fleet:
      i, next_free, last_x, last_y, history = car
      o.write(f"{len(car['history'])} ")
      for ride in car["history"]:
        o.write(f"{ride} ")
      o.write("\n")
