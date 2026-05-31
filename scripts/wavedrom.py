# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///

from pathlib import Path
from xml.etree import ElementTree as ET
import re
import sys

SVG_NS = "http://www.w3.org/2000/svg"

ET.register_namespace("", SVG_NS)
ET.register_namespace("xlink", "http://www.w3.org/1999/xlink")


def patch_css(css: str) -> str:
    css = re.sub(r"text\s*\{", "text{fill:#ddd;", css, count=1)

    replacements = {
        "#000": "#ddd",
        "#fff": "none",
        "#ffffff": "none",
        "white": "none",
        "#0041c4": "#7ab7ff",
        "#888": "#666",
        "#aaa": "#777",
        "#f00": "#ff6666",
        "#ff0000": "#ff6666",
    }

    for old, new in replacements.items():
        css = re.sub(re.escape(old), new, css, flags=re.IGNORECASE)

    return css


def find_parent(root: ET.Element, child: ET.Element) -> ET.Element | None:
    for parent in root.iter():
        if child in list(parent):
            return parent
    return None


def remove_background(root: ET.Element) -> None:
    for elem in list(root.iter()):
        if elem.tag != f"{{{SVG_NS}}}rect":
            continue

        style_norm = elem.get("style", "").replace(" ", "").lower()
        fill = (elem.get("fill") or "").lower()

        # Only remove large/background/helper white rectangles.
        # Keeps colored waveform value blocks intact.
        if (
            "fill:white" in style_norm
            or "fill:#fff" in style_norm
            or fill in {"white", "#fff", "#ffffff"}
        ):
            parent = find_parent(root, elem)
            if parent is not None:
                parent.remove(elem)


def make_light(input_file: Path, output_file: Path) -> None:
    tree = ET.parse(input_file)
    root = tree.getroot()

    remove_background(root)

    tree.write(output_file, encoding="utf-8", xml_declaration=True)


def make_dark(input_file: Path, output_file: Path) -> None:
    tree = ET.parse(input_file)
    root = tree.getroot()

    remove_background(root)

    style_el = root.find(f".//{{{SVG_NS}}}style")
    if style_el is not None and style_el.text:
        style_el.text = patch_css(style_el.text)

    for elem in root.iter():
        style = elem.get("style")
        if style:
            elem.set("style", patch_css(style))

    tree.write(output_file, encoding="utf-8", xml_declaration=True)


def main() -> None:
    if len(sys.argv) != 2:
        print(f"Usage: {Path(sys.argv[0]).name} input.svg")
        raise SystemExit(1)

    input_file = Path(sys.argv[1])
    stem = input_file.with_suffix("")

    light_file = stem.with_name(f"{stem.name}-light.svg")
    dark_file = stem.with_name(f"{stem.name}-dark.svg")

    make_light(input_file, light_file)
    make_dark(input_file, dark_file)

    print(f"Wrote {light_file}")
    print(f"Wrote {dark_file}")


if __name__ == "__main__":
    main()
