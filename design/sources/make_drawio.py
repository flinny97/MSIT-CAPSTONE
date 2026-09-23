#!/usr/bin/env python3
"""Editable draw.io file. Same layout as the PNGs: plain boxes, straight lines, no notes."""
from pathlib import Path
from xml.sax.saxutils import escape

OUT = Path(__file__).resolve().parent.parent / "MSIT5910_Unit3_Diagrams.drawio"

FONT = "Times New Roman"
FS = 16          # 16 px = 12 pt
K = 1.4          # scale from the PNG coordinate system
INK = "#000000"

BLUE_F, BLUE_S = "#DCEAF8", "#2878D0"
ORANGE_F, ORANGE_S = "#FBE4DB", "#D2552A"
TEAL_F, TEAL_S = "#DAF3EA", "#12A273"
AMBER_F, AMBER_S = "#FDF0D5", "#D18E0A"
PINK_F, PINK_S = "#FBE4ED", "#D96A94"
GREY_S = "#808080"

_n = [0]


def nid():
    _n[0] += 1
    return f"c{_n[0]}"


def style(fill, stroke, bold=False):
    return (f"rounded=0;whiteSpace=wrap;html=1;fillColor={fill};strokeColor={stroke};"
            f"fontFamily={FONT};fontSize={FS};fontColor={INK};fontStyle={1 if bold else 0};"
            f"verticalAlign=middle;align=center;")


class Page:
    """Boxes are placed in PNG coordinates (y up) and converted to draw.io (y down)."""

    def __init__(self, name, w, h):
        self.name, self.w, self.h = name, w, h
        self.cells = []

    def box(self, x, y, w, h, text, st):
        cid = nid()
        X, Y = round(x * K), round((self.h - y - h) * K)
        self.cells.append(
            f'<mxCell id="{cid}" value="{escape(text)}" style="{st}" vertex="1" parent="1">'
            f'<mxGeometry x="{X}" y="{Y}" width="{round(w * K)}" height="{round(h * K)}" '
            f'as="geometry"/></mxCell>')
        return cid

    def text(self, x, y, w, h, s, bold=False, align="center"):
        st = (f"text;html=1;strokeColor=none;fillColor=none;align={align};verticalAlign=middle;"
              f"whiteSpace=wrap;fontFamily={FONT};fontSize={FS};fontColor={INK};"
              f"fontStyle={1 if bold else 0};")
        return self.box(x, y, w, h, s, st)

    def line(self, pts, arrow=True, color=INK, width=1):
        """Straight polyline through PNG-space points."""
        P = [(round(px * K), round((self.h - py) * K)) for px, py in pts]
        wp = "".join(f'<mxPoint x="{x}" y="{y}"/>' for x, y in P[1:-1])
        st = (f"html=1;rounded=0;edgeStyle=orthogonalEdgeStyle;"
              f"endArrow={'block' if arrow else 'none'};endFill=1;"
              f"strokeColor={color};strokeWidth={width};exitDx=0;exitDy=0;")
        self.cells.append(
            f'<mxCell id="{nid()}" style="{st}" edge="1" parent="1">'
            f'<mxGeometry relative="1" as="geometry">'
            f'<mxPoint x="{P[0][0]}" y="{P[0][1]}" as="sourcePoint"/>'
            f'<mxPoint x="{P[-1][0]}" y="{P[-1][1]}" as="targetPoint"/>'
            f'<Array as="points">{wp}</Array></mxGeometry></mxCell>')

    def xml(self):
        return (f'<diagram id="{self.name.lower().replace(" ", "-")}" name="{escape(self.name)}">'
                f'<mxGraphModel dx="1200" dy="800" grid="0" gridSize="10" guides="1" '
                f'tooltips="1" connect="1" arrows="1" fold="1" page="1" pageScale="1" '
                f'pageWidth="{round(self.w * K)}" pageHeight="{round(self.h * K)}" '
                f'math="0" shadow="0"><root><mxCell id="0"/><mxCell id="1" parent="0"/>'
                f'{"".join(self.cells)}</root></mxGraphModel></diagram>')


# ------------------------------------------------------------------ figure 1
p1 = Page("System Architecture", 650, 672)

p1.box(40, 612, 250, 40, "Participant", style(ORANGE_F, ORANGE_S))
p1.box(360, 612, 250, 40, "Researcher", style(ORANGE_F, ORANGE_S))

p1.box(20, 500, 610, 85, "", style("none", GREY_S))
p1.text(30, 560, 200, 22, "Presentation Layer", align="left")
p1.box(40, 512, 250, 42, "Participant Interface", style(BLUE_F, BLUE_S))
p1.box(360, 512, 250, 42, "Administrator Interface", style(BLUE_F, BLUE_S))

p1.box(20, 340, 610, 130, "", style("none", GREY_S))
p1.text(30, 445, 200, 22, "Application Layer", align="left")
for x, t in [(40, "M1\nTraining Delivery"), (243, "M2\nAssessment Collection"),
             (446, "M4\nAnalysis and Reporting")]:
    p1.box(x, 355, 184, 85, t, style(TEAL_F, TEAL_S))

p1.box(20, 170, 610, 140, "", style("none", GREY_S))
p1.text(30, 285, 200, 22, "Data Layer", align="left")
p1.box(40, 185, 570, 95, "", style("none", AMBER_S))
p1.text(150, 252, 350, 24, "M3   Data Storage and Security", bold=True)
p1.box(60, 198, 255, 48, "Content Repository", style(AMBER_F, AMBER_S))
p1.box(335, 198, 255, 48, "Assessment Data Store", style(AMBER_F, AMBER_S))

p1.box(20, 60, 610, 72, "Security and Privacy Controls\nConsent, participant IDs, encryption, "
                        "least-privilege access", style(PINK_F, PINK_S))

for pts in [[(165, 612), (165, 554)], [(485, 612), (485, 554)],
            [(132, 512), (132, 440)], [(240, 512), (240, 476), (335, 476), (335, 440)],
            [(538, 512), (538, 440)], [(224, 397), (243, 397)], [(427, 397), (446, 397)],
            [(100, 355), (100, 280)], [(335, 355), (335, 280)], [(538, 280), (538, 355)],
            [(325, 170), (325, 132)]]:
    p1.line(pts)

# ------------------------------------------------------------------ figure 2
p2 = Page("Data Flow Diagram", 650, 556)

for t, y in [("1.0   Enrol and Obtain Consent", 425), ("2.0   Deliver Pre-Assessment", 345),
             ("3.0   Deliver Training Module", 265), ("4.0   Deliver Post-Assessment", 185),
             ("5.0   Analyse and Report", 105)]:
    p2.box(195, y, 260, 46, t, style(TEAL_F, TEAL_S))
p2.box(195, 500, 260, 35, "Participant", style(ORANGE_F, ORANGE_S))
p2.box(195, 40, 260, 35, "Researcher", style(ORANGE_F, ORANGE_S))
p2.box(20, 295, 150, 46, "D1   Content Repository", style(AMBER_F, AMBER_S))
p2.box(480, 145, 150, 46, "D2   Assessment Data Store", style(AMBER_F, AMBER_S))

for pts in [[(325, 500), (325, 471)], [(325, 425), (325, 391)], [(325, 345), (325, 311)],
            [(325, 265), (325, 231)], [(325, 185), (325, 151)], [(325, 105), (325, 75)],
            [(95, 341), (95, 368), (195, 368)], [(95, 295), (95, 288), (195, 288)],
            [(555, 368), (555, 191)], [(500, 145), (500, 128), (455, 128)]]:
    p2.line(pts)
p2.line([(455, 368), (555, 368)], arrow=False)
p2.line([(455, 208), (555, 208)], arrow=False)

p2.text(105, 375, 70, 22, "items")
p2.text(105, 266, 70, 22, "content")
p2.text(560, 293, 90, 22, "responses")
p2.text(505, 105, 80, 22, "records")

# ------------------------------------------------------------------ figure 3
p3 = Page("Branching Model", 650, 300)
p3.box(20, 230, 110, 40, "main", style(BLUE_F, BLUE_S))
p3.box(20, 80, 110, 40, "development", style(ORANGE_F, ORANGE_S))
p3.line([(140, 250), (620, 250)], arrow=False, color=BLUE_S, width=2)
p3.line([(210, 100), (520, 100)], arrow=False, color=ORANGE_S, width=2)

dot = ("ellipse;whiteSpace=wrap;html=1;fillColor=#FFFFFF;strokeWidth=2;fontSize=1;"
       "strokeColor=")
for x in (165, 570):
    p3.box(x - 8, 242, 16, 16, "", dot + BLUE_S + ";")
for i in range(7):
    p3.box(240 + i * 41.7 - 8, 92, 16, 16, "", dot + ORANGE_S + ";")

p3.line([(165, 242), (165, 100), (205, 100)])
p3.line([(520, 100), (570, 100), (570, 242)])
p3.text(100, 274, 140, 22, "initial commit")
p3.text(505, 274, 140, 22, "merge and tag")
p3.text(180, 164, 90, 22, "branch", align="left")
p3.text(210, 30, 320, 40, "commits for documents, diagrams, requirements,\n"
                          "content, and scoring code")

xml = ('<mxfile host="app.diagrams.net" agent="MSIT5910" version="24.7.17" type="device">'
       + p1.xml() + p2.xml() + p3.xml() + '</mxfile>')
OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(xml, encoding="utf-8")

import xml.dom.minidom as md
md.parseString(xml)
print(f"Saved {OUT} ({len(xml):,} bytes, 3 pages, valid XML)")
