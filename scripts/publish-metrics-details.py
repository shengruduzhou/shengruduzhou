"""Validate locally rendered profile metrics and update only their managed region."""
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

START = "<!-- METRICS:DETAILS:START -->"
END = "<!-- METRICS:DETAILS:END -->"
DEST = Path("assets/metrics")
README = Path("README.md")
FILES = ("isocalendar.svg", "languages.svg", "trophy-dark.svg", "trophy-light.svg")

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
        if not {"most used languages", "recently used languages"} <= headings:
            raise ValueError("language sections missing")
        if not re.search(r"estimation from .*? edited files? across [1-9][\d,]* commits?", body):
            # Some upstream versions abbreviate the commit count (e.g. 1.2k).
            if not re.search(r"estimation from .*? edited files? across [1-9][\d.,]*[km]? commits?", body):
                raise ValueError("no non-empty authored-commit analysis")
    else:
        if sum(tag(el) == "text" for el in root.iter()) < 3:
            raise ValueError("trophy panels missing")
    return data

def main():
    source = Path(sys.argv[1])
    readme = README.read_text(encoding="utf-8")
    if readme.count(START) != 1 or readme.count(END) != 1:
        raise ValueError("managed README markers missing or duplicated")
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
        parts.append('### Language Analytics\n\n<img src="./assets/metrics/languages.svg" width="100%" alt="In-depth language analysis: authored code changes and recent language activity" />\n\n<sub>Public repositories · Programming languages · Git commit patch analysis · Recent activity: 30 days (available events)</sub>')
    dark, light = exists("trophy-dark.svg"), exists("trophy-light.svg")
    if dark and light:
        parts.append('### GitHub Profile Trophies\n\n<picture>\n  <source media="(prefers-color-scheme: dark)" srcset="./assets/metrics/trophy-dark.svg">\n  <source media="(prefers-color-scheme: light)" srcset="./assets/metrics/trophy-light.svg">\n  <img src="./assets/metrics/trophy-light.svg" width="100%" alt="GitHub profile trophies generated locally" />\n</picture>')
    elif dark or light:
        name = "trophy-dark.svg" if dark else "trophy-light.svg"
        parts.append(f'### GitHub Profile Trophies\n\n<img src="./assets/metrics/{name}" width="100%" alt="GitHub profile trophies generated locally" />')
    if not parts or not accepted:
        raise SystemExit("No new valid detail module; existing README and assets preserved")
    out = readme[:start] + "\n" + "\n\n".join(parts) + "\n" + readme[end:]
    if exists("isocalendar.svg") and exists("languages.svg"):
        out = out.replace("<details open>\n<summary>Account overview", "<details>\n<summary>Account overview", 1)
    README.write_text(out, encoding="utf-8")

if __name__ == "__main__":
    main()
