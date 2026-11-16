#!/usr/bin/env python3
"""Builds assets/snake/contribution-snake.svg and assets/activity.svg.

Data sources (stdlib only, no third-party services, no secrets required):
  * contribution calendar  -> github.com/users/<user>/contributions  (public)
  * repos / languages      -> REST API. Uses GITHUB_TOKEN when set (CI), else falls back
                              to scraping the repositories page (language by repo count).

    PROFILE_USER=ahkhan-nafrok python scripts/build_activity.py
"""
import datetime as dt
import json
import os
import re
import sys
import urllib.request

from svgkit import DIM, GAP, HI, LINE, MID, W, e, hline, panel, put, section_header, svg, vline

USER = os.environ.get("PROFILE_USER", "ahkhan-nafrok")
TOKEN = os.environ.get("GITHUB_TOKEN", "")
UA = {"User-Agent": "Mozilla/5.0 (profile-readme-bot)"}


# ------------------------------------------------------------------ DATA
def http(url, headers=None, timeout=30):
    req = urllib.request.Request(url, headers={**UA, **(headers or {})})
    return urllib.request.urlopen(req, timeout=timeout).read().decode("utf-8", "replace")


def fetch_calendar(user):
    page = http(f"https://github.com/users/{user}/contributions")
    tips = {m.group(1): m.group(2) for m in re.finditer(
        r'<tool-tip[^>]*\bfor="(contribution-day-component-\d+-\d+)"[^>]*>\s*(No|[\d,]+)\s+contributions?', page)}
    days = []
    for m in re.finditer(r'<td\b([^>]*\bdata-date="[^"]+"[^>]*)>', page):
        a = dict(re.findall(r'([\w-]+)="([^"]*)"', m.group(1)))
        mm = re.match(r"contribution-day-component-(\d+)-(\d+)", a.get("id", ""))
        if not mm:
            continue
        txt = tips.get(a["id"], "No")
        days.append(dict(date=a["data-date"], level=int(a.get("data-level", "0")),
                         count=0 if txt == "No" else int(txt.replace(",", "")),
                         row=int(mm.group(1)), col=int(mm.group(2))))
    if len(days) < 300:
        raise RuntimeError(f"calendar parse looks wrong ({len(days)} days)")
    days.sort(key=lambda d: d["date"])
    return days


def streaks(days):
    cur = best = run = 0
    for d in days:
        run = run + 1 if d["count"] > 0 else 0
        best = max(best, run)
    seq = days[:-1] if days[-1]["count"] == 0 else days  # today may not be over yet
    for d in reversed(seq):
        if d["count"] > 0:
            cur += 1
        else:
            break
    return cur, best


def api(path):
    h = {"Accept": "application/vnd.github+json"}
    if TOKEN:
        h["Authorization"] = f"Bearer {TOKEN}"
    url = path if path.startswith("http") else f"https://api.github.com{path}"
    return json.loads(http(url, h, 20))


def fetch_repo_data(user):
    """-> (public_repos | None, [(language, weight)], basis)"""
    pub, langs, basis = None, {}, "by bytes"
    try:
        pub = api(f"/users/{user}").get("public_repos")
        for r in api(f"/users/{user}/repos?per_page=100&type=owner&sort=pushed")[:60]:
            if r.get("fork"):
                continue
            for k, v in api(r["languages_url"]).items():
                langs[k] = langs.get(k, 0) + v
    except Exception as ex:
        print("  api unavailable:", ex)
        langs = {}
    if not langs:
        try:
            page = http(f"https://github.com/{user}?tab=repositories&type=source")
            for name in re.findall(r'itemprop="programmingLanguage">\s*([^<]+?)\s*<', page):
                langs[name] = langs.get(name, 0) + 1
            basis = "by repo count"
        except Exception as ex:
            print("  scrape unavailable:", ex)
    return pub, sorted(langs.items(), key=lambda kv: -kv[1]), basis


# ------------------------------------------------------------------ SNAKE
PITCH, CELL = 15, 12
GX, GY = 60, 52
LEVELS = ["#1a1d21", "#2f353b", "#535b63", "#8f979f", "#e4e7ea"]
PAD, LEN, DT = 20, 10, 0.04  # off-grid run-up (cells), body length, seconds per cell


def lerp(c1, c2, t):
    a = [int(c1[i:i + 2], 16) for i in (1, 3, 5)]
    b = [int(c2[i:i + 2], 16) for i in (1, 3, 5)]
    return "#" + "".join(f"{round(x + (y - x) * t):02x}" for x, y in zip(a, b))


def compress(pts):
    out = [pts[0]]
    for i in range(1, len(pts) - 1):
        a, b, c = pts[i - 1], pts[i], pts[i + 1]
        if (round(b[0] - a[0], 3), round(b[1] - a[1], 3)) != (round(c[0] - b[0], 3), round(c[1] - b[1], 3)):
            out.append(b)
    out.append(pts[-1])
    return out


def build_snake(days):
    ncols = max(d["col"] for d in days) + 1
    cells = {(d["col"], d["row"]): d for d in days}
    seq = []
    for c in range(ncols):
        seq += [(c, r) for r in (range(7) if c % 2 == 0 else range(6, -1, -1))]
    index = {pos: i for i, pos in enumerate(seq)}
    T = (len(seq) + 2 * PAD) * DT

    def ctr(c, r):
        return (GX + c * PITCH + CELL / 2, GY + r * PITCH + CELL / 2)

    pts = [ctr(-k, seq[0][1]) for k in range(PAD, 0, -1)] + [ctr(c, r) for c, r in seq]
    pts += [ctr(seq[-1][0] + k, seq[-1][1]) for k in range(1, PAD + 1)]
    route = "M" + " L".join(f"{x:.1f} {y:.1f}" for x, y in compress(pts))

    H = GY + 7 * PITCH - 3 + 18
    p = panel(0, 0, W, H)
    p += f'<text x="24" y="26" font-size="11" letter-spacing="1.5" fill="{DIM}">CONTRIBUTION.GRID&#160;&#160;//&#160;&#160;LAST 365 DAYS</text>'
    lx = 876 - 26 - 8 - 5 * PITCH
    p += f'<text x="{lx-8}" y="26" text-anchor="end" font-size="10" fill="{DIM}">less</text>'
    for i, col in enumerate(LEVELS):
        p += f'<rect x="{lx+i*PITCH}" y="17" width="{CELL}" height="{CELL}" fill="{col}"/>'
    p += f'<text x="876" y="26" text-anchor="end" font-size="10" fill="{DIM}">more</text>'
    last_m = None
    for c in range(ncols):
        top = next((d for d in days if d["col"] == c), None)
        if top and top["date"][5:7] != last_m:
            last_m = top["date"][5:7]
            name = dt.date.fromisoformat(top["date"]).strftime("%b")
            p += f'<text x="{GX+c*PITCH}" y="{GY-8}" font-size="10" fill="{DIM}">{name}</text>'
    for r, name in ((1, "Mon"), (3, "Wed"), (5, "Fri")):
        p += f'<text x="24" y="{GY+r*PITCH+10}" font-size="10" fill="{DIM}">{name}</text>'
    for (c, r), d in cells.items():
        x, y = GX + c * PITCH, GY + r * PITCH
        anim = ""
        if d["level"] > 0:
            f = (PAD + index[(c, r)]) * DT / T
            anim = (f'<animate attributeName="fill" dur="{T:.2f}s" repeatCount="indefinite" calcMode="discrete" '
                    f'keyTimes="0;{f:.5f};1" values="{LEVELS[d["level"]]};{LEVELS[0]};{LEVELS[0]}"/>')
        p += f'<rect x="{x}" y="{y}" width="{CELL}" height="{CELL}" rx="2" fill="{LEVELS[d["level"]]}">{anim}</rect>'

    def mover(k):  # k steps behind the head
        return (f'<animateMotion dur="{T:.2f}s" repeatCount="indefinite" begin="-{T - k * DT:.3f}s">'
                f'<mpath xlink:href="#route"/></animateMotion>')

    body = ""
    for k in range(LEN - 1, -1, -1):
        size = 13 - k * 0.5
        col = "#f4f6f7" if k == 0 else lerp("#c3c8cd", "#3a3f45", (k - 1) / (LEN - 2))
        if k == 0:
            body += (f'<rect x="-11" y="-11" width="22" height="22" fill="{HI}" opacity=".35" filter="url(#blur8)">'
                     f'{mover(0)}</rect>')
        body += (f'<rect x="{-size/2:.1f}" y="{-size/2:.1f}" width="{size:.1f}" height="{size:.1f}" rx="2" '
                 f'fill="{col}" opacity="{1 - k * 0.05:.2f}">{mover(k)}</rect>')
    p += body
    total = sum(d["count"] for d in days)
    label = f"Contribution snake eating {total} contributions from the last 365 days"
    defs = f'<path id="route" d="{route}" fill="none"/>'
    out = svg(W, 16 + H, f'<g transform="translate(0,16)">{p}</g>', label, defs)
    put("snake/contribution-snake.svg", out)


# ------------------------------------------------------------------ ACTIVITY
SHADES = ["#f4f6f7", "#c3c8cd", "#9aa1a8", "#737b83", "#555c63", "#3a3f45"]


def build_activity(days, pub, langs, basis):
    cur, best_streak = streaks(days)
    total = sum(d["count"] for d in days)
    active = sum(1 for d in days if d["count"] > 0)
    best_day = max(d["count"] for d in days)
    metrics = [
        (f"{total:,}", "contributions, 1y"), (str(active), "active days"), (str(cur), "current streak (days)"),
        (str(best_streak), "longest streak (days)"), (str(best_day), "best day"),
        (str(pub) if pub is not None else "-", "public repos"),
    ]
    H = 200
    p = panel(0, 0, W, H)
    for i, (num, lab) in enumerate(metrics):
        x = 28 + (i % 3) * 172
        y = 64 if i < 3 else 148
        p += f'<text x="{x}" y="{y}" font-size="32" font-weight="800" fill="url(#steel)">{e(num)}</text>'
        p += f'<text x="{x}" y="{y+20}" font-size="11" fill="{MID}">{e(lab)}</text>'
    p += hline(28, 100, 492, LINE, .6)
    p += vline(544, 20, H - 40)
    p += f'<text x="572" y="30" font-size="10" letter-spacing="2" fill="{DIM}">LANG.MAP</text>'
    p += f'<text x="872" y="30" text-anchor="end" font-size="10" fill="{DIM}">{basis}</text>'
    if langs:
        top = langs[:5]
        rest = sum(v for _, v in langs[5:])
        rows = top + ([("Other", rest)] if rest else [])
        tot = sum(v for _, v in rows)
        x = 572.0
        for i, (_, v) in enumerate(rows):
            w = 300 * v / tot
            p += f'<rect x="{x:.1f}" y="42" width="{max(w - 1, 1):.1f}" height="8" fill="{SHADES[i]}"/>'
            x += w
        for i, (name, v) in enumerate(rows):
            y = 76 + i * 20
            p += f'<rect x="572" y="{y-8}" width="8" height="8" fill="{SHADES[i]}"/>'
            p += f'<text x="590" y="{y}" font-size="12" fill="{HI}">{e(name)}</text>'
            p += f'<text x="872" y="{y}" text-anchor="end" font-size="11" fill="{MID}">{100*v/tot:.1f}%</text>'
    else:
        p += f'<text x="572" y="84" font-size="12" fill="{MID}">language data syncs on the first workflow run</text>'
    stamp = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%d")
    b = section_header("[ COMMIT.LOG ]", f"synced {stamp} UTC", GAP)
    b += f'<g transform="translate(0,{GAP+40+16})">{p}</g>'
    summary = f"GitHub activity: {total} contributions in the last year, {cur} day current streak, {best_streak} day longest streak"
    put("activity.svg", svg(W, GAP + 40 + 16 + H, b, summary))


if __name__ == "__main__":
    try:
        days = fetch_calendar(USER)
    except Exception as ex:
        print("FAILED to read the contribution calendar:", ex)
        sys.exit(1)  # keep the previous SVGs untouched
    pub, langs, basis = fetch_repo_data(USER)
    build_snake(days)
    build_activity(days, pub, langs, basis)
    print(f"ok: {len(days)} days, {sum(d['count'] for d in days)} contributions, langs={len(langs)} ({basis})")
