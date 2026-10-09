#!/usr/bin/env python3
"""Validate the optional Ash Marble reference with Python's standard library.

Usage: python3 scripts/validate_ash_marble.py [repo] [--baseline-ref REF]
The baseline defaults to the original v1.0.0 commit; git is used only locally.
This is not a full accessibility or production-component certification.
"""
from __future__ import annotations

import argparse
from html.parser import HTMLParser
import json
import math
from pathlib import Path
import re
import subprocess
from urllib.parse import unquote, urlsplit
from xml.etree import ElementTree as ET

BASELINE = "8fd7d2de97d508cc030be289ea33d92cc7835645"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def luminance(color: str) -> float:
    components = [int(color[i:i + 2], 16) / 255 for i in (1, 3, 5)]
    linear = [x / 12.92 if x <= .04045 else ((x + .055) / 1.055) ** 2.4 for x in components]
    return sum(x * weight for x, weight in zip(linear, [.2126, .7152, .0722]))


def contrast(first: str, second: str) -> float:
    high, low = sorted([luminance(first), luminance(second)], reverse=True)
    return (high + .05) / (low + .05)


def blend(foreground: str, background: str, alpha: float) -> str:
    # Conservative integer rounding: floor reduces the light background luminance.
    return "#" + "".join(f"{math.floor(int(foreground[i:i + 2], 16) * alpha + int(background[i:i + 2], 16) * (1 - alpha)):02x}" for i in (1, 3, 5))


def css_values(css: str, selector: str) -> dict[str, str]:
    block = re.search(re.escape(selector) + r"\s*\{([^{}]*)\}", css)
    require(block is not None, f"Missing CSS selector: {selector}")
    return dict(re.findall(r"--([\w-]+)\s*:\s*([^;]+);", block.group(1)))


def normalize(value: str) -> str:
    return re.sub(r"(?<![\w.])0(?=\.\d)", "", re.sub(r"\s+", "", value).lower())


class Markup(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.ids: list[str] = []
        self.refs: list[str] = []
        self.label_refs: list[str] = []
        self.buttons: list[dict[str, str]] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = dict(attrs)
        if values.get("id"):
            self.ids.append(values["id"])
        for attr in ["href", "src"]:
            if values.get(attr):
                self.refs.append(values[attr])
        for attr in ["aria-labelledby", "aria-describedby"]:
            if values.get(attr):
                self.label_refs.extend(values[attr].split())
        if tag == "button":
            self.buttons.append(values)

    def handle_startendtag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self.handle_starttag(tag, attrs)


def local_reference(repo: Path, source: Path, reference: str) -> Path | None:
    url = urlsplit(reference)
    if url.scheme or url.netloc:
        return None
    target = (source.parent / unquote(url.path)).resolve() if url.path else source.resolve()
    require(target.is_relative_to(repo), f"Reference escapes repository: {source}: {reference}")
    require(target.is_file(), f"Missing reference: {source.relative_to(repo)} -> {reference}")
    return target


def markdown_slug(heading: str) -> str:
    heading = re.sub(r"[^\w -]", "", heading.strip().lower())
    return heading.replace(" ", "-")


def validate(repo: Path, baseline_ref: str) -> None:
    base_path = repo / "tokens/design-tokens.json"
    basic = json.loads(base_path.read_text(encoding="utf-8"))
    ash = json.loads((repo / "tokens/ash-marble.json").read_text(encoding="utf-8"))
    require(basic["version"] == ash["version"] == "1.1.0", "Version mismatch")
    result = subprocess.run(["git", "-C", str(repo), "show", baseline_ref + ":tokens/design-tokens.json"], capture_output=True, text=True)
    require(result.returncode == 0, "Original baseline commit unavailable; use a full clone or --baseline-ref with the original v1.0.0 ref")
    original = json.loads(result.stdout)
    comparison = dict(basic)
    comparison["version"] = original["version"]
    require(comparison == original, "Baseline tokens changed beyond the version field")
    require(set(ash["tones"]) == {"pale", "gray"}, "Invalid tone set")
    require(ash["defaultTone"] == "pale", "Default tone mismatch")
    require(ash["material"]["default"] == "marble", "Default material mismatch")
    require(ash["themeCompatibility"]["existingCycle"] == basic["theme"]["cycle"], "Theme cycle drift")
    require(ash["themeCompatibility"]["applyTonesWhenResolvedMode"] == "light", "Ash must be light-only")
    print("PASS: complete v1.0.0 baseline unchanged except version; mode/tone/material contracts")

    css = (repo / "examples/ash-marble.css").read_text(encoding="utf-8")
    host = (repo / "examples/ash-marble-demo.css").read_text(encoding="utf-8")
    selector = ':root[data-palette="ash-marble"][data-resolved-theme="light"]'
    pale = css_values(css, selector)
    gray = pale | css_values(css, selector + '[data-ash-tone="gray"]')
    for tone, values in [("pale", pale), ("gray", gray)]:
        for name, color in ash["tones"][tone].items():
            require(normalize(values[name]) == normalize(color), f"CSS/token mismatch: {tone}.{name}")
        for name in ["s1", "s2", "s3", "s4", "s5", "other"]:
            require(normalize(values[name]) == normalize(ash["dataColors"][name]), f"Data token mismatch: {name}")
            require(values["data-" + name] == "var(--" + name + ")", f"Data alias mismatch: {name}")
        require(normalize(values["accent-hero"]) == normalize(ash["accents"]["heroMetric"]), "Hero accent mismatch")
        require(normalize(values["accent-secondary"]) == normalize(ash["accents"]["secondaryMetric"]), "Secondary accent mismatch")
        for period in ["prior", "current"]:
            require(normalize(values["data-" + period + "-period"]) == normalize(ash["dataColors"][period + "Period"]), f"Period color mismatch: {period}")
    for mode, values in [("light", css_values(host, ":root")), ("dark", css_values(host, ':root[data-resolved-theme="dark"]'))]:
        for name in ["page", "surface-1", "surface-2", "ink-1", "ink-2", "ink-3", "grid", "axis", "hairline", "wash", "focus", "s1", "s2", "s3", "s4", "s5", "other"]:
            require(normalize(values[name]) == normalize(basic["colors"][mode][name]), f"Demo base token mismatch: {mode}.{name}")
    print("PASS: every overlay color/alias and demo light/dark base CSS agrees with JSON")

    material = ash["material"]["marble"]
    opacity = material["opacity"]
    require(0 < opacity <= .12, "Texture opacity exceeds the reviewed cap")
    texture_block = re.search(re.escape(selector + " .ash-marble-card::before") + r"\s*\{([^{}]*)\}", css).group(1)
    require(float(re.search(r"opacity:\s*([\d.]+)", texture_block).group(1)) == opacity, "CSS/material opacity mismatch")
    require("pointer-events: none" in texture_block and "border-radius: inherit" in texture_block and "z-index: -1" in texture_block, "Texture layer/pointer geometry missing")
    require(".ash-marble-card > *" not in css, "Recipe must not override all host child positions")
    require("overflow: hidden" not in css, "Recipe must not clip card focus/overlays")
    svg_path = local_reference(repo, repo / "tokens/ash-marble.json", material["asset"])
    texture = ET.parse(svg_path).getroot()
    require(not list(texture.iter("{http://www.w3.org/2000/svg}script")), "Unexpected script in decorative SVG")
    ns = "{http://www.w3.org/2000/svg}"
    require([child.tag for child in texture] == [ns + "defs", ns + "g"], "New SVG drawing structure requires a revised alpha bound")
    require(all(not any(key == "style" or key.lower().startswith("on") or key.endswith("href") for key in node.attrib) for node in texture.iter()), "Unexpected SVG style/event/external reference")
    paths = list(texture.iter(ns + "path"))
    require(len(paths) == 7 and all("opacity" in path.attrib for path in paths), "New SVG paths require a revised alpha bound")
    max_alpha = 1 - math.prod(1 - float(path.attrib.get("opacity", "1")) for path in paths)
    require(all("stroke" not in path.attrib for path in paths), "New stroke colors need a revised contrast bound")
    group = texture.find("{http://www.w3.org/2000/svg}g")
    require(group is not None and group.attrib.get("stroke") == "#71808A", "Unexpected vein stroke")
    require(all(node.tag == ns + "path" for node in group) and "opacity" not in group.attrib, "Unexpected SVG compositing")
    filters = list(texture.iter(ns + "filter"))
    require(len(filters) == 1 and [node.tag for node in filters[0]] == [ns + "feTurbulence", ns + "feDisplacementMap"], "New SVG filter requires a revised alpha bound")
    require(filters[0][1].attrib.get("in") == "SourceGraphic", "Unexpected SVG filter input")
    for tone, colors in ash["tones"].items():
        ratios = []
        for ink in ["ink-1", "ink-2", "ink-3"]:
            for background in ["page", "surface-1"]:
                ratio = contrast(colors[ink], colors[background])
                require(ratio >= 4.5, f"Text contrast failed: {tone}.{ink} on {background}: {ratio:.3f}")
        for ink in ["ink-1", "ink-2"]:
            require(contrast(colors[ink], colors["surface-2"]) >= 4.5, f"Control text contrast failed: {tone}.{ink}")
        # All SVG paths overlapping is an intentionally conservative source-over bound.
        darkest = blend(group.attrib["stroke"], colors["surface-1"], max_alpha * opacity)
        for ink in ["ink-1", "ink-2", "ink-3"]:
            ratio = contrast(colors[ink], darkest)
            ratios.append(ratio)
            require(ratio >= 4.5, f"Text contrast failed after texture: {tone}.{ink}: {ratio:.3f}")
        require(contrast(ash["accents"]["heroMetric"], colors["page"]) >= 4.5, f"Hero contrast failed: {tone}")
        print(f"PASS: {tone} text/control/hero colors; conservative textured ink minimum {min(ratios):.3f}:1")

    links = 0
    for source in [repo / "README.md", *sorted((repo / "docs").rglob("*.md"))]:
        content = source.read_text(encoding="utf-8")
        lines = []
        fence = None
        for line in content.splitlines():
            match = re.match(r"\s*(`{3,}|~{3,})", line)
            if match:
                marker = match.group(1)
                if fence is None:
                    fence = marker
                elif marker[0] == fence[0] and len(marker) >= len(fence):
                    fence = None
            elif fence is None:
                lines.append(line)
        require(fence is None, f"Unclosed Markdown fence: {source}")
        for reference in re.findall(r"\[[^\]]*\]\(([^\s)]+)\)", "\n".join(lines)):
            target = local_reference(repo, source, reference)
            if target and urlsplit(reference).fragment and target.suffix == ".md":
                slugs = [markdown_slug(h) for h in re.findall(r"^#{1,6}\s+(.+)$", target.read_text(encoding="utf-8"), re.M)]
                require(unquote(urlsplit(reference).fragment) in slugs, f"Missing Markdown anchor: {reference}")
            links += 1
    html_path = repo / "examples/ash-marble-demo.html"
    html = html_path.read_text(encoding="utf-8")
    markup = Markup()
    markup.feed(html)
    require(len(set(markup.ids)) == len(markup.ids), "Duplicate HTML IDs")
    require(set(markup.label_refs) <= set(markup.ids), "Broken ARIA ID references")
    require(all(button.get("type") == "button" for button in markup.buttons), "Button missing explicit type")
    for reference in markup.refs:
        require(local_reference(repo, html_path, reference) is not None, "Demo must not require remote assets")
    for source in (repo / "examples").glob("*.css"):
        for reference in re.findall(r"url\([\"']?([^\"')]+)", source.read_text(encoding="utf-8")):
            require(local_reference(repo, source, reference) is not None, "Demo CSS must not require remote assets")
    js = (repo / "examples/ash-marble-demo.js").read_text(encoding="utf-8")
    require(not any(pattern in js for pattern in [".innerHTML", "insertAdjacentHTML", "eval(", "fetch(", "XMLHttpRequest"]), "Unexpected unsafe DOM/network API in demo")
    require("演示数据" in html and "fallback" in html and "scope=\"col\"" in html, "Demo evidence/data/table boundary missing")
    paradigm = (repo / "docs/DESIGN_PARADIGM.md").read_text(encoding="utf-8")
    require(re.findall(r"^## (\d+)\.", paradigm, re.M) == [str(i) for i in range(1, 16)], "Baseline 15-section coverage changed")
    print(f"PASS: {links} Markdown links/anchors, fences, HTML/ARIA IDs, local assets, safe demo DOM and all 15 baseline sections")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("repo", nargs="?", default=".", type=Path)
    parser.add_argument("--baseline-ref", default=BASELINE)
    args = parser.parse_args()
    validate(args.repo.resolve(), args.baseline_ref)


if __name__ == "__main__":
    main()
