from operator import itemgetter

video_count, endpoint_count, request_count, cache_count, cache_size = 0, 0, 0, 0, 0
endpoints, endpoint_ids, caches, cache_ids, video_sizes, video_ids = [], [], [], [], [], []
min_video_size, max_video_size = 0, 0
video_priorities = {}

print_sizes = False
debug = False
console = True

# Get our input data
path = input("Input File: ")
source, ext = path.split(sep = ".") if len(path.split(sep = ".")) == 2 else path.split(sep = ".")[0], "in"
with open(path) as p:
  next_endpoint = 2 # preset
  line_count = sum([1 for i in p])
  indices = range(line_count)
  p.seek(0)
  for line, index in zip(p, indices):
    values = [int(i) for i in line.split() if i.isdigit()]
    
    # Meta data
    if index == 0:
      video_count, endpoint_count, request_count, cache_count, cache_size = values
      endpoint_ids, cache_ids, video_ids = range(endpoint_count), range(cache_count), range(video_count)
      # video_priorities = [[] for i in video_ids]
      print(
        f"{video_count} videos, {endpoint_count} endpoints, {request_count} requests, {cache_count} caches (each is {cache_size} MB)"
      )
    
    # Video sizes
    elif index == 1:
      video_sizes = values
      min_video_size = min(video_sizes)
      # max_video_size = max(video_sizes) # currently not using, so not bothering to calculate
    
    # Endpoint
    elif index == next_endpoint and len(values) == 2:
      latency_to_server, expected_caches = values
      next_endpoint = index + expected_caches + 1
      endpoint = (latency_to_server, [], []) # endpoint = (latency to server, cache links, video requests)
      endpoints.append(endpoint)
    
    # Cache, connect cache to last endpoint
    elif len(values) == 2:
      cache_id, latency_to_cache = values
      endpoint = endpoints[-1]
      
      # If this cache is lower latency than just connecting to the server, then it is useful, otherwise it's a waste of processing
      if latency_to_cache < endpoint[0]:
        endpoint[1].append((cache_id, latency_to_cache))
    
    # Video request
    else:
      video_id, endpoint_requesting, specific_requests_count = values
      endpoint = endpoints[endpoint_requesting]
      endpoint[2].append((video_id, specific_requests_count))

# Calculate theoretically optimal time savings given infinitely large caches -- likely impossible to match given cache size restraints
optimum_savings = 0
for endpoint in endpoints:
  lowest_latency = endpoint[0]
  for cache in endpoint[1]:
    lowest_latency = min(lowest_latency, cache[1])
  optimum_savings += sum([request[1] for request in endpoint[2]]) * (endpoint[0] - lowest_latency)
optimum_savings *= 1000
optimum_savings /= endpoint_count

# Sort endpoints' requests by volume, most requested video first
for endpoint in endpoints:
  endpoint[2].sort(key = itemgetter(1), reverse = True)

# Generate unrequested, unrequested, empty, empty, caches
for cache in cache_ids:
  caches.append(([], {}, 0, [])
                ) # cache = (video requests by endpoints, aggregate requests for videos, MB used, videos stored in cache)

# Elevate requests to cache-level
for endpoint, endpoint_id in zip(endpoints, endpoint_ids):
  for linked_cache in endpoint[1]:
    cache_id, latency_to_cache = linked_cache
    for request in endpoint[2]:
      video_id, video_requests = request
      caches[cache_id][0].append((video_requests, video_id, latency_to_cache, endpoint_id))

# Auction loop design
# ---
# This code is meant to compare a video that a number has to a cache, to see if the cache has it. If it does, then it should
# # want to finish this?

...

# The purpose of priority is to find all endpoints that have the same video number as input,
# and then add together all those requests together to rate them by priority.
# It'll make use of the number of requests, along with the average lantecy, to calculate this.
def priority(video_id):
  request_no = 0
  endpoint_no = []
  latency = 0
  
  for cache in caches:
    for request, cache_id in zip(cache, cache_ids):
      if request[cache_id][1] == video_id:
        request_no += request[0]
        endpoint_no.append(request[3])
        latency += request[2]
      
      priority = (request_no / (latency / len(endpoint_no)))
      cache.append((request_no, endpoint_no, latency / len(endpoint_no), priority))

# # # currently not used?

...

# I am doing a local priority list for each individual cache. Each cache will make an
# array of its videos, sorted in order of the video requests for each video divided by the
# latency between all endpoints that are requesting such.

# Greedy initial priority score for each cache, for each video score
for cache, cache_id in zip(caches, cache_ids):
  requested_videos = {}
  for request in cache[0]:
    request_count, video_id, latency, endpoint_id = request
    # Add video_id to requested_videos
    if video_id not in requested_videos:
      requested_videos[video_id] = (
        video_id, 0, 0, 0, 0
      ) # request = (video_id, sum_video_requests, sum_latency_to_caches, sum_latency_to_server, requesting_endpoints_count)
    old = requested_videos[video_id] # current values for video
    latency_to_server = endpoints[endpoint_id][0] # grab that endpoint's latency to the main server
    requested_videos[video_id] = (
      video_id, old[0] + request_count, old[1] + latency_to_cache, old[2] + latency_to_server, old[3] + 1
    ) # update entry for video
  
  cache = (cache[0], requested_videos, cache[2], cache[3]) # update requested_videos dictionary in cache
  for request in requested_videos: # iterates over keys
    video_id, sum_video_requests, sum_latency_to_caches, sum_latency_to_server, requesting_endpoints_count = requested_videos[
      request]
    priority_score = request_count * (
      sum_latency_to_server - sum_latency_to_caches
    ) # quick and dirty (greedy) prioritisation -- negative is slower than latency to server
    if priority_score > 0: # only bother if actually faster than going to the server
      if video_id not in video_priorities:
        video_priorities[video_id] = []
      video_priorities[video_id].append((priority_score, cache_id)
                                        ) # add cache's priority to the video_priorities list, for each video_id

# Packing -- "Greedy" in that it always fits in the highest priority videos if it can, starting from the highest and working towards the lowest
space_for_videos, videos_to_cache = True, True
while space_for_videos and videos_to_cache:
  for video in video_priorities.values():
    video.sort(key = itemgetter(0), reverse = True)
  
  sorted_priorities = [
    (video_id, video_priorities[video_id])
    for video_id in sorted(video_priorities, key = lambda video_id: video_priorities[video_id][0][0], reverse = True)
  ]
  video_priorities = {}
  for video_id, video in sorted_priorities:
    video_priorities[video_id] = video # because sorting dictionaries doesn't work...
  
  remove_from_priorities = []
  
  if debug: print(f"Video priorities: {video_priorities}")
  for video_id, video in video_priorities.items():
    top = video.pop(0)
    if debug:
      print(
        f"Video {video_id} in cache {top[1]} scores {top[0]}, is {video_sizes[video_id]} MB, cache contains {caches[top[1]][2]} MB"
      )
    if top[0] > 0 and (video_sizes[video_id] + caches[top[1]][2]) <= cache_size:
      caches[top[1]][3].append(video_id) # put video_id into the cache's list of stored videos
      old_cache = caches[top[1]]
      caches[top[1]] = (old_cache[0], old_cache[1], old_cache[2] + video_sizes[video_id], old_cache[3])
      if debug:
        print(
          f"Video {video_id} added to cache {top[1]}, scores {top[0]}, is {video_sizes[video_id]} MB, cache contains {caches[top[1]][2]} MB"
        )
    else:
      # for now, completely greedy
      # if we recalculate the priorities, we will do so here
      # if we prune out videos that don't fit, we will do so here
      pass
    if video == []:
      remove_from_priorities.append(video_id)
      continue # flags videos with no more requests from deletion from video_priorities dict
  # Do we have any space?
  for cache in caches:
    if cache[2] == cache_size or cache[2] >= cache_size - min_video_size + 1: # full or can't fit any more videos
      continue
    else:
      space_for_videos = True
      break
  else: # if we finish without breaking (or, in this case, return)
    space_for_videos = False
  if video_priorities == {}:
    videos_to_cache = False
  else:
    for video_id in remove_from_priorities:
      del video_priorities[video_id]

utilised_caches = [(sorted(cache[3]), cache_id) for cache, cache_id in zip(caches, cache_ids)
                   if cache[2] > 0 and cache[2] <= cache_size]
utilised_cache_count = len(utilised_caches)
print(f"Utilised {utilised_cache_count} caches")
print(f"Caches: {utilised_caches}")

# # Scorer
scores = []
for endpoint in endpoints:
  connected_caches = [(cache[0], cache[1], caches[cache[0]][3]) for cache in endpoint[1]]
  connected_videos = {}
  
  for video in endpoint[2]:
    for cache in connected_caches:
      cache_id, latency_to_cache, cached_videos = cache
      
      if video[0] in cached_videos:
        if video[0] not in connected_videos:
          connected_videos[video[0]] = []
        
        connected_videos[video[0]].append((cache_id, latency_to_cache, video[1]))
  
  for video in connected_videos:
    lowest = endpoint[0]
    fastest_cache = -1
    cache_id, latency_to_cache, request_count = 0, 0, 0
    for cache in connected_videos[video]:
      cache_id, latency_to_cache, request_count = cache
      
      if latency_to_cache < lowest_latency:
        lowest = latency_to_cache
        fastest_cache = cache_id
    
    scores.append(request_count * (endpoint[0] - lowest))

score = sum(scores)
score *= 1000
score /= len(scores)

print(f"Score: {score}")
print(f"Optimal: {optimum_savings}")
print(f"Efficiency: {score/optimum_savings:%}")

# Output submission file
with open(source + ".out", mode = "w") as o:
  o.write(f"{utilised_cache_count}\n")
  
  for cache, cache_id in utilised_caches:
    o.write(f"{cache_id}")
    
    for video in cache:
      o.write(f" {video}")
    
    o.write("\n")
