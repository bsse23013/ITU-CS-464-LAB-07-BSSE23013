#!/usr/bin/env python3
"""Lab 07 documentation helper.

Reads what DocCapture (press F9 in Play Mode) saved:
    Docs/screens/NN-name/colour.png
    Docs/screens/NN-name/greyscale.png      (made again from colour.png if missing)
    Docs/screens/NN-name/annotations.json   (pixel boxes of every Annot marker)

and writes next to them:
    annotated.png     colour screenshot with numbered boxes, arrows and callout text
    greyscale.png     (only if it was missing)
    callouts.md       the same callouts as a numbered list

Then it pastes callouts.md into README.md between the markers
    <!--CALLOUTS:01-title-->  ...  <!--/CALLOUTS-->

Usage (from the repo root):   python Docs/tools/make_docs.py
Needs:                         pip install pillow
"""
import json
import os
import sys
import textwrap

from PIL import Image, ImageDraw, ImageFont, ImageOps

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
SHOTS = os.path.join(ROOT, "Docs", "screens")
README = os.path.join(ROOT, "README.md")
FONT = os.path.join(ROOT, "Assets", "Lab07", "Resources", "Lab07", "Fonts", "Poppins-SemiBold.ttf")

MARGIN = 470
COLOURS = [(255, 64, 129), (0, 200, 255), (255, 214, 10), (120, 255, 120), (255, 140, 0), (190, 140, 255)]


def font(size):
    try:
        return ImageFont.truetype(FONT, size)
    except OSError:
        return ImageFont.load_default()


def luminance_grey(img):
    """Same maths as DocCapture: relative luminance, then back to display values."""
    px = img.convert("RGB")
    out = Image.new("L", px.size)
    data = []
    for r, g, b in px.getdata():
        lin = 0.2126 * (r / 255) ** 2.2 + 0.7152 * (g / 255) ** 2.2 + 0.0722 * (b / 255) ** 2.2
        data.append(int(round((lin ** (1 / 2.2)) * 255)))
    out.putdata(data)
    return out.convert("RGB")


def spread(ys, heights, top, bottom, gap=14):
    """Keep callout labels from overlapping: push down, then pull back up if we ran out of room."""
    order = sorted(range(len(ys)), key=lambda i: ys[i])
    pos = {}
    cursor = top
    for i in order:
        y = max(ys[i], cursor)
        pos[i] = y
        cursor = y + heights[i] + gap
    overflow = cursor - gap - bottom
    if overflow > 0:
        cursor = bottom
        for i in reversed(order):
            y = min(pos[i], cursor - heights[i])
            pos[i] = y
            cursor = y - gap
    return pos


def annotate(colour_path, ann_path, out_path):
    shot = Image.open(colour_path).convert("RGB")
    with open(ann_path, encoding="utf-8") as fh:
        sheet = json.load(fh)
    items = sheet.get("items", [])

    w, h = shot.size
    canvas = Image.new("RGB", (w + 2 * MARGIN, h), (24, 26, 48))
    canvas.paste(shot, (MARGIN, 0))
    d = ImageDraw.Draw(canvas)
    f_note = font(30)
    f_num = font(34)

    boxes = []
    for i, it in enumerate(items):
        x, y, bw, bh = it["x"] + MARGIN, it["y"], it["w"], it["h"]
        boxes.append((x, y, x + bw, y + bh))

    wrapped, heights, sides = [], [], []
    for i, it in enumerate(items):
        lines = textwrap.wrap("%d. %s" % (i + 1, it["note"]), width=27)
        wrapped.append(lines)
        heights.append(len(lines) * 38 + 12)
        cx = (boxes[i][0] + boxes[i][2]) / 2
        sides.append("L" if cx < MARGIN + w / 2 else "R")

    label_y = {}
    for side in ("L", "R"):
        idx = [i for i in range(len(items)) if sides[i] == side]
        if not idx:
            continue
        ys = [(boxes[i][1] + boxes[i][3]) / 2 - heights[i] / 2 for i in idx]
        hs = [heights[i] for i in idx]
        pos = spread(ys, hs, 20, h - 20)
        for k, i in enumerate(idx):
            label_y[i] = pos[k]

    for i, it in enumerate(items):
        col = COLOURS[i % len(COLOURS)]
        x0, y0, x1, y1 = boxes[i]
        d.rectangle([x0, y0, x1, y1], outline=col, width=5)

        # numbered badge on the box corner
        r = 24
        d.ellipse([x0 - r, y0 - r, x0 + r, y0 + r], fill=col)
        d.text((x0, y0), str(i + 1), fill=(0, 0, 0), font=f_num, anchor="mm")

        # label in the margin
        ly = label_y[i]
        if sides[i] == "L":
            lx0, lx1 = 16, MARGIN - 16
            ax, bx = lx1, x0
        else:
            lx0, lx1 = w + MARGIN + 16, w + 2 * MARGIN - 16
            ax, bx = lx0, x1
        d.rounded_rectangle([lx0, ly, lx1, ly + heights[i]], radius=14, fill=(40, 44, 90), outline=col, width=3)
        ty = ly + 8
        for line in wrapped[i]:
            d.text((lx0 + 14, ty), line, fill=(246, 244, 255), font=f_note)
            ty += 38

        # arrow from the label to the box
        ay = ly + heights[i] / 2
        by = min(max(ay, y0), y1)
        d.line([(ax, ay), (bx, by)], fill=col, width=4)
        # arrow head
        import math
        ang = math.atan2(by - ay, bx - ax)
        for s in (-0.45, 0.45):
            d.line([(bx, by), (bx - 22 * math.cos(ang + s), by - 22 * math.sin(ang + s))], fill=col, width=4)

    canvas.save(out_path)
    return items


def inject(readme, name, md):
    start = "<!--CALLOUTS:%s-->" % name
    end = "<!--/CALLOUTS-->"
    a = readme.find(start)
    if a < 0:
        return readme
    b = readme.find(end, a)
    if b < 0:
        return readme
    return readme[: a + len(start)] + "\n" + md + "\n" + readme[b:]


def main():
    if not os.path.isdir(SHOTS):
        print("No Docs/screens folder yet. Run the scene, press F9, then run this again.")
        return 1
    readme = open(README, encoding="utf-8").read() if os.path.exists(README) else ""
    done = 0
    for name in sorted(os.listdir(SHOTS)):
        folder = os.path.join(SHOTS, name)
        colour = os.path.join(folder, "colour.png")
        if not os.path.isfile(colour):
            continue
        grey = os.path.join(folder, "greyscale.png")
        if not os.path.isfile(grey):
            luminance_grey(Image.open(colour)).save(grey)
        ann = os.path.join(folder, "annotations.json")
        items = []
        if os.path.isfile(ann):
            items = annotate(colour, ann, os.path.join(folder, "annotated.png"))
        else:
            Image.open(colour).save(os.path.join(folder, "annotated.png"))
        md = "\n".join("%d. %s" % (i + 1, it["note"]) for i, it in enumerate(items))
        with open(os.path.join(folder, "callouts.md"), "w", encoding="utf-8") as fh:
            fh.write(md + "\n")
        readme = inject(readme, name, md)
        done += 1
        print("ok", name, "(%d callouts)" % len(items))
    if readme:
        with open(README, "w", encoding="utf-8") as fh:
            fh.write(readme)
    print("%d screens processed" % done)
    return 0


if __name__ == "__main__":
    sys.exit(main())
