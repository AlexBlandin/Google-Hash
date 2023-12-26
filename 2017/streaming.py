from operator import itemgetter

files = ["me_at_the_zoo"]

for path in files:
  videos = []  # [{size: N, endpoints: [{endpoint_id: N, request_count: N}]}]
  endpoints = []  # [{latency_to_server: N, connected_caches: [{cache_id: N, latency_to_cache: N}]}]
  caches = []  # [[video_id: N]]

  video_count, endpoint_count, request_count, cache_count, cache_size = 0, 0, 0, 0, 0
  with open(f"{path}.in", encoding="utf8") as f:
    next_endpoint = 2
    line_no = -1
    for _line in f:
      line = [int(i) for i in _line.split() if i.isdigit()]
      line_no += 1

      # meta data
      if line_no == 0:
        video_count, endpoint_count, request_count, cache_count, cache_size = line
        caches = [{}] * cache_count
        endpoint_ids, cache_ids, video_ids = range(endpoint_count), range(cache_count), range(video_count)
        print(f"{video_count} videos, {endpoint_count} endpoints, {request_count} requests, {cache_count} {cache_size} MB caches")

      # init videos
      elif line_no == 1:
        videos.extend({"size": size, "endpoints": [], "cache_candidates": set()} for size in line if size <= cache_size)

      # init endpoints
      elif line_no == next_endpoint and len(line) == 2:
        latency_to_server, expected_caches = line
        next_endpoint = line_no + expected_caches + 1
        endpoints.append({"latency_to_server": latency_to_server, "connected_caches": []})

      # connect caches to endpoints
      elif len(line) == 2:
        cache_id, latency_to_cache = line
        if latency_to_cache < endpoints[-1]["latency_to_server"]:
          endpoints[-1]["connected_caches"].append({"cache_id": cache_id, "latency_to_cache": latency_to_cache})

      # video request
      else:
        video_id, endpoint_id, request_count = line
        for _cache in endpoints[endpoint_id]["connected_caches"]:
          cache_id, latency_to_cache = _cache["cache_id"], _cache["latency_to_cache"]
          cache = caches[cache_id]
          if video_id not in cache:
            cache[video_id] = {
              "video_id": video_id,
              "request_count": request_count,
              "sum_latency_to_server": endpoints[endpoint_id]["latency_to_server"],
              "sum_latency_to_cache": latency_to_cache,
              "size": videos[video_id]["size"],
              "score": 0,
              "cache_candidates": set(),
            }
          else:
            video = cache[video_id]
            video["request_count"] += request_count
            video["sum_latency_to_server"] += endpoints[endpoint_id]["latency_to_server"]
            video["sum_latency_to_cache"] += latency_to_cache
            video["score"] = video["request_count"] * (video["sum_latency_to_server"] - video["sum_latency_to_cache"]) / video["size"]
            video["cache_candidates"].add(cache_id)

  for _cache in endpoints[endpoint_id]["connected_caches"]:
    cache = caches[_cache["cache_id"]]
    for video in cache:
      video = cache[video_id]
      video["score"] = video["request_count"] * (video["sum_latency_to_server"] - video["sum_latency_to_cache"]) / video["size"]

  temp_caches = [sorted(cache.values(), key=itemgetter("score"), reverse=True) for cache in caches]

  caches = temp_caches

  # output submission file
  with open(f"{path}.out", mode="w", encoding="utf8") as o:
    o.write(f"{len(caches)}\n")
    for videos, chache_id in zip(caches, range(len(caches)), strict=False):
      o.write(f"{cache_id}")
      for video in videos:
        o.write(f" {video['video_id']}")
      o.write("\n")

print("Done.")
