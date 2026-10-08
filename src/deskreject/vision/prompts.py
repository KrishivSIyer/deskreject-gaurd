ANONYMITY_PROMPT = """\
You inspect a cropped image from an academic manuscript submitted for double-blind review.
Report anything that could identify the authors or their institution: university or company
logos, crests, seals, lab names, readable author or institution names, email addresses,
watermarks, name badges, or identifiable signage in photographs.
Read text exactly as printed. Do not guess. If nothing identifying is visible, return found=false.
Output only JSON.\
"""

PANEL_PROMPT = """\
This image is one figure from an academic paper. List the sub-panel labels printed in the figure,
for example (a), (b), (c). Return only labels you can actually read, as single lowercase letters,
in reading order (top to bottom, left to right). If the figure has no sub-panel labels, return an
empty list. Output only JSON.\
"""
