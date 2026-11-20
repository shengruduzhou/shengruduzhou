"""Validate locally rendered profile metrics and update only their managed region."""
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

START = "<!-- METRICS:DETAILS:START -->"
END = "<!-- METRICS:DETAILS:END -->"
ACTIVITY_START = "<!-- METRICS:ACTIVITY:START -->"
ACTIVITY_END = "<!-- METRICS:ACTIVITY:END -->"
DEST = Path("assets/metrics")
README = Path("README.md")
FILES = ("isocalendar.svg", "languages.svg", "trophy-dark.svg", "trophy-light.svg",
         "wakatime.svg", "anilist.svg", "music.svg", "steam.svg", "stock.svg")

def tag(element):
    return element.tag.rsplit("}", 1)[-1]

def normalized(element):
    return " ".join(" ".join(element.itertext()).split()).lower()

def validate(name, data):
    if not 1000 <= len(data) <= 5_000_000:
        raise ValueError("unexpected SVG size")
    root = ET.fromstring(data)
    if tag(root) != "svg":
        raise ValueError("not SVG")
    for el in root.iter():
        if tag(el).lower() == "script" or any(
            key.rsplit("}", 1)[-1].lower().startswith("on") for key in el.attrib
        ):
            raise ValueError("executable content")
        if "error" in el.get("class", "").split() and tag(el) in {"div", "section", "span"}:
            raise ValueError("plugin error block")
    headings = {normalized(el) for el in root.iter() if tag(el) in {"h1", "h2", "h3"}}
    body = " ".join(normalized(el) for el in root.iter() if tag(el) in {"h1","h2","h3","div","span","small","text"})
    if re.search(r"rate limit exceeded|bad credentials|plugin error|unexpected error|not enough scopes|user not found|service unavailable|unable to fetch|error occurred", body):
        raise ValueError("API error")
    if name == "isocalendar.svg":
        if not {"contributions calendar", "commits per day"} <= headings:
            raise ValueError("calendar sections missing")
    elif name == "languages.svg":
        if "most used languages" not in headings:
            raise ValueError("language sections missing")
        if not re.search(r"estimation from .*? edited files? across [1-9][\d,]* commits?", body):
            # Some upstream versions abbreviate the commit count (e.g. 1.2k).
            if not re.search(r"estimation from .*? edited files? across [1-9][\d.,]*[km]? commits?", body):
                raise ValueError("no non-empty authored-commit analysis")
    elif name == "wakatime.svg":
        if not any(h.startswith("wakatime") for h in headings) or "language activity" not in headings:
            raise ValueError("WakaTime sections missing")
    elif name in {"music.svg", "steam.svg"}:
        if not headings or not any(tag(el) in {"img", "svg", "path"} for el in root.iter() if el is not root):
            raise ValueError("plugin content missing")
    elif name == "anilist.svg":
        if "anilist" not in headings or "favorites genres:" not in body:
            raise ValueError("AniList profile data missing")
    elif name == "stock.svg":
        if not any(h.startswith("stock prices for ") for h in headings) or "valued at" not in body or not any(
            "stock-chart" in el.get("class", "").split() and any(tag(child) == "svg" for child in el.iter())
            for el in root.iter()
        ):
            raise ValueError("stock price/chart missing")
    else:
        if sum(tag(el) == "text" for el in root.iter()) < 3:
            raise ValueError("trophy panels missing")
    return data

def main():
    source = Path(sys.argv[1])
    readme = README.read_text(encoding="utf-8")
    if readme.count(START) != 1 or readme.count(END) != 1:
        raise ValueError("managed README markers missing or duplicated")
    if readme.count(ACTIVITY_START) != 1 or readme.count(ACTIVITY_END) != 1:
        raise ValueError("managed activity markers missing or duplicated")
    start = readme.index(START) + len(START)
    end = readme.index(END, start)
    DEST.mkdir(parents=True, exist_ok=True)
    accepted = 0
    for name in FILES:
        p = source / name
        if not p.is_file():
            print(f"::warning::{name} not produced; preserving last successful copy")
            continue
        try:
            data = validate(name, p.read_bytes())
        except (ValueError, ET.ParseError) as error:
            print(f"::warning::{name} rejected: {error}")
            continue
        (DEST / name).write_bytes(data)
        print(f"Accepted {name}: {len(data):,} bytes")
        accepted += 1

    def exists(name):
        return (DEST / name).is_file()

    parts = []
    if exists("isocalendar.svg"):
        parts.append('### Isometric Calendar\n\n<img src="./assets/metrics/isocalendar.svg" width="100%" alt="Full-year isometric GitHub contribution calendar" />')
    if exists("languages.svg"):
        parts.append('### Language Analytics\n\n<img src="./assets/metrics/languages.svg" width="100%" alt="In-depth language analysis: authored code changes" />\n\n<sub>Public repositories · Programming languages · Git commit patch analysis · Analyzed commit history (time-limited)</sub>')
    activity = []
    if exists("wakatime.svg"):
        activity.append('### WakaTime\n\n<img src="./assets/metrics/wakatime.svg" width="100%" alt="WakaTime coding activity over the last seven days" />\n\n<sub>Last 7 days · Languages, editors and operating systems · No project names displayed.</sub>')
    if exists("anilist.svg"):
        activity.append('### AniList\n\n<img src="./assets/metrics/anilist.svg" width="100%" alt="AniList anime and manga favorites and current activity" />')
    if exists("music.svg"):
        activity.append('### Music\n\n<img src="./assets/metrics/music.svg" width="100%" alt="Recently played music on Spotify" />')
    if exists("steam.svg"):
        activity.append('### Steam\n\n<img src="./assets/metrics/steam.svg" width="100%" alt="Steam profile and gaming activity" />')
    if exists("stock.svg"):
        activity.append('### Market Watch\n\n<img src="./assets/metrics/stock.svg" width="100%" alt="Public stock price chart" />\n\n<sub>Market watch · 3 months · Daily observations · Not portfolio holdings or returns.</sub>')
    dark, light = exists("trophy-dark.svg"), exists("trophy-light.svg")
    if dark and light:
        parts.append('### GitHub Profile Trophies\n\n<picture>\n  <source media="(prefers-color-scheme: dark)" srcset="./assets/metrics/trophy-dark.svg">\n  <source media="(prefers-color-scheme: light)" srcset="./assets/metrics/trophy-light.svg">\n  <img src="./assets/metrics/trophy-light.svg" width="100%" alt="GitHub profile trophies generated locally" />\n</picture>')
    elif dark or light:
        name = "trophy-dark.svg" if dark else "trophy-light.svg"
        parts.append(f'### GitHub Profile Trophies\n\n<img src="./assets/metrics/{name}" width="100%" alt="GitHub profile trophies generated locally" />')
    if not parts or not accepted:
        raise SystemExit("No new valid detail module; existing README and assets preserved")
    out = readme[:start] + "\n" + "\n\n".join(parts) + "\n" + readme[end:]
    activity_start = out.index(ACTIVITY_START) + len(ACTIVITY_START)
    activity_end = out.index(ACTIVITY_END, activity_start)
    out = out[:activity_start] + "\n" + "\n\n".join(activity) + "\n" + out[activity_end:]
    if exists("isocalendar.svg") and exists("languages.svg"):
        out = out.replace("<details open>\n<summary>Account overview", "<details>\n<summary>Account overview", 1)
    README.write_text(out, encoding="utf-8")

if __name__ == "__main__":
    main()
