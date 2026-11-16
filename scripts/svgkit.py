"""Shared design tokens + SVG primitives for the profile README.

Design rules
  * Canvas is 900px wide, matching the GitHub README column, so text renders ~1:1.
  * Panels paint their own dark background, so they read correctly in light mode too.
  * Steel gradient on titles, numbers and hairlines only. Brand colour appears only in the stack.
"""
import html
import os

e = html.escape
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS = os.path.join(ROOT, "assets")

W = 900
GAP = 32  # transparent breathing room baked into the top of every section SVG

FONT = "ui-monospace,SFMono-Regular,'JetBrains Mono','Fira Code',Menlo,Consolas,'DejaVu Sans Mono','Liberation Mono',monospace"
BG, PANEL_TOP, PANEL_BOT = "#0b0c0d", "#16191c", "#0c0d0f"
LINE, DIM, MID, HI = "#24282c", "#6b727a", "#9aa1a8", "#e4e7ea"

DEFS = f"""<defs>
<linearGradient id="steel" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#f4f6f7"/><stop offset=".5" stop-color="#a4abb2"/><stop offset="1" stop-color="#5f666d"/></linearGradient>
<linearGradient id="edge" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#9aa1a8" stop-opacity="0"/><stop offset=".5" stop-color="#c3c8cd" stop-opacity=".7"/><stop offset="1" stop-color="#9aa1a8" stop-opacity="0"/></linearGradient>
<linearGradient id="fade" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#9aa1a8" stop-opacity=".8"/><stop offset="1" stop-color="#9aa1a8" stop-opacity="0"/></linearGradient>
<linearGradient id="panel" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{PANEL_TOP}"/><stop offset="1" stop-color="{PANEL_BOT}"/></linearGradient>
<pattern id="grid" width="24" height="24" patternUnits="userSpaceOnUse"><path d="M24 0H0V24" fill="none" stroke="#ffffff" stroke-opacity=".035"/></pattern>
<filter id="blur4" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="4"/></filter>
<filter id="blur8" x="-100%" y="-100%" width="300%" height="300%"><feGaussianBlur stdDeviation="8"/></filter>
</defs>"""


def svg(w, h, body, label, extra_defs="", canvas=False, grid=False):
    """canvas=True paints a full-bleed dark background (header only)."""
    bg = ""
    if canvas:
        bg = f'<rect width="{w}" height="{h}" fill="{BG}"/>'
        if grid:
            bg += f'<rect width="{w}" height="{h}" fill="url(#grid)"/>'
    return (f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" '
            f'viewBox="0 0 {w} {h}" width="{w}" height="{h}" role="img" aria-label="{e(label)}" '
            f'font-family="{FONT}">{DEFS}{extra_defs}{bg}{body}</svg>')


def put(rel, s):
    path = os.path.join(ASSETS, rel)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(s)
    return path


def hline(x, y, w, fill="url(#edge)", op=1):
    if w <= 0:
        return ""
    return f'<rect x="{x}" y="{y}" width="{w}" height="1" fill="{fill}" fill-opacity="{op}"/>'


def vline(x, y, h, fill=LINE, op=1):
    return f'<rect x="{x}" y="{y}" width="1" height="{h}" fill="{fill}" fill-opacity="{op}"/>'


def brackets(w, h, m=12, l=18, op=.55):
    p = [f"M{m} {m+l}V{m}H{m+l}", f"M{w-m-l} {m}H{w-m}V{m+l}",
         f"M{m} {h-m-l}V{h-m}H{m+l}", f"M{w-m-l} {h-m}H{w-m}V{h-m-l}"]
    return "".join(f'<path d="{d}" fill="none" stroke="{MID}" stroke-opacity="{op}"/>' for d in p)


def blink(x, y, s=8, fill=HI, dur="2s", lo=".15"):
    return (f'<rect x="{x}" y="{y}" width="{s}" height="{s}" fill="{fill}">'
            f'<animate attributeName="opacity" values="1;{lo};1" dur="{dur}" repeatCount="indefinite"/></rect>')


def state_mark(x, y, state):
    if state in ("LIVE", "RUNNING"):
        return blink(x, y)
    return f'<rect x="{x+.5}" y="{y+.5}" width="7" height="7" fill="none" stroke="{MID}"/>'


def panel(x, y, w, h, accent=True):
    """Bordered steel panel with a 1px steel hairline along the bottom edge."""
    s = f'<rect x="{x+.5}" y="{y+.5}" width="{w-1}" height="{h-1}" fill="url(#panel)" stroke="{LINE}"/>'
    if accent:
        s += hline(x, y + h - 1, w, "url(#steel)", .85)
    return s


def section_header(label, tag, y=0, width=W):
    """40px tall `[ LABEL ]` bar with a fading hairline and a right-aligned tag."""
    lx = 22
    label_w = len(label) * (12 * .6 + 2.5)
    tag_w = len(tag) * (11 * .6 + 1.5)
    x0 = int(lx + label_w + 14)
    x1 = int(width - tag_w - 16)
    return (f'<g transform="translate(0,{y})">'
            f'<rect x="0" y="15" width="8" height="8" fill="url(#steel)"/>'
            f'<text x="{lx}" y="24" font-size="12" font-weight="700" letter-spacing="2.5" fill="{HI}">{e(label)}</text>'
            f'{hline(x0, 19, x1 - x0, "url(#fade)")}'
            f'<text x="{width}" y="24" text-anchor="end" font-size="11" letter-spacing="1.5" fill="{DIM}">{e(tag)}</text></g>')
