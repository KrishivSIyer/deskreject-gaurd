import re
from typing import Any

from deskreject.models import Caption, Figure, ImageRef, Span, TextBlock


def find_captions(blocks: list[TextBlock]) -> list[Caption]:
    captions = []
    pattern = re.compile(r"^(Fig\.|Figure|Table)\s+(\d+)\s*[.:|]", re.IGNORECASE)
    for b in blocks:
        text = b.text.strip()
        match = pattern.match(text)
        if match:
            kind_str = match.group(1).lower()
            kind = "table" if kind_str == "table" else "figure"
            num = int(match.group(2))
            captions.append(
                Caption(
                    kind=kind,
                    number=num,
                    page=b.page,
                    bbox=b.bbox,
                    text=text
                )
            )
    return captions


def find_figures(
    doc: Any,
    captions: list[Caption],
    images: list[ImageRef],
    spans: list[Span],
    drawings: list[tuple[int, dict]]
) -> list[Figure]:
    figures = []

    for cap in captions:
        page_num = cap.page
        page = doc[page_num - 1]
        raw_blocks = page.get_text("blocks")

        cap_x0, cap_y0, cap_x1, cap_y1 = cap.bbox
        page_w = page.rect.width
        col_mid = page_w / 2
        is_left_col = cap_x1 < col_mid + 20
        is_right_col = cap_x0 > col_mid - 20

        min_y = 0.0
        max_y = cap_y0

        blocks_above = []
        for b in raw_blocks:
            if b[6] != 0:
                continue
            bx0, by0, bx1, by1, btext, _bno, _btype = b
            # body text heuristic: length > 30 or width > 100
            if by1 <= cap_y0 and (len(btext.strip()) > 30 or (bx1 - bx0) > 100) and ((is_left_col and bx1 < col_mid + 20) or (is_right_col and bx0 > col_mid - 20) or (not is_left_col and not is_right_col)):
                blocks_above.append(b)

        if blocks_above:
            blocks_above.sort(key=lambda x: x[3], reverse=True)
            min_y = blocks_above[0][3]

        if max_y - min_y < 10:
            min_y = cap_y1
            max_y = page.rect.height
            blocks_below = []
            for b in raw_blocks:
                if b[6] != 0:
                    continue
                bx0, by0, bx1, by1, btext, _bno, _btype = b
                if by0 >= cap_y1 and (len(btext.strip()) > 30 or (bx1 - bx0) > 100) and ((is_left_col and bx1 < col_mid + 20) or (is_right_col and bx0 > col_mid - 20) or (not is_left_col and not is_right_col)):
                    blocks_below.append(b)
            if blocks_below:
                blocks_below.sort(key=lambda x: x[1])
                max_y = blocks_below[0][1]

        col_x0 = 0.0 if is_left_col else col_mid
        col_x1 = col_mid if is_left_col and not is_right_col else page_w
        if not is_left_col and not is_right_col:
            col_x0, col_x1 = 0.0, page_w

        region = (col_x0, min_y, col_x1, max_y)

        fig_images = []
        for img in images:
            if img.page == page_num:
                ix0, iy0, ix1, iy1 = img.bbox
                if iy1 > region[1] and iy0 < region[3]:
                    region = (min(region[0], ix0), region[1], max(region[2], ix1), region[3])
                    fig_images.append(img)

        fig_spans = []
        for sp in spans:
            if sp.page == page_num:
                sx0, sy0, sx1, sy1 = sp.bbox
                if sy1 > region[1] and sy0 < region[3] and sx1 > col_x0 and sx0 < col_x1 and len(sp.text) < 15:
                    fig_spans.append(sp)

        union_x0, union_y0, union_x1, union_y1 = 9999, 9999, -9999, -9999
        items = fig_images + fig_spans

        for d_page, d in drawings:
            if d_page == page_num:
                dx0, dy0, dx1, dy1 = d["rect"]
                if dy1 > region[1] and dy0 < region[3] and dx1 > col_x0 and dx0 < col_x1:
                    union_x0 = min(union_x0, dx0)
                    union_y0 = min(union_y0, dy0)
                    union_x1 = max(union_x1, dx1)
                    union_y1 = max(union_y1, dy1)

        for it in items:
            ix0, iy0, ix1, iy1 = it.bbox
            if isinstance(it, Span):
                ix0 -= 4
                iy0 -= 4
                ix1 += 4
                iy1 += 4
            union_x0 = min(union_x0, ix0)
            union_y0 = min(union_y0, iy0)
            union_x1 = max(union_x1, ix1)
            union_y1 = max(union_y1, iy1)

        if union_x0 > union_x1:
            union_bbox = region
        else:
            union_bbox = (union_x0, union_y0, union_x1, union_y1)

        fig_id = f"{cap.kind.capitalize()} {cap.number}"
        figures.append(
            Figure(
                id=fig_id,
                number=cap.number,
                page=page_num,
                region=union_bbox,
                caption=cap,
                images=fig_images,
                spans=fig_spans
            )
        )

    return figures
