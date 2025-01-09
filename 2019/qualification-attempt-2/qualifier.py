"""
Google Hash 2019 qualifier.

Copyright 2020 Alex Blandin
"""

from operator import itemgetter
from pathlib import Path

for path in ["a_example", "b_lovely_landscapes", "c_memorable_moments", "d_pet_pictures", "e_shiny_selfies"]:
  image_count = 0
  images = []  # [image: {"id": N, "horizontal": Bool, "tags" = [String]}]
  slideshow = []  # [slide: [image: N]]
  tags = {}  # {"tag": [image: N]}

  with Path(f"{path}.txt").open(encoding="utf8") as o:
    lines = o.readlines()
    image_count = int(lines[0])
    print(f"{image_count} images")  # noqa: T201
    for line, image_index in zip(lines[1:], range(image_count), strict=False):
      image = line.split()
      images.append({"id": image_index, "horizontal": image[0] == "H", "tags": image[2:]})
      for tag in images[-1]["tags"]:
        tags[tag] = tags.get(tag, [])
        tags[tag].append(image_index)

  for tag in tags:
    tags[tag].sort(key=lambda image: len(images[image]["tags"]), reverse=True)
    tags[tag].sort(key=lambda image: images[image]["tags"])

  for tag in list(tags)[:5]:
    print(f"{tag}: " + str(tags[tag] if len(tags[tag]) < 5 else (f"{tags[tag][:5]}"[:-1] + ", ... "))[1:-1])  # noqa: PLR2004, T201

  if path in {"c_memorable_moments", "d_pet_pictures"}:
    temp = dict(zip(tags, range(len(tags)), strict=False))
    tags = temp
    for image in images:
      image["tags"].sort(key=lambda tag: tags[tag])

  if path != "e_shiny_selfies":
    images.sort(key=itemgetter("tags"))

  wait = {}
  for image in images:
    slide = []
    if image["horizontal"]:
      slide.append(image["id"])
      slideshow.append(slide)
    elif "id" in wait and not wait["horizontal"]:
      slide.extend((image["id"], wait["id"]))
      slideshow.append(slide)
      wait = {}
    else:
      wait = image
  if "id" in wait:
    slideshow.append([wait["id"]])

  with Path(f"{path}.out").open(mode="w", encoding="utf8") as o:
    # output
    o.write(f"{len(slideshow)}\n")
    for slide in slideshow:
      o.write(f"{' '.join([str(image) for image in slide])}\n")

print("Done.")  # noqa: T201
