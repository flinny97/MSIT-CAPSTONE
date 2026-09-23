"""
Capstone figures, rebuilt plain.

Design rules:
  - Liberation Serif (metrically identical to Times New Roman), 12 pt everywhere.
  - Figures are drawn at their final printed width (6.5 in), so 12 pt on the
    canvas is 12 pt on the page. Coordinates are hundredths of an inch.
  - Straight segments only. No curves, no arcs.
  - Boxes carry names. Details live in the tables, not inside the shapes.
"""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, FancyArrow

# figures are written into the design/ folder, one level up from this script
OUT_DIR = Path(__file__).resolve().parent.parent

FONT = "Liberation Serif"   # Times New Roman metrics
FS = 12
plt.rcParams["font.family"] = FONT
plt.rcParams["font.size"] = FS

# Unit 2 Gantt palette
BLUE_F, BLUE_S = "#DCEAF8", "#2878D0"
ORANGE_F, ORANGE_S = "#FBE4DB", "#D2552A"
TEAL_F, TEAL_S = "#DAF3EA", "#12A273"
AMBER_F, AMBER_S = "#FDF0D5", "#D18E0A"
PINK_F, PINK_S = "#FBE4ED", "#D96A94"
GREY_F, GREY_S = "#FFFFFF", "#808080"
INK = "#000000"

W = 650  # 6.5 inches


def canvas(height_units):
    fig, ax = plt.subplots(figsize=(W / 100, height_units / 100))
    ax.set_xlim(0, W)
    ax.set_ylim(0, height_units)
    ax.axis("off")
    fig.subplots_adjust(left=0, right=1, top=1, bottom=0)
    return fig, ax


def rect(ax, x, y, w, h, fill, stroke, lw=1.0, z=2):
    ax.add_patch(Rectangle((x, y), w, h, facecolor=fill, edgecolor=stroke,
                           linewidth=lw, zorder=z))


def label(ax, x, y, s, bold=False, size=FS, color=INK, ha="center", va="center", z=5):
    ax.text(x, y, s, ha=ha, va=va, fontsize=size, color=color, zorder=z,
            fontweight="bold" if bold else "normal", linespacing=1.25)


def aline(ax, pts, z=4, lw=1.0, head=True, ls="-"):
    """Straight polyline through pts, optional arrowhead on the final segment."""
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    ax.plot(xs, ys, color=INK, lw=lw, zorder=z, solid_capstyle="butt", ls=ls)
    if head:
        x0, y0 = pts[-2]
        x1, y1 = pts[-1]
        dx, dy = x1 - x0, y1 - y0
        n = (dx ** 2 + dy ** 2) ** 0.5
        dx, dy = dx / n, dy / n
        ax.add_patch(FancyArrow(x1 - dx * 8, y1 - dy * 8, dx * 8, dy * 8,
                                width=0, head_width=7, head_length=8,
                                length_includes_head=True, color=INK, zorder=z + 1))


def vlink(ax, x, y_top, y_bot, **kw):
    aline(ax, [(x, y_top), (x, y_bot)], **kw)


def elbow(ax, x0, y0, x1, y1, **kw):
    """Vertical then horizontal then vertical, all straight."""
    ymid = (y0 + y1) / 2
    aline(ax, [(x0, y0), (x0, ymid), (x1, ymid), (x1, y1)], **kw)


# ====================================================================== FIGURE 1
def figure1():
    H = 672
    fig, ax = canvas(H)

    # actors
    rect(ax, 40, 612, 250, 40, ORANGE_F, ORANGE_S)
    label(ax, 165, 632, "Participant")
    rect(ax, 360, 612, 250, 40, ORANGE_F, ORANGE_S)
    label(ax, 485, 632, "Researcher")

    # presentation layer
    rect(ax, 20, 500, 610, 85, "#FFFFFF", GREY_S, lw=0.8, z=1)
    label(ax, 30, 572, "Presentation Layer", ha="left", size=FS)
    rect(ax, 40, 512, 250, 42, BLUE_F, BLUE_S)
    label(ax, 165, 533, "Participant Interface")
    rect(ax, 360, 512, 250, 42, BLUE_F, BLUE_S)
    label(ax, 485, 533, "Administrator Interface")

    # application layer
    rect(ax, 20, 340, 610, 130, "#FFFFFF", GREY_S, lw=0.8, z=1)
    label(ax, 30, 457, "Application Layer", ha="left", size=FS)
    mods = [(40, "M1", "Training\nDelivery"), (243, "M2", "Assessment\nCollection"),
            (446, "M4", "Analysis and\nReporting")]
    for x, tag, name in mods:
        rect(ax, x, 355, 184, 85, TEAL_F, TEAL_S)
        label(ax, x + 92, 424, tag, bold=True)
        label(ax, x + 92, 392, name)

    # data layer
    rect(ax, 20, 170, 610, 140, "#FFFFFF", GREY_S, lw=0.8, z=1)
    label(ax, 30, 297, "Data Layer", ha="left", size=FS)
    rect(ax, 40, 185, 570, 95, "#FFFFFF", AMBER_S)
    label(ax, 325, 263, "M3   Data Storage and Security", bold=True)
    rect(ax, 60, 198, 255, 48, AMBER_F, AMBER_S)
    label(ax, 187, 222, "Content Repository")
    rect(ax, 335, 198, 255, 48, AMBER_F, AMBER_S)
    label(ax, 462, 222, "Assessment Data Store")

    # security controls
    rect(ax, 20, 60, 610, 72, PINK_F, PINK_S)
    label(ax, 325, 110, "Security and Privacy Controls", bold=True)
    label(ax, 325, 80, "Consent, participant IDs, encryption,\nleast-privilege access")

    # straight connectors
    vlink(ax, 165, 612, 554)
    vlink(ax, 485, 612, 554)
    vlink(ax, 132, 512, 440)          # participant interface -> M1
    elbow(ax, 240, 512, 335, 440)     # participant interface -> M2
    vlink(ax, 538, 512, 440)          # admin interface -> M4
    aline(ax, [(224, 397), (243, 397)])      # M1 -> M2
    aline(ax, [(427, 397), (446, 397)])      # M2 -> M4
    vlink(ax, 100, 355, 280)          # M1 -> M3
    vlink(ax, 335, 355, 280)          # M2 -> M3
    vlink(ax, 538, 280, 355)          # M3 -> M4
    vlink(ax, 325, 170, 132)          # data layer -> security controls

    fig.savefig(OUT_DIR / "figure1-system-architecture.png",
                dpi=300, facecolor="white", bbox_inches="tight", pad_inches=0.05)
    plt.close(fig)


# ====================================================================== FIGURE 2
def figure2():
    H = 556
    fig, ax = canvas(H)

    bx, bw, bh = 195, 260, 46
    steps = [
        ("1.0   Enrol and Obtain Consent", 425),
        ("2.0   Deliver Pre-Assessment", 345),
        ("3.0   Deliver Training Module", 265),
        ("4.0   Deliver Post-Assessment", 185),
        ("5.0   Analyse and Report", 105),
    ]
    for name, y in steps:
        rect(ax, bx, y, bw, bh, TEAL_F, TEAL_S)
        label(ax, bx + bw / 2, y + bh / 2, name)

    rect(ax, bx, 500, bw, 35, ORANGE_F, ORANGE_S)
    label(ax, bx + bw / 2, 517, "Participant")
    rect(ax, bx, 40, bw, 35, ORANGE_F, ORANGE_S)
    label(ax, bx + bw / 2, 57, "Researcher")

    rect(ax, 20, 295, 150, 46, AMBER_F, AMBER_S)
    label(ax, 95, 318, "D1   Content\nRepository")
    rect(ax, 480, 145, 150, 46, AMBER_F, AMBER_S)
    label(ax, 555, 168, "D2   Assessment\nData Store")

    vlink(ax, 325, 500, 471)
    for i in range(len(steps) - 1):
        vlink(ax, 325, steps[i][1], steps[i + 1][1] + bh)
    vlink(ax, 325, 105, 75)

    aline(ax, [(95, 341), (95, 368), (195, 368)])
    aline(ax, [(95, 295), (95, 288), (195, 288)])
    label(ax, 140, 382, "items")
    label(ax, 140, 273, "content")

    # both assessments write to D2 through one line
    aline(ax, [(455, 368), (555, 368)], head=False)
    aline(ax, [(455, 208), (555, 208)], head=False)
    aline(ax, [(555, 368), (555, 191)])
    label(ax, 592, 300, "responses")

    aline(ax, [(500, 145), (500, 128), (455, 128)])
    label(ax, 515, 112, "records", ha="left")

    fig.savefig(OUT_DIR / "figure2-data-flow-diagram.png",
                dpi=300, facecolor="white", bbox_inches="tight", pad_inches=0.05)
    plt.close(fig)


# ====================================================================== FIGURE 3
def figure3():
    H = 300
    fig, ax = canvas(H)

    y_main, y_dev = 250, 100

    rect(ax, 20, y_main - 20, 110, 40, BLUE_F, BLUE_S)
    label(ax, 75, y_main, "main")
    rect(ax, 20, y_dev - 20, 110, 40, ORANGE_F, ORANGE_S)
    label(ax, 75, y_dev, "development")

    ax.plot([140, 620], [y_main, y_main], color=BLUE_S, lw=1.4, zorder=2)
    ax.plot([210, 520], [y_dev, y_dev], color=ORANGE_S, lw=1.4, zorder=2)

    for x in (165, 570):
        ax.add_patch(plt.Circle((x, y_main), 8, facecolor="white",
                                edgecolor=BLUE_S, lw=1.4, zorder=3))
    for i in range(7):
        ax.add_patch(plt.Circle((240 + i * 41.7, y_dev), 8, facecolor="white",
                                edgecolor=ORANGE_S, lw=1.4, zorder=3))

    aline(ax, [(165, 242), (165, y_dev), (205, y_dev)])
    aline(ax, [(520, y_dev), (570, y_dev), (570, 242)])

    label(ax, 165, 285, "initial commit")
    label(ax, 570, 285, "merge and tag")
    label(ax, 180, 175, "branch", ha="left")

    label(ax, 365, 45, "commits for documents, diagrams, requirements,\ncontent, and scoring code")

    fig.savefig(OUT_DIR / "figure3-branching-model.png",
                dpi=300, facecolor="white", bbox_inches="tight", pad_inches=0.05)
    plt.close(fig)


figure1()
figure2()
figure3()
print("three figures rebuilt at 6.5 in wide, Liberation Serif 12 pt, straight connectors")
