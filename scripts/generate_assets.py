#!/usr/bin/env python3
"""
Generates glassmorphic SVG assets for the GitHub profile README:
  - project cards (assets/cards/*.svg)
  - section dividers (assets/dividers/*.svg)

Why SVG instead of live CSS: GitHub strips <style>/backdrop-filter from
rendered README HTML, so real glassmorphism can't happen at page-render
time. Instead we bake the blur + translucency into the SVG itself using
<feGaussianBlur>, which GitHub renders natively when an .svg file is
referenced via an <img> tag. Re-run this script any time project data
or images change; the GitHub Action re-runs it on a schedule too.

Usage:
    python3 scripts/generate_assets.py
"""

import base64
import mimetypes
import os
import textwrap

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CARDS_DIR = os.path.join(ROOT, "assets", "cards")
DIVIDERS_DIR = os.path.join(ROOT, "assets", "dividers")
PROJECTS_DIR = os.path.join(ROOT, "assets", "projects")

os.makedirs(CARDS_DIR, exist_ok=True)
os.makedirs(DIVIDERS_DIR, exist_ok=True)
os.makedirs(PROJECTS_DIR, exist_ok=True)

# ---------------------------------------------------------------------------
# Palette — warm grey / stone, single accent
# ---------------------------------------------------------------------------
STONE_950 = "#0c0a09"
STONE_900 = "#1c1917"
STONE_800 = "#292524"
STONE_700 = "#44403c"
STONE_600 = "#57534e"
STONE_500 = "#78716c"
STONE_400 = "#a8a29e"
STONE_300 = "#d6d3d1"
STONE_100 = "#f5f5f4"
ACCENT = "#e7e5e4"  # warm off-white used sparingly for emphasis

# ---------------------------------------------------------------------------
# Project data — edit this list, then re-run the script
# ---------------------------------------------------------------------------
PROJECTS = [
    {
        "slug": "nafrok",
        "name": "NAFROK",
        "year": "2024",
        "desc": "Web design agency — 30+ production systems shipped. "
                "\u20b915\u201345K fixed pricing, 1\u20133 week delivery, "
                "125% avg. conversion lift.",
        "tags": ["Next.js", "Design Systems", "Client Delivery"],
        "link": "https://nafrok.com",
        "image": None,
    },
    {
        "slug": "slatebooks",
        "name": "SlateBooks",
        "year": "2025",
        "desc": "E-commerce platform built from zero — brand identity, "
                "admin dashboard, payments, inventory. 30 \u2192 1,200 "
                "monthly visitors.",
        "tags": ["MERN", "Payments", "Admin Dashboard"],
        "link": "https://slatebooks.in",
        "image": None,
    },
    {
        "slug": "aixrescue",
        "name": "AIxRescue",
        "year": "2025",
        "desc": "Real-time disaster intelligence — satellite imagery, "
                "live weather telemetry, AI anomaly detection in one "
                "command dashboard.",
        "tags": ["Python", "Anomaly Detection", "Dashboards"],
        "link": "https://aixrescue.io",
        "image": None,
    },
    {
        "slug": "aixdrone",
        "name": "AIxDrone",
        "year": "2025",
        "desc": "Autonomous flight system — LiDAR + GPS + IMU sensor "
                "fusion, onboard PyTorch inference, obstacle avoidance, "
                "swarm coordination.",
        "tags": ["PyTorch", "Sensor Fusion", "Autonomy"],
        "link": "https://aixdrone.io",
        "image": None,
    },
    {
        "slug": "aixrobo",
        "name": "AIxRobo",
        "year": "2025",
        "desc": "Independent research lab — humanoid robotics, LLM + "
                "physical intelligence, multi-modal perception, "
                "autonomous systems.",
        "tags": ["Robotics", "LLM", "Perception"],
        "link": "https://aixrobo.com",
        "image": "aixrobo.png",
    },
    {
        "slug": "retail-joints",
        "name": "Retail Joints",
        "year": "2023",
        "desc": "Call center infrastructure — 20+ machines built and "
                "networked, full VoIP stack, security hardened, "
                "delivered under budget.",
        "tags": ["VoIP", "Networking", "Infra"],
        "link": "https://retailjoints.io",
        "image": None,
    },
]

CARD_W, CARD_H = 380, 390
IMG_H = 190


def _wrap(text, width=38):
    return textwrap.wrap(text, width=width)


def _b64_image(path):
    mime, _ = mimetypes.guess_type(path)
    with open(path, "rb") as f:
        data = base64.b64encode(f.read()).decode("ascii")
    return f"data:{mime};base64,{data}"


def _tag_pills(tags, x, y):
    """Render tag pills left-to-right, wrapping to a new row if needed."""
    out = []
    cx = x
    cy = y
    row_h = 26
    max_x = CARD_W - 24
    for tag in tags:
        w = 14 + len(tag) * 6.4
        if cx + w > max_x:
            cx = x
            cy += row_h
        out.append(f"""
        <rect x="{cx:.1f}" y="{cy:.1f}" width="{w:.1f}" height="22" rx="11"
              fill="{STONE_800}" stroke="{STONE_600}" stroke-width="1" opacity="0.9"/>
        <text x="{cx + w/2:.1f}" y="{cy + 15:.1f}" font-family="'Fira Code',monospace"
              font-size="10.5" fill="{STONE_300}" text-anchor="middle">{tag}</text>
        """)
        cx += w + 8
    return "".join(out), cy + row_h


def make_card_svg(p):
    slug = p["slug"]
    lines = _wrap(p["desc"])
    desc_svg = "".join(
        f'<tspan x="24" dy="{0 if i == 0 else 17}">{line}</tspan>'
        for i, line in enumerate(lines)
    )

    image_path = os.path.join(PROJECTS_DIR, p["image"]) if p["image"] else None
    has_real_image = image_path and os.path.isfile(image_path)

    if has_real_image:
        href = _b64_image(image_path)
        image_block = f"""
        <clipPath id="imgClip-{slug}">
          <path d="M0,0 H{CARD_W} V{IMG_H-16}
                   Q{CARD_W},{IMG_H} {CARD_W-16},{IMG_H}
                   H16 Q0,{IMG_H} 0,{IMG_H-16} Z"/>
        </clipPath>
        <g clip-path="url(#imgClip-{slug})">
          <image href="{href}" x="0" y="0" width="{CARD_W}" height="{IMG_H}"
                 preserveAspectRatio="xMidYMid slice"/>
          <rect x="0" y="0" width="{CARD_W}" height="{IMG_H}"
                fill="url(#imgFade-{slug})"/>
        </g>
        """
    else:
        image_block = f"""
        <clipPath id="imgClip-{slug}">
          <path d="M0,0 H{CARD_W} V{IMG_H-16}
                   Q{CARD_W},{IMG_H} {CARD_W-16},{IMG_H}
                   H16 Q0,{IMG_H} 0,{IMG_H-16} Z"/>
        </clipPath>
        <g clip-path="url(#imgClip-{slug})">
          <rect x="0" y="0" width="{CARD_W}" height="{IMG_H}" fill="url(#placeholderGrad-{slug})"/>
          <rect x="0" y="0" width="{CARD_W}" height="{IMG_H}" fill="url(#hatch)" opacity="0.5"/>
          <g transform="translate({CARD_W/2},{IMG_H/2 - 10})" opacity="0.55">
            <rect x="-18" y="-13" width="36" height="26" rx="4" fill="none"
                  stroke="{STONE_400}" stroke-width="1.6"/>
            <circle cx="0" cy="0" r="6" fill="none" stroke="{STONE_400}" stroke-width="1.6"/>
            <rect x="-6" y="-19" width="12" height="6" rx="1.5" fill="{STONE_400}"/>
          </g>
          <text x="{CARD_W/2}" y="{IMG_H/2 + 24}" font-family="'Fira Code',monospace"
                font-size="10" letter-spacing="2" fill="{STONE_400}" text-anchor="middle"
                opacity="0.7">IMAGE PENDING</text>
        </g>
        """

    tags_svg, tags_bottom = _tag_pills(p["tags"], 24, 40 + len(lines) * 17 + IMG_H + 14)

    return f"""<svg width="{CARD_W}" height="{CARD_H}" viewBox="0 0 {CARD_W} {CARD_H}"
     xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="bgGrad-{slug}" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%" stop-color="{STONE_900}"/>
      <stop offset="100%" stop-color="{STONE_950}"/>
    </linearGradient>
    <linearGradient id="placeholderGrad-{slug}" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%" stop-color="{STONE_800}"/>
      <stop offset="100%" stop-color="{STONE_900}"/>
    </linearGradient>
    <linearGradient id="imgFade-{slug}" x1="0" y1="0" x2="0" y2="1">
      <stop offset="55%" stop-color="{STONE_950}" stop-opacity="0"/>
      <stop offset="100%" stop-color="{STONE_950}" stop-opacity="0.55"/>
    </linearGradient>
    <pattern id="hatch" width="8" height="8" patternTransform="rotate(45)" patternUnits="userSpaceOnUse">
      <line x1="0" y1="0" x2="0" y2="8" stroke="{STONE_700}" stroke-width="1" opacity="0.35"/>
    </pattern>
    <filter id="blurBlob-{slug}" x="-60%" y="-60%" width="220%" height="220%">
      <feGaussianBlur stdDeviation="34"/>
    </filter>
    <clipPath id="cardClip-{slug}">
      <rect x="0.5" y="0.5" width="{CARD_W-1}" height="{CARD_H-1}" rx="18"/>
    </clipPath>
  </defs>

  <g clip-path="url(#cardClip-{slug})">
    <rect x="0" y="0" width="{CARD_W}" height="{CARD_H}" fill="url(#bgGrad-{slug})"/>
    <circle cx="{CARD_W-30}" cy="{IMG_H+40}" r="90" fill="{STONE_500}" opacity="0.18"
            filter="url(#blurBlob-{slug})"/>
    <circle cx="20" cy="{CARD_H-20}" r="70" fill="{STONE_400}" opacity="0.10"
            filter="url(#blurBlob-{slug})"/>

    {image_block}

    <rect x="0" y="{IMG_H}" width="{CARD_W}" height="{CARD_H-IMG_H}" fill="{STONE_900}" opacity="0.55"/>

    <rect x="16" y="{IMG_H-32}" width="{16 + len(p['year'])*8}" height="24" rx="12"
          fill="{STONE_950}" stroke="{STONE_600}" stroke-width="1" opacity="0.92"/>
    <text x="{16 + (16 + len(p['year'])*8)/2}" y="{IMG_H-15.5}" font-family="'Fira Code',monospace"
          font-size="11" fill="{STONE_300}" text-anchor="middle">{p['year']}</text>

    <text x="24" y="{IMG_H+30}" font-family="'Fira Code',monospace" font-weight="600"
          font-size="20" fill="{ACCENT}">{p['name']}</text>

    <text x="24" y="{IMG_H+55}" font-family="'Fira Code',monospace" font-size="12.5"
          fill="{STONE_400}">{desc_svg}</text>

    {tags_svg}
  </g>
  <rect x="0.5" y="0.5" width="{CARD_W-1}" height="{CARD_H-1}" rx="18"
        fill="none" stroke="{STONE_700}" stroke-width="1" opacity="0.8"/>
  <rect x="1.5" y="1.5" width="{CARD_W-3}" height="{CARD_H-3}" rx="17"
        fill="none" stroke="{STONE_100}" stroke-width="1" opacity="0.06"/>
</svg>"""


def make_divider_svg(label, width=880):
    height = 60
    return f"""<svg width="{width}" height="{height}" viewBox="0 0 {width} {height}"
     xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="lineL" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0%" stop-color="{STONE_900}" stop-opacity="0"/>
      <stop offset="100%" stop-color="{STONE_500}" stop-opacity="0.9"/>
    </linearGradient>
    <linearGradient id="lineR" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0%" stop-color="{STONE_500}" stop-opacity="0.9"/>
      <stop offset="100%" stop-color="{STONE_900}" stop-opacity="0"/>
    </linearGradient>
  </defs>
  <line x1="0" y1="{height/2}" x2="{width/2 - len(label)*5.2 - 22}" y2="{height/2}"
        stroke="url(#lineL)" stroke-width="1"/>
  <line x1="{width/2 + len(label)*5.2 + 22}" y1="{height/2}" x2="{width}" y2="{height/2}"
        stroke="url(#lineR)" stroke-width="1"/>
  <rect x="{width/2 - len(label)*5.2 - 30}" y="{height/2 - 3}" width="6" height="6" rx="1.5"
        fill="{STONE_800}" stroke="{STONE_400}" stroke-width="1" transform="rotate(45 {width/2 - len(label)*5.2 - 27} {height/2})"/>
  <rect x="{width/2 + len(label)*5.2 + 24}" y="{height/2 - 3}" width="6" height="6" rx="1.5"
        fill="{STONE_800}" stroke="{STONE_400}" stroke-width="1" transform="rotate(45 {width/2 + len(label)*5.2 + 27} {height/2})"/>
  <text x="{width/2}" y="{height/2 + 4}" font-family="'Fira Code',monospace" font-size="12.5"
        letter-spacing="4" fill="{STONE_300}" text-anchor="middle">{label}</text>
</svg>"""


def make_stats_strip_svg(stats, width=880, height=130):
    n = len(stats)
    col_w = width / n
    parts = [f"""<svg width="{width}" height="{height}" viewBox="0 0 {width} {height}"
     xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="stripBg" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%" stop-color="{STONE_900}"/>
      <stop offset="100%" stop-color="{STONE_950}"/>
    </linearGradient>
    <filter id="stripBlur" x="-60%" y="-60%" width="220%" height="220%">
      <feGaussianBlur stdDeviation="40"/>
    </filter>
    <clipPath id="stripClip">
      <rect x="0.5" y="0.5" width="{width-1}" height="{height-1}" rx="20"/>
    </clipPath>
  </defs>
  <g clip-path="url(#stripClip)">
    <rect x="0" y="0" width="{width}" height="{height}" fill="url(#stripBg)"/>
    <circle cx="{width*0.15}" cy="{height*0.2}" r="80" fill="{STONE_500}" opacity="0.15" filter="url(#stripBlur)"/>
    <circle cx="{width*0.85}" cy="{height*0.9}" r="90" fill="{STONE_400}" opacity="0.12" filter="url(#stripBlur)"/>
    <rect x="0" y="0" width="{width}" height="{height}" fill="{STONE_100}" opacity="0.02"/>
  </g>"""]
    for i, (value, label) in enumerate(stats):
        cx = col_w * i + col_w / 2
        if i > 0:
            parts.append(
                f'<line x1="{col_w*i:.1f}" y1="26" x2="{col_w*i:.1f}" y2="{height-26}" '
                f'stroke="{STONE_700}" stroke-width="1" opacity="0.7"/>'
            )
        parts.append(f"""
        <text x="{cx:.1f}" y="{height/2 - 6}" font-family="'Fira Code',monospace"
              font-weight="700" font-size="30" fill="{ACCENT}" text-anchor="middle">{value}</text>
        <text x="{cx:.1f}" y="{height/2 + 24}" font-family="'Fira Code',monospace"
              font-size="11" letter-spacing="1.5" fill="{STONE_400}" text-anchor="middle">{label}</text>
        """)
    parts.append(f"""
  <rect x="0.5" y="0.5" width="{width-1}" height="{height-1}" rx="20"
        fill="none" stroke="{STONE_700}" stroke-width="1" opacity="0.8"/>
  <rect x="1.5" y="1.5" width="{width-3}" height="{height-3}" rx="19"
        fill="none" stroke="{STONE_100}" stroke-width="1" opacity="0.06"/>
</svg>""")
    return "".join(parts)


def main():
    for p in PROJECTS:
        svg = make_card_svg(p)
        path = os.path.join(CARDS_DIR, f"{p['slug']}.svg")
        with open(path, "w") as f:
            f.write(svg)
        print(f"wrote {path}")

    for label in ["SELECTED WORK", "TECH STACK", "GITHUB ACTIVITY", "CONNECT"]:
        svg = make_divider_svg(label)
        fname = label.lower().replace(" ", "-") + ".svg"
        path = os.path.join(DIVIDERS_DIR, fname)
        with open(path, "w") as f:
            f.write(svg)
        print(f"wrote {path}")

    stats = [
        ("2", "COMPANIES FOUNDED"),
        ("30+", "SYSTEMS SHIPPED"),
        ("3", "YEARS BUILDING"),
    ]
    strip_svg = make_stats_strip_svg(stats)
    strip_path = os.path.join(ROOT, "assets", "stats-strip.svg")
    with open(strip_path, "w") as f:
        f.write(strip_svg)
    print(f"wrote {strip_path}")


if __name__ == "__main__":
    main()
