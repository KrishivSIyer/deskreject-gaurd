import re

from deskreject.models import Caption, Mention, TextBlock


def find_mentions(
    blocks: list[TextBlock],
    captions: list[Caption],
    references_start: tuple[int, float] | None
) -> list[Mention]:
    mentions: list[Mention] = []
    
    # regex matches:
    # Group 1: Fig, Figure, Figs, Table, Tables
    # Group 2: The first number or ??
    # Group 3: The second number or ?? (optional, if there is a separator)
    pattern = re.compile(
        r"\b(Fig(?:ure)?s?\.?|Tables?)\s*([S\d]+|\?\?)(?:\s*(?:–|-|—|to|and|&|,)\s*([S\d]+|\?\?))?",
        re.IGNORECASE
    )
    
    def is_after_refs(b: TextBlock) -> bool:
        if not references_start:
            return False
        ref_page, ref_y = references_start
        if b.page > ref_page:
            return True
        return bool(b.page == ref_page and b.bbox[1] >= ref_y)
        
    def in_caption(b: TextBlock) -> bool:
        # A simple check: does the block overlap with any caption?
        for cap in captions:
            if cap.page == b.page:
                # bounding box intersection
                x0, y0, x1, y1 = b.bbox
                cx0, cy0, cx1, cy1 = cap.bbox
                if not (x1 <= cx0 or x0 >= cx1 or y1 <= cy0 or y0 >= cy1):
                    return True
        return False

    for b in blocks:
        text = b.text
        after_refs = is_after_refs(b)
        is_cap = in_caption(b)
        
        for match in pattern.finditer(text):
            kind_str = match.group(1).lower()
            kind = "table" if "table" in kind_str else "figure"
            
            num1_str = match.group(2)
            num2_str = match.group(3)
            
            def parse_num(n_str: str | None) -> list[int]:
                if not n_str:
                    return []
                if n_str == "??":
                    return [0]
                if n_str.upper().startswith("S"):
                    # Ignore supplementary labels
                    return []
                try:
                    return [int(n_str)]
                except ValueError:
                    return []

            nums1 = parse_num(num1_str)
            nums2 = parse_num(num2_str)
            
            if nums1 and nums2 and nums1[0] > 0 and nums2[0] > 0:
                # If it's a range and the separator was a dash/to, we expand it
                sep_match = re.search(r"(?:–|-|—|to)", match.group(0))
                if sep_match:
                    start, end = min(nums1[0], nums2[0]), max(nums1[0], nums2[0])
                    # Guard against huge ranges
                    if end - start < 20:
                        nums = list(range(start, end + 1))
                    else:
                        nums = [nums1[0], nums2[0]]
                else:
                    nums = [nums1[0], nums2[0]]
            else:
                nums = nums1 + nums2
                
            for num in nums:
                mentions.append(Mention(
                    kind=kind,
                    number=num,
                    page=b.page,
                    bbox=b.bbox,
                    in_caption=is_cap,
                    after_references=after_refs
                ))
                
    return mentions
