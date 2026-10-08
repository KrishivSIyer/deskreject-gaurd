import io

import fitz
import matplotlib.pyplot as plt
from PIL import Image, ImageDraw

plt.rcParams["pdf.fonttype"] = 42

def create_vector_figure(panels, title, figsize, fontsize, line_color_1=None, line_color_2=None):
    fig, axes = plt.subplots(1, len(panels), figsize=figsize)
    if len(panels) == 1:
        axes = [axes]
    
    for ax, label in zip(axes, panels):
        ax.plot([0, 1], [0, 1], color=line_color_1 or 'blue')
        if line_color_2:
            ax.plot([0, 1], [1, 0], color=line_color_2)
        ax.set_title(title, fontsize=fontsize)
        ax.text(0.5, 0.5, f"({label})", fontsize=fontsize, ha='center')
    
    buf = io.BytesIO()
    fig.savefig(buf, format="pdf", bbox_inches="tight")
    plt.close(fig)
    return buf.getvalue()

def create_raster_figure(text, size=(280, 200)):
    img = Image.new("RGB", size, color="white")
    draw = ImageDraw.Draw(img)
    draw.text((size[0]//2, size[1]//2), text, fill="black", anchor="mm")
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()

def build_pdf(filename, bad=True):
    doc = fitz.open()
    
    # Setup metadata
    if bad:
        doc.set_metadata({"author": "Dr. Jane Rao", "creator": "PyMuPDF", "title": "DeskReject Guard Sample"})
    else:
        doc.set_metadata({"author": "", "creator": "PyMuPDF", "title": "DeskReject Guard Sample"})

    # Create 4 pages
    for p in range(4):
        doc.new_page(width=612, height=792)  # US Letter
        
    p0 = doc[0]
    p1 = doc[1]
    p2 = doc[2]
    p3 = doc[3]

    fontname = "helv"
    
    # --- Page 1: Front matter and Intro ---
    # Title
    p0.insert_text((50, 50), "A Very Bad Paper for DeskReject Guard" if bad else "A Very Clean Paper", fontsize=18, fontname=fontname)
    
    # Author Block
    if bad:
        p0.insert_text((50, 80), "Dr. Jane Rao, John Doe", fontsize=12, fontname=fontname)
        p0.insert_text((50, 95), "Department of CSE, Example University", fontsize=12, fontname=fontname)
        p0.insert_text((50, 110), "jane.rao@example-univ.edu", fontsize=12, fontname=fontname)
    else:
        p0.insert_text((50, 80), "Anonymous Authors", fontsize=12, fontname=fontname)

    # Abstract
    p0.insert_text((50, 150), "Abstract", fontsize=14, fontname=fontname)
    p0.insert_text((50, 170), "This is the abstract of the paper.", fontsize=10, fontname=fontname)

    # Introduction
    p0.insert_text((50, 210), "1 Introduction", fontsize=14, fontname=fontname)
    
    intro_y = 230
    if bad:
        p0.insert_text((50, intro_y), "In our previous work [3], we introduced a novel method.", fontsize=10, fontname=fontname)
        intro_y += 15
        
        url = "https://github.com/rao-lab/deskproject"
        p0.insert_text((50, intro_y), f"Our code is available at {url}.", fontsize=10, fontname=fontname)
        p0.insert_link({"kind": fitz.LINK_URI, "from": fitz.Rect(50, intro_y-10, 300, intro_y+5), "uri": url})
        intro_y += 15
        
        p0.insert_text((50, intro_y), "We evaluate on the dataset.", fontsize=10, fontname=fontname)
        intro_y += 15
        
        p0.insert_text((50, intro_y), "As shown in Figure 2, the architecture is complex.", fontsize=10, fontname=fontname)
        intro_y += 15
        p0.insert_text((50, intro_y), "Then, Figure 1 shows the data.", fontsize=10, fontname=fontname)
        intro_y += 15
        p0.insert_text((50, intro_y), "See Figure 7 for an overview.", fontsize=10, fontname=fontname)
        intro_y += 15
        p0.insert_text((50, intro_y), "Table ?? shows the results.", fontsize=10, fontname=fontname)
    else:
        # Clean paper logic
        url = "https://anonymous.4open.science/r/ANON"
        p0.insert_text((50, intro_y), f"Our code is available at {url}.", fontsize=10, fontname=fontname)
        p0.insert_link({"kind": fitz.LINK_URI, "from": fitz.Rect(50, intro_y-10, 300, intro_y+5), "uri": url})
        intro_y += 15
        
        p0.insert_text((50, intro_y), "As shown in Figure 1, the data is simple.", fontsize=10, fontname=fontname)
        intro_y += 15
        p0.insert_text((50, intro_y), "Then, Figure 2 shows the architecture.", fontsize=10, fontname=fontname)
        intro_y += 15
        p0.insert_text((50, intro_y), "Figure 3 provides a system diagram.", fontsize=10, fontname=fontname)
        intro_y += 15
        p0.insert_text((50, intro_y), "Figure 4 shows a vector plot.", fontsize=10, fontname=fontname)
        intro_y += 15
        p0.insert_text((50, intro_y), "Figure 5 shows the results.", fontsize=10, fontname=fontname)
        intro_y += 15
        p0.insert_text((50, intro_y), "Table 1 shows the results.", fontsize=10, fontname=fontname)

    # Figure 1: Vector 4-panel (bad) or 3-panel (clean)
    pdf_bytes_fig1 = create_vector_figure(
        ['a', 'b', 'c', 'd'] if bad else ['a', 'b', 'c'],
        "Fig 1 Plot", (5, 2), 10
    )
    fig1_doc = fitz.open("pdf", pdf_bytes_fig1)
    p0.show_pdf_page(fitz.Rect(50, 350, 350, 450), fig1_doc, 0)
    if bad:
        p0.insert_text((50, 465), "Figure 1. Data distributions. (a) Train set. (b) Validation set. (c) Test set.", fontsize=10, fontname=fontname)
    else:
        p0.insert_text((50, 465), "Figure 1. Data distributions. (a) Train set. (b) Validation set. (c) Test set.", fontsize=10, fontname=fontname)


    # --- Page 2: Method and Figures 2, 3 ---
    p1.insert_text((50, 50), "2 Method", fontsize=14, fontname=fontname)
    
    # Figure 2: Raster DPI check
    # bad: 280 px placed at 3.3 in (~237pt) -> ~85 dpi
    # clean: 600 px placed at 3.3 in -> ~180 dpi
    px_w2 = 280 if bad else 600
    png_bytes_fig2 = create_raster_figure("System Architecture", size=(px_w2, int(px_w2*0.7)))
    p1.insert_image(fitz.Rect(50, 80, 50 + 237, 80 + 237*0.7), stream=png_bytes_fig2)
    p1.insert_text((50, 80 + 237*0.7 + 15), "Figure 2. System architecture.", fontsize=10, fontname=fontname)

    # Figure 3: Logo check
    text3 = "EXAMPLE UNIVERSITY, Robotics Lab" if bad else "System Pipeline"
    png_bytes_fig3 = create_raster_figure(text3, size=(400, 200))
    p1.insert_image(fitz.Rect(50, 350, 350, 500), stream=png_bytes_fig3)
    p1.insert_text((50, 515), "Figure 3. System diagram.", fontsize=10, fontname=fontname)

    # --- Page 3: Figures 4, 5 ---
    p2.insert_text((50, 50), "3 Results", fontsize=14, fontname=fontname)
    
    # Figure 4: Vector font size check
    # bad: 9pt text at 7in wide, placed at 3.3in wide (237pt) -> ~4.2pt effective
    # clean: 16pt text at 7in wide, placed at 3.3in wide -> ~7.5pt effective
    fontsize4 = 9 if bad else 20
    pdf_bytes_fig4 = create_vector_figure(['a'], "Vector Plot", (7, 3), fontsize4)
    fig4_doc = fitz.open("pdf", pdf_bytes_fig4)
    p2.show_pdf_page(fitz.Rect(50, 80, 50 + 237, 80 + 237*(3/7)), fig4_doc, 0)
    p2.insert_text((50, 80 + 237*(3/7) + 15), "Figure 4. Vector plot.", fontsize=10, fontname=fontname)

    # Figure 5: Colorblind check
    # bad: #d62728 and #2ca02c (red/green)
    # clean: okabe-ito palette colors
    c1, c2 = ("#d62728", "#2ca02c") if bad else ("#E69F00", "#56B4E9")
    pdf_bytes_fig5 = create_vector_figure(['a'], "Results", (4, 3), 10, c1, c2)
    fig5_doc = fitz.open("pdf", pdf_bytes_fig5)
    p2.show_pdf_page(fitz.Rect(50, 250, 350, 475), fig5_doc, 0)
    p2.insert_text((50, 490), "Figure 5. Results using line plot.", fontsize=10, fontname=fontname)

    p2.insert_text((50, 530), "Table 1. Dataset stats.", fontsize=10, fontname=fontname)


    # --- Page 4: Back matter ---
    p3.insert_text((50, 50), "4 Conclusion", fontsize=14, fontname=fontname)
    p3.insert_text((50, 70), "We conclude the paper here.", fontsize=10, fontname=fontname)
    
    y = 100
    if bad:
        p3.insert_text((50, y), "Acknowledgements", fontsize=14, fontname=fontname)
        y += 20
        p3.insert_text((50, y), "We thank the EXAMPLE UNIVERSITY Robotics Lab for funding.", fontsize=10, fontname=fontname)
        y += 30
        
        p3.insert_text((50, y), "Ethics Statement", fontsize=14, fontname=fontname)
        y += 20
        p3.insert_text((50, y), "This research was approved by the IRB.", fontsize=10, fontname=fontname)
        y += 30
    else:
        p3.insert_text((50, y), "Data Availability", fontsize=14, fontname=fontname)
        y += 20
        p3.insert_text((50, y), "Data is available upon request.", fontsize=10, fontname=fontname)
        y += 30
        
        p3.insert_text((50, y), "Conflict of Interest", fontsize=14, fontname=fontname)
        y += 20
        p3.insert_text((50, y), "The authors declare no conflicts of interest.", fontsize=10, fontname=fontname)
        y += 30
        
        p3.insert_text((50, y), "AI Use", fontsize=14, fontname=fontname)
        y += 20
        p3.insert_text((50, y), "No AI was used in this research.", fontsize=10, fontname=fontname)
        y += 30

    p3.insert_text((50, y), "References", fontsize=14, fontname=fontname)
    y += 20
    p3.insert_text((50, y), "[1] Doe, J. (2024). Some paper.", fontsize=10, fontname=fontname)
    y += 15
    p3.insert_text((50, y), "[2] Smith, A. (2023). Another paper.", fontsize=10, fontname=fontname)
    if bad:
        y += 15
        p3.insert_text((50, y), "[3] Rao, J. (2025). Previous Work.", fontsize=10, fontname=fontname)

    doc.save(filename)
    doc.close()

def write_expected_json():
    import json
    data = [
        {"code": "ANON_METADATA_AUTHOR", "figure_id": None, "priority": "P0"},
        {"code": "ANON_AUTHOR_BLOCK", "figure_id": None, "priority": "P0"},
        {"code": "ANON_EMAIL", "figure_id": None, "priority": "P0"},
        {"code": "ANON_AFFILIATION", "figure_id": None, "priority": "P0"},
        {"code": "ANON_REPO_URL", "figure_id": None, "priority": "P0"},
        {"code": "ANON_SELF_CITE", "figure_id": None, "priority": "P0"},
        {"code": "ANON_ACK", "figure_id": None, "priority": "P0"},
        {"code": "ANON_LOGO_IN_FIGURE", "figure_id": "Figure 3", "priority": "P0"},
        {"code": "FIG_PANEL_UNREFERENCED", "figure_id": "Figure 1", "priority": "P0"},
        {"code": "SEQ_OUT_OF_ORDER", "figure_id": None, "priority": "P0"},
        {"code": "SEQ_GHOST", "figure_id": "Figure 4", "priority": "P0"},
        {"code": "SEQ_ORPHAN_REF", "figure_id": "Figure 7", "priority": "P0"},
        {"code": "SEQ_UNRESOLVED_REF", "figure_id": None, "priority": "P0"},
        {"code": "STMT_MISSING_DATA_AVAILABILITY", "figure_id": None, "priority": "P0"},
        {"code": "STMT_MISSING_CONFLICT_OF_INTEREST", "figure_id": None, "priority": "P0"},
        {"code": "STMT_MISSING_AI_USE", "figure_id": None, "priority": "P0"},
        {"code": "LEG_RASTER_LOW_DPI", "figure_id": "Figure 2", "priority": "P1"},
        {"code": "LEG_FONT_TOO_SMALL", "figure_id": "Figure 4", "priority": "P1"},
        {"code": "ACC_CB_INDISTINGUISHABLE", "figure_id": "Figure 5", "priority": "P1"}
    ]
    with open("samples/expected.json", "w") as f:
        json.dump(data, f, indent=4)

def write_bad_paper_tex():
    tex = r"""\documentclass[final]{article}
\usepackage{graphicx}
\usepackage{hyperref}

\title{A Very Bad Paper for DeskReject Guard}
\author{Dr. Jane Rao \and John Doe}

\begin{document}

\maketitle

\begin{abstract}
This is the abstract.
\end{abstract}

\section{Introduction}
In our previous work [3], we introduced a novel method. 
Our code is available at \url{https://github.com/rao-lab/deskproject}.
See Figure 7 for an overview.
Table ?? shows the results.
Figure 2 shows the architecture, and then Figure 1 shows the data.

\begin{figure}[h]
\centering
\includegraphics[width=0.48\textwidth]{fig1}
\caption{Data distributions. (a) Train set. (b) Validation set. (c) Test set.}
\end{figure}

\section{Method}

\begin{figure}[h]
\centering
\includegraphics[width=0.48\textwidth]{fig2}
\caption{System architecture.}
\end{figure}

\begin{figure}[h]
\centering
\includegraphics[width=0.48\textwidth]{fig3}
\caption{System diagram with crest.}
\end{figure}

\begin{figure}[h]
\centering
\includegraphics[width=0.48\textwidth]{fig4}
\caption{Vector plot with tiny text.}
\end{figure}

\section{Acknowledgements}
We thank the EXAMPLE UNIVERSITY Robotics Lab for funding.

\section{Ethics Statement}
This research was approved by the IRB.

\begin{thebibliography}{9}
\bibitem{rao2025}
Rao, J. (2025). Previous Work.
\end{thebibliography}

\end{document}
"""
    with open("samples/bad_paper.tex", "w") as f:
        f.write(tex)

if __name__ == "__main__":
    build_pdf("samples/bad_paper.pdf", bad=True)
    build_pdf("samples/clean_paper.pdf", bad=False)
    write_expected_json()
    write_bad_paper_tex()
    print("Generated bad_paper.pdf, clean_paper.pdf, expected.json and bad_paper.tex")
