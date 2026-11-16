#!/usr/bin/env python3
"""Builds the static README graphics. Edit the DATA block, then run:
    python scripts/build_assets.py
(The contribution snake and activity panel are built by build_activity.py.)
"""
import base64
import io
import json
import os

from svgkit import (BG, DIM, GAP, HI, LINE, MID, ROOT, W, blink, brackets, e, hline, panel,
                    put, section_header, state_mark, svg, vline)

# ------------------------------------------------------------------ DATA
STATS = [
    ("30+", ["production systems", "shipped"]),
    ("02", ["major next-gen", "labs running"]),
    ("16", ["age at first line", "of JS + CSS"]),
    ("0", ["GPS required", "for autonomy"]),
]

LABS = [
    dict(key="nafrok", name="NAFROK", role="NEXT-GEN WEB LAB", path="~/labs/nafrok",
         lines=("Full-stack production sites. Fixed pricing,", "ruthless timelines, measurable results."),
         tags=["Next.js", "Tailwind", "Vercel", "Fixed-price"]),
    dict(key="aixrobo", name="AIxRobo", role="NEXT-GEN RESEARCH LAB", path="~/labs/aixrobo",
         lines=("Autonomous drones, humanoid robotics and", "LLM-powered physical intelligence."),
         tags=["PyTorch", "C++", "LLM", "Robotics"]),
]

# lab = which lab the project belongs to (edit if I guessed wrong)
PROJECTS = [
    dict(pid="0x01", proc="AIxDRONE", lab="AIxROBO", focus="GPS-denied navigation",
         stack="Python · C++ · OpenCV", state="R&D"),
    dict(pid="0x02", proc="AIxRESCUE", lab="AIxROBO", focus="Hostile-environment autonomy",
         stack="Python · OpenCV · Embedded", state="R&D"),
    dict(pid="0x03", proc="SLATEBOOKS", lab="NAFROK", focus="MERN storefront + payments",
         stack="MongoDB · Express · React · Node", state="LIVE"),
    dict(pid="0x04", proc="RETAIL JOINTS", lab="NAFROK", focus="Production retail system",
         stack="Full-stack · Production", state="LIVE"),
]

STACK = [
    ("LANGUAGES", ["Python", "JavaScript", "TypeScript", "C++", "Kotlin"]),
    ("FRONTEND / MOBILE", ["Next.js", "React", "Tailwind", "Android Studio"]),
    ("BACKEND / DATA", ["Node.js", "FastAPI", "MongoDB", "PostgreSQL", "Redis"]),
    ("AI / ROBOTICS", ["TensorFlow", "PyTorch", "OpenCV", "Raspberry Pi", "Arduino"]),
    ("DEVOPS / TOOLS", ["Docker", "Linux", "Git", "Vercel", "Figma"]),
]
ICONS = json.load(open(os.path.join(ROOT, "scripts", "brand_icons.json"), encoding="utf-8"))
NEAR_BLACK = {"000000"}  # brand colours that vanish on a dark panel get steel white instead


# ------------------------------------------------------------------ HEADER
def header():
    H = 280
    cx, cy = 730, 140
    b = brackets(W, H)
    b += f'<text x="32" y="36" font-size="11" letter-spacing="2" fill="{DIM}">RA9 // AH KHAN</text>'
    b += blink(768, 28)
    b += f'<text x="868" y="36" text-anchor="end" font-size="11" letter-spacing="2" fill="{DIM}">SYS.ONLINE</text>'
    b += hline(32, 52, 836)
    b += '<text x="30" y="136" font-size="72" font-weight="800" letter-spacing="-1" fill="url(#steel)">AH KHAN</text>'
    b += (f'<rect x="32" y="158" width="12" height="24" fill="{HI}">'
          '<animate attributeName="opacity" values="1;0;1" dur="1.1s" repeatCount="indefinite"/></rect>')
    for i, t in enumerate(["Full-Stack Systems", "AI / ML Engineering", "Autonomous Robotics"]):
        b += (f'<text x="56" y="178" font-size="22" fill="{HI}" opacity="{1 if i == 0 else 0}">{e(t)}'
              f'<animate attributeName="opacity" values="0;1;1;0;0" keyTimes="0;.03;.30;.33;1" '
              f'dur="9s" begin="{i*3}s" repeatCount="indefinite"/></text>')
    b += f'<text x="32" y="216" font-size="13" fill="{DIM}">aka Ra9&#160;&#160;//&#160;&#160;founder of NAFROK + AIxRobo</text>'
    for r, op in ((84, .22), (56, .32), (28, .5)):
        b += f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="{MID}" stroke-opacity="{op}"/>'
    b += (f'<circle cx="{cx}" cy="{cy}" r="70" fill="none" stroke="{MID}" stroke-opacity=".6" stroke-dasharray="2 8">'
          f'<animateTransform attributeName="transform" type="rotate" from="0 {cx} {cy}" to="360 {cx} {cy}" dur="40s" repeatCount="indefinite"/></circle>')
    b += f'<line x1="{cx-100}" y1="{cy}" x2="{cx+100}" y2="{cy}" stroke="{MID}" stroke-opacity=".2"/>'
    b += f'<line x1="{cx}" y1="{cy-100}" x2="{cx}" y2="{cy+100}" stroke="{MID}" stroke-opacity=".2"/>'
    b += (f'<line x1="{cx}" y1="{cy}" x2="{cx+84}" y2="{cy}" stroke="{HI}" stroke-opacity=".7">'
          f'<animateTransform attributeName="transform" type="rotate" from="0 {cx} {cy}" to="360 {cx} {cy}" dur="8s" repeatCount="indefinite"/></line>')
    b += f'<rect x="{cx-2}" y="{cy-2}" width="4" height="4" fill="{HI}"/>'
    b += hline(32, 248, 836)
    b += f'<text x="32" y="268" font-size="11" letter-spacing="2" fill="{DIM}">NAFROK // AIxROBO</text>'
    b += f'<text x="868" y="268" text-anchor="end" font-size="11" letter-spacing="2" fill="{DIM}">BENGALURU&#160;&#160;12.9716°N 77.5946°E</text>'
    put("header.svg", svg(W, H, b, "Ah Khan (Ra9): full-stack, AI/ML, robotics", canvas=True, grid=True))


# ------------------------------------------------------------------ STATS
def stats():
    H = 124
    b = panel(0, 0, W, H)
    cw = W // len(STATS)
    for i, (n, lines) in enumerate(STATS):
        x = i * cw
        if i:
            b += vline(x, 18, H - 36)
        b += f'<text x="{x+28}" y="68" font-size="44" font-weight="800" fill="url(#steel)">{e(n)}</text>'
        for j, ln in enumerate(lines):
            b += f'<text x="{x+28}" y="{92+j*16}" font-size="12" fill="{MID}">{e(ln)}</text>'
    label = "Career highlights: " + ", ".join(f"{n} {' '.join(l)}" for n, l in STATS)
    put("stats-strip.svg", svg(W, GAP + H, f'<g transform="translate(0,{GAP})">{b}</g>', label))


# ------------------------------------------------------------------ LABS
def aixrobo_visual_b64():
    try:
        from PIL import Image
        im = Image.open(os.path.join(ROOT, "assets", "projects", "aixrobo.png")).convert("RGB")
        im = im.crop((100, 250, 1500, 613)).resize((864, 224), Image.LANCZOS)
        buf = io.BytesIO()
        im.save(buf, "JPEG", quality=80, optimize=True)
        return base64.b64encode(buf.getvalue()).decode()
    except Exception as ex:  # no PIL / no image: panel falls back to a blueprint
        print("  (aixrobo image skipped:", ex, ")")
        return None


def nafrok_visual(px, py, w, h):
    """Blueprint of a site: browser frame, hero skeleton, placeholder image."""
    b = f'<rect x="{px+1}" y="{py}" width="{w-2}" height="{h}" fill="#0d0f11"/>'
    fx, fy, fw, fh = px + 28, py + 12, w - 56, h - 24
    b += f'<rect x="{fx+.5}" y="{fy+.5}" width="{fw-1}" height="{fh-1}" fill="none" stroke="{MID}" stroke-opacity=".45"/>'
    b += hline(fx, fy + 16, fw, MID, .25)
    for i in range(3):
        b += f'<rect x="{fx+10+i*10}" y="{fy+6}" width="5" height="5" fill="{MID}" fill-opacity=".5"/>'
    b += f'<rect x="{fx+20}" y="{fy+30}" width="150" height="8" fill="url(#steel)"/>'
    b += f'<rect x="{fx+20}" y="{fy+46}" width="112" height="5" fill="{MID}" fill-opacity=".45"/>'
    b += f'<rect x="{fx+20}" y="{fy+56}" width="132" height="5" fill="{MID}" fill-opacity=".3"/>'
    b += f'<rect x="{fx+20.5}" y="{fy+68.5}" width="54" height="14" fill="none" stroke="{HI}" stroke-opacity=".7"/>'
    ix, iy, iw, ih = fx + fw - 128, fy + 26, 108, fh - 26 - 12
    b += f'<rect x="{ix+.5}" y="{iy+.5}" width="{iw}" height="{ih}" fill="none" stroke="{MID}" stroke-opacity=".35"/>'
    b += f'<path d="M{ix} {iy}L{ix+iw} {iy+ih}M{ix+iw} {iy}L{ix} {iy+ih}" stroke="{MID}" stroke-opacity=".2"/>'
    return b


def labs():
    pw, ph, gap = 434, 336, 32
    img = aixrobo_visual_b64()
    y0 = GAP + 40 + 16
    b = section_header("[ LABS.RUNNING ]", "2 major next-gen labs", GAP)
    extra = ('<linearGradient id="vfade" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#101214" stop-opacity="0"/>'
             '<stop offset="1" stop-color="#101214" stop-opacity=".92"/></linearGradient>')
    for i, lab in enumerate(LABS):
        px, py = i * (pw + gap), y0
        b += panel(px, py, pw, ph)
        b += f'<text x="{px+24}" y="{py+28}" font-size="11" fill="{DIM}">{e(lab["path"])}</text>'
        b += blink(px + pw - 24 - 60 - 14, py + 20)
        b += f'<text x="{px+pw-24}" y="{py+28}" text-anchor="end" font-size="11" letter-spacing="2" fill="{MID}">RUNNING</text>'
        b += hline(px + 24, py + 44, pw - 48, LINE)
        vx, vy, vw, vh = px, py + 56, pw, 112
        if lab["key"] == "aixrobo" and img:
            b += f'<image x="{vx+1}" y="{vy}" width="{vw-2}" height="{vh}" preserveAspectRatio="none" xlink:href="data:image/jpeg;base64,{img}"/>'
            b += f'<rect x="{vx+1}" y="{vy}" width="{vw-2}" height="{vh}" fill="url(#vfade)"/>'
        else:
            b += nafrok_visual(vx, vy, vw, vh)
        b += hline(px + 1, vy + vh, pw - 2, LINE)
        b += f'<text x="{px+24}" y="{py+210}" font-size="26" font-weight="800" fill="url(#steel)">{e(lab["name"])}</text>'
        b += f'<text x="{px+24}" y="{py+230}" font-size="11" letter-spacing="2" fill="{DIM}">{e(lab["role"])}</text>'
        for j, ln in enumerate(lab["lines"]):
            b += f'<text x="{px+24}" y="{py+256+j*18}" font-size="12" fill="{MID}">{e(ln)}</text>'
        x = px + 24
        for t in lab["tags"]:
            tw = len(t) * 6.6 + 20
            b += f'<rect x="{x+.5}" y="{py+296.5}" width="{tw:.0f}" height="22" fill="none" stroke="{LINE}"/>'
            b += f'<text x="{x+10}" y="{py+311}" font-size="11" fill="{HI}">{e(t)}</text>'
            x += tw + 8
    H = y0 + ph
    put("labs.svg", svg(W, H, b, "Two major next-gen labs running: NAFROK (web) and AIxRobo (research)", extra))


# ------------------------------------------------------------------ PROJECTS
def projects():
    rh, bar = 40, 36
    top = 108
    H = top + len(PROJECTS) * rh + 40
    y0 = GAP + 40 + 16
    b = section_header("[ PROJECTS.RUNNING ]", "ps --state running", GAP)
    p = panel(0, 0, W, H)
    p += f'<rect x="1" y="1" width="{W-2}" height="{bar-1}" fill="#ffffff" fill-opacity=".02"/>'
    for i in range(3):
        p += f'<rect x="{20+i*18}" y="13" width="10" height="10" fill="#3a3f45"/>'
    p += f'<text x="450" y="23" text-anchor="middle" font-size="11" fill="{DIM}">ra9@aixrobo: ~/labs</text>'
    p += hline(1, bar, W - 2, LINE)
    p += f'<text x="28" y="66" font-size="13" fill="{MID}">$ <tspan fill="{HI}">ps --projects --state running</tspan></text>'
    cols = [(28, "PID"), (84, "PROCESS"), (226, "LAB"), (330, "FOCUS"), (560, "STACK"), (808, "STATE")]
    for x, t in cols:
        p += f'<text x="{x}" y="96" font-size="10" letter-spacing="2" fill="{DIM}">{t}</text>'
    p += hline(28, top, W - 56, LINE)
    for i, r in enumerate(PROJECTS):
        ry = top + i * rh
        y = ry + 25
        p += f'<text x="28" y="{y}" font-size="12" fill="{DIM}">{r["pid"]}</text>'
        p += f'<text x="84" y="{y}" font-size="14" font-weight="700" fill="{HI}">{e(r["proc"])}</text>'
        p += f'<text x="226" y="{y}" font-size="12" fill="{MID}">{e(r["lab"])}</text>'
        p += f'<text x="330" y="{y}" font-size="12" fill="{MID}">{e(r["focus"])}</text>'
        p += f'<text x="560" y="{y}" font-size="12" fill="{MID}">{e(r["stack"])}</text>'
        p += state_mark(808, y - 9, r["state"])
        p += f'<text x="826" y="{y}" font-size="11" letter-spacing="2" fill="{HI}">{e(r["state"])}</text>'
        if i < len(PROJECTS) - 1:
            p += hline(28, ry + rh - 1, W - 56, LINE, .5)
    live = sum(1 for r in PROJECTS if r["state"] == "LIVE")
    fy = H - 16
    p += (f'<text x="28" y="{fy}" font-size="11" fill="{DIM}">{len(PROJECTS)} running&#160;&#160;//&#160;&#160;{live} live&#160;&#160;//&#160;&#160;'
          f'{len(PROJECTS)-live} in the lab&#160;&#160;//&#160;&#160;0 crashed</text>')
    p += f'<text x="872" y="{fy}" text-anchor="end" font-size="11" fill="{DIM}">LIVE = in production&#160;&#160; R&amp;D = in the lab</text>'
    b += f'<g transform="translate(0,{y0})">{p}</g>'
    put("projects.svg", svg(W, y0 + H, b, "Projects running: " + ", ".join(r["proc"] for r in PROJECTS)))


# ------------------------------------------------------------------ STACK
def stack():
    tw_, th_, tg = 134, 72, 8
    lane = 84
    pad = 20
    H = pad * 2 + len(STACK) * lane - 12
    y0 = GAP + 40 + 16
    hexes = set()
    for _, items in STACK:
        for t in items:
            hexes.add(brand(t))
    extra = ('<linearGradient id="tile" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#16191c"/>'
             '<stop offset="1" stop-color="#0d0f11"/></linearGradient>')
    for h in sorted(hexes):
        extra += (f'<radialGradient id="g{h}" cx=".5" cy=".5" r=".5"><stop offset="0" stop-color="#{h}" stop-opacity=".5"/>'
                  f'<stop offset="1" stop-color="#{h}" stop-opacity="0"/></radialGradient>'
                  f'<linearGradient id="t{h}" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#{h}" stop-opacity="0"/>'
                  f'<stop offset=".5" stop-color="#{h}"/><stop offset="1" stop-color="#{h}" stop-opacity="0"/></linearGradient>')
    b = section_header("[ STACK.LOAD ]", "24 modules loaded", GAP)
    p = panel(0, 0, W, H)
    n = 0
    for i, (label, items) in enumerate(STACK):
        ly = pad + i * lane
        p += f'<text x="24" y="{ly+40}" font-size="10" letter-spacing="1.5" fill="{DIM}">{e(label)}</text>'
        for j, name in enumerate(items):
            tx, ty = 174 + j * (tw_ + tg), ly
            h = brand(name)
            ic = ICONS[name]["path"]
            delay = (n * 0.37) % 5
            n += 1
            p += f'<rect x="{tx+.5}" y="{ty+.5}" width="{tw_-1}" height="{th_-1}" fill="url(#tile)" stroke="{LINE}"/>'
            p += (f'<ellipse cx="{tx+tw_/2}" cy="{ty+26}" rx="54" ry="30" fill="url(#g{h})">'
                  f'<animate attributeName="opacity" values=".55;1;.55" dur="5s" begin="{delay:.2f}s" repeatCount="indefinite"/></ellipse>')
            p += f'<ellipse cx="{tx+tw_/2}" cy="{ty+th_}" rx="60" ry="9" fill="url(#g{h})" opacity=".7"/>'
            p += f'<rect x="{tx+1}" y="{ty}" width="{tw_-2}" height="2" fill="url(#t{h})"/>'
            tf = f'translate({tx+tw_/2-14},{ty+10}) scale(1.1667)'
            p += f'<path d="{ic}" transform="{tf}" fill="#{h}" opacity=".6" filter="url(#blur4)"/>'
            p += f'<path d="{ic}" transform="{tf}" fill="#{h}"/>'
            p += f'<text x="{tx+tw_/2}" y="{ty+60}" text-anchor="middle" font-size="12" font-weight="600" fill="{HI}">{e(name)}</text>'
        if i < len(STACK) - 1:
            p += hline(24, ly + lane - 6, W - 48, LINE, .5)
    b += f'<g transform="translate(0,{y0})">{p}</g>'
    alt = "Tech stack. " + " ".join(f"{l}: {', '.join(it)}." for l, it in STACK)
    put("stack.svg", svg(W, y0 + H, b, alt, extra))


def brand(name):
    h = ICONS[name]["hex"].lower()
    return "e4e7ea" if h in NEAR_BLACK else h


# ------------------------------------------------------------------ CONNECT
def connect():
    b = section_header("[ OPEN.CHANNEL ]", "bengaluru, in", GAP)
    put("dividers/connect.svg", svg(W, GAP + 40, b, "Open channel"))


if __name__ == "__main__":
    header(); stats(); labs(); projects(); stack(); connect()
    print("static assets written")
