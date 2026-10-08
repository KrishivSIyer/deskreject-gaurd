import math
from pathlib import Path

import fitz
import numpy as np
from PIL import Image

from deskreject.checks.base import Context, register_check
from deskreject.config import settings
from deskreject.models import Finding, ParsedDoc, Preset, Severity

MACHADO_MATRICES = {
    "protanopia": np.array([
        [0.152286, 1.052583, -0.204868],
        [0.114503, 0.786281,  0.099216],
        [-0.003882, -0.048116, 1.051998]
    ]),
    "deuteranopia": np.array([
        [0.367322, 0.860646, -0.227968],
        [0.280085, 0.672501, 0.047413],
        [-0.011820, 0.042940, 0.968881]
    ]),
    "tritanopia": np.array([
        [1.255528, -0.076749, -0.178779],
        [-0.078411, 0.930809, 0.147602],
        [0.004733, 0.691367, 0.303900]
    ])
}

def rgb_to_lab(rgb: tuple[int, int, int]) -> tuple[float, float, float]:
    """Convert sRGB to CIE Lab."""
    # Normalize RGB
    r = rgb[0] / 255.0
    g = rgb[1] / 255.0
    b = rgb[2] / 255.0

    # sRGB to Linear RGB
    r = ((r + 0.055) / 1.055) ** 2.4 if r > 0.04045 else r / 12.92
    g = ((g + 0.055) / 1.055) ** 2.4 if g > 0.04045 else g / 12.92
    b = ((b + 0.055) / 1.055) ** 2.4 if b > 0.04045 else b / 12.92

    # Linear RGB to XYZ
    x = (r * 0.4124564 + g * 0.3575761 + b * 0.1804375) / 0.95047
    y = (r * 0.2126729 + g * 0.7151522 + b * 0.0721750) / 1.00000
    z = (r * 0.0193339 + g * 0.1191920 + b * 0.9503041) / 1.08883

    # XYZ to Lab
    def f(t: float) -> float:
        return t ** (1/3) if t > 0.008856 else 7.787 * t + 16 / 116

    fx = f(x)
    fy = f(y)
    fz = f(z)

    l = 116 * fy - 16
    a = 500 * (fx - fy)
    b_val = 200 * (fy - fz)
    return l, a, b_val

def get_chroma(lab: tuple[float, float, float]) -> float:
    return math.sqrt(lab[1]**2 + lab[2]**2)

def delta_e(lab1: tuple[float, float, float], lab2: tuple[float, float, float]) -> float:
    return math.sqrt((lab1[0] - lab2[0])**2 + (lab1[1] - lab2[1])**2 + (lab1[2] - lab2[2])**2)

def simulate_colorblind(img: Image.Image, matrix: np.ndarray) -> Image.Image:
    # Convert sRGB to linear RGB, apply matrix, back to sRGB
    # For speed in this check, we apply directly to gamma RGB
    arr = np.array(img, dtype=float)
    shape = arr.shape
    arr = arr.reshape(-1, 3)
    
    # Linearize approx
    arr = (arr / 255.0) ** 2.2
    
    # Apply matrix
    arr = np.dot(arr, matrix.T)
    
    # Clip and de-linearize
    arr = np.clip(arr, 0.0, 1.0)
    arr = arr ** (1 / 2.2)
    arr = (arr * 255.0).astype(np.uint8)
    
    return Image.fromarray(arr.reshape(shape))

@register_check
def check_accessibility(doc: ParsedDoc, preset: Preset, ctx: Context) -> list[Finding]:
    findings = []
    
    preview_dir = settings.cache_dir / "previews"
    preview_dir.mkdir(parents=True, exist_ok=True)
    
    if hasattr(ctx, "figure_previews"):
        if ctx.figure_previews is None:
            ctx.figure_previews = {}
    else:
        ctx.__dict__["figure_previews"] = {}
        
    pdf = None
    if doc.figures:
        pdf = fitz.open(doc.path)

    for fig in doc.figures:
        page = pdf.load_page(fig.page - 1)
        pix = page.get_pixmap(matrix=fitz.Matrix(150/72, 150/72), clip=fitz.Rect(fig.region))
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)

        # Save simulated images
        ctx.figure_previews[fig.id] = {}
        for mode, matrix in MACHADO_MATRICES.items():
            sim_img = simulate_colorblind(img, matrix)
            # Remove spaces and normalize for filename
            clean_id = fig.id.replace(" ", "_").lower()
            file_name = f"{Path(doc.path).stem}_{clean_id}_{mode}.png"
            out_path = preview_dir / file_name
            sim_img.save(out_path)
            ctx.figure_previews[fig.id][mode] = str(out_path)

        # Check color distinguishability
        # 1. Downscale to 200px wide
        if img.width > 200:
            ratio = 200 / img.width
            img_small = img.resize((200, int(img.height * ratio)), Image.Resampling.LANCZOS)
        else:
            img_small = img.copy()

        # 2. Quantize to 8 colors
        q_img = img_small.quantize(colors=8, method=Image.Quantize.MAXCOVERAGE)
        q_img = q_img.convert("RGB")
        
        # 3. Get colors with >= 1.5% pixels
        total_pixels = q_img.width * q_img.height
        min_pixels = total_pixels * 0.015
        
        colors_count = q_img.getcolors(8)
        if not colors_count:
            continue
            
        valid_colors = []
        for count, rgb in colors_count:
            if count >= min_pixels:
                lab = rgb_to_lab(rgb)
                if get_chroma(lab) >= 12:
                    valid_colors.append((rgb, lab))

        # 4. Check color pairs
        problematic_pairs = []
        for i in range(len(valid_colors)):
            for j in range(i + 1, len(valid_colors)):
                rgb1, lab1 = valid_colors[i]
                rgb2, lab2 = valid_colors[j]
                
                d_orig = delta_e(lab1, lab2)
                if d_orig >= 30:
                    # Check in simulated modes
                    # We can use the matrix on the single color
                    for mode, matrix in MACHADO_MATRICES.items():
                        c1_arr = np.array(rgb1) / 255.0
                        c1_lin = c1_arr ** 2.2
                        c1_sim = np.clip(np.dot(c1_lin, matrix.T), 0, 1) ** (1/2.2) * 255
                        c1_sim_lab = rgb_to_lab(tuple(c1_sim.astype(int)))
                        
                        c2_arr = np.array(rgb2) / 255.0
                        c2_lin = c2_arr ** 2.2
                        c2_sim = np.clip(np.dot(c2_lin, matrix.T), 0, 1) ** (1/2.2) * 255
                        c2_sim_lab = rgb_to_lab(tuple(c2_sim.astype(int)))
                        
                        d_sim = delta_e(c1_sim_lab, c2_sim_lab)
                        
                        if d_sim < 12:
                            problematic_pairs.append((rgb1, rgb2, mode))
                            break

        if problematic_pairs:
            findings.append(Finding(
                code="ACC_CB_INDISTINGUISHABLE",
                check="accessibility",
                severity=Severity.warning,
                title="Colors indistinguishable for colorblind readers",
                detail="Some colors in this figure rely purely on hue to be distinguished, which fails under colorblindness.",
                page=fig.page,
                bbox=fig.region,
                evidence=f"Colors lost contrast in {problematic_pairs[0][2]} simulation.",
                source="rule",
                figure_id=fig.id,
            ))

    if pdf:
        pdf.close()

    return findings
