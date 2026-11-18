"""
make_sprites.py - draws every sprite used by the Roll Rush menu system.

All shapes are drawn from scratch with Pillow (no downloaded art, no AI images).
Everything is white on transparent so Unity can tint it with the palette.
Run:  python Tools/make_sprites.py
"""
import math, os
from PIL import Image, ImageDraw, ImageFilter

OUT = os.path.join(os.path.dirname(__file__), "..", "Assets", "Lab07", "Resources", "Lab07", "Sprites")
os.makedirs(OUT, exist_ok=True)
SS = 4  # supersampling for smooth edges


def save(mask, name, size):
    """mask is an 'L' image drawn at SS x size; turn it into white RGBA and save."""
    mask = mask.resize((size, size), Image.LANCZOS)
    img = Image.new("RGBA", (size, size), (255, 255, 255, 0))
    img.putalpha(mask)
    img.save(os.path.join(OUT, name + ".png"))


def canvas(size):
    return Image.new("L", (size * SS, size * SS), 0)


def S(v):
    return v * SS


def pts(points):
    return [(S(x), S(y)) for x, y in points]


def thick_line(d, points, w, fill=255):
    """polyline with round joins and caps"""
    p = pts(points)
    d.line(p, fill=fill, width=S(w), joint="curve")
    r = S(w) / 2
    for x, y in (p[0], p[-1]):
        d.ellipse((x - r, y - r, x + r, y + r), fill=fill)


def rrect(d, box, r, fill=255):
    x0, y0, x1, y1 = box
    d.rounded_rectangle((S(x0), S(y0), S(x1), S(y1)), radius=S(r), fill=fill)


def circle(d, cx, cy, r, fill=255, outline=None, width=0):
    d.ellipse((S(cx - r), S(cy - r), S(cx + r), S(cy + r)), fill=fill, outline=outline, width=S(width))


def ring(d, cx, cy, r, w, fill=255):
    circle(d, cx, cy, r, fill=fill)
    circle(d, cx, cy, r - w, fill=0)


def rounded_poly(d, points, r, fill=255):
    """filled polygon with softened corners"""
    d.polygon(pts(points), fill=fill)
    thick_line(d, points + [points[0]], r * 2, fill)


# ---------------------------------------------------------------- 9-slice shapes
def shape_rrect(name, size, radius, outline=0):
    m = canvas(size)
    d = ImageDraw.Draw(m)
    rrect(d, (0, 0, size, size), radius)
    if outline:
        rrect(d, (outline, outline, size - outline, size - outline), radius - outline, fill=0)
    save(m, name, size)


shape_rrect("rrect_b44", 128, 40)
shape_rrect("rrect_outline_b44", 128, 40, outline=7)
shape_rrect("pill_b64", 192, 64)
shape_rrect("pill_outline_b64", 192, 64, outline=8)


def shadow(name, size, radius, blur):
    m = Image.new("L", (size * SS, size * SS), 0)
    d = ImageDraw.Draw(m)
    pad = blur * 1.6
    rrect(d, (pad, pad, size - pad, size - pad), radius)
    m = m.filter(ImageFilter.GaussianBlur(S(blur)))
    save(m, name, size)


shadow("shadow_b96", 256, 48, 22)

# ---------------------------------------------------------------- simple shapes
m = canvas(256); circle(ImageDraw.Draw(m), 128, 128, 126); save(m, "circle", 256)
m = canvas(256); ring(ImageDraw.Draw(m), 128, 128, 124, 16); save(m, "ring", 256)

# soft radial vignette: transparent in the middle, opaque at the edges (meta UI: damage flash)
size = 256
v = Image.new("L", (size, size), 0)
px = v.load()
for y in range(size):
    for x in range(size):
        dx, dy = (x - 127.5) / 127.5, (y - 127.5) / 127.5
        r = max(abs(dx), abs(dy)) * 0.55 + math.hypot(dx, dy) * 0.45
        a = max(0.0, (r - 0.45) / 0.65)
        px[x, y] = int(255 * min(1.0, a * a))
img = Image.new("RGBA", (size, size), (255, 255, 255, 0)); img.putalpha(v)
img.save(os.path.join(OUT, "vignette.png"))

# vertical fade (opaque top -> transparent bottom) used for the background gradient
img = Image.new("RGBA", (4, 256), (255, 255, 255, 0))
for y in range(256):
    a = int(255 * (1 - y / 255) ** 1.4)
    for x in range(4):
        img.putpixel((x, y), (255, 255, 255, a))
img.save(os.path.join(OUT, "fade_v.png"))

# faint grid tile for the arena floor (tiled in Unity)
img = Image.new("RGBA", (64, 64), (255, 255, 255, 0))
d = ImageDraw.Draw(img)
d.rectangle((0, 0, 63, 1), fill=(255, 255, 255, 40))
d.rectangle((0, 0, 1, 63), fill=(255, 255, 255, 40))
img.save(os.path.join(OUT, "grid_t.png"))

# fully rounded bar for the health bar fill: drawn 8:1 so the caps stay round
bw, bh = 512, 64
m = Image.new("L", (bw * SS, bh * SS), 0)
ImageDraw.Draw(m).rounded_rectangle((0, 0, S(bw), S(bh)), radius=S(bh // 2), fill=255)
m = m.resize((bw, bh), Image.LANCZOS)
img = Image.new("RGBA", (bw, bh), (255, 255, 255, 0)); img.putalpha(m)
img.save(os.path.join(OUT, "bar_8x1.png"))

# ---------------------------------------------------------------- ball + skin patterns
def ball():
    size = 256
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    px = img.load()
    for y in range(size):
        for x in range(size):
            dx, dy = (x - 127.5) / 126, (y - 127.5) / 126
            r = math.hypot(dx, dy)
            if r <= 1:
                # light from the top-left: bright spot to soft dark edge
                lx, ly = (x - 90) / 150, (y - 85) / 150
                l = max(0.0, 1 - math.hypot(lx, ly))
                shade = 0.62 + 0.38 * l ** 0.9
                edge = 1.0 if r < 0.985 else max(0.0, (1 - r) / 0.015)
                c = int(255 * shade)
                px[x, y] = (c, c, c, int(255 * edge))
    img.save(os.path.join(OUT, "ball.png"))


ball()


def pattern(name, kind):
    size = 256
    m = canvas(size)
    d = ImageDraw.Draw(m)
    if kind == "stripe":
        rrect(d, (-20, 96, 276, 130), 0)
        rrect(d, (-20, 150, 276, 184), 0)
    elif kind == "dots":
        for cx, cy in [(88, 88), (168, 88), (128, 128), (88, 168), (168, 168)]:
            circle(d, cx, cy, 15)
    elif kind == "star":
        star_pts(d, 128, 128, 62, 26)
    # clip to the ball
    clip = canvas(size)
    circle(ImageDraw.Draw(clip), 128, 128, 120)
    m = Image.composite(m, Image.new("L", m.size, 0), clip)
    save(m, name, size)


def star_pts(d, cx, cy, ro, ri, fill=255):
    p = []
    for i in range(10):
        a = -math.pi / 2 + i * math.pi / 5
        r = ro if i % 2 == 0 else ri
        p.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    rounded_poly(d, p, 3, fill)


pattern("ball_stripe", "stripe")
pattern("ball_dots", "dots")
pattern("ball_star", "star")

# ---------------------------------------------------------------- icons (128 px)
I = 128


def icon(name, fn):
    m = canvas(I)
    fn(ImageDraw.Draw(m))
    save(m, name, I)


icon("icon_play", lambda d: rounded_poly(d, [(44, 28), (44, 100), (104, 64)], 5))


def _pause(d):
    rrect(d, (34, 24, 54, 104), 7)
    rrect(d, (74, 24, 94, 104), 7)


icon("icon_pause", _pause)
icon("icon_back", lambda d: thick_line(d, [(80, 24), (40, 64), (80, 104)], 16))
icon("icon_next", lambda d: thick_line(d, [(48, 24), (88, 64), (48, 104)], 16))
icon("icon_close", lambda d: (thick_line(d, [(32, 32), (96, 96)], 15), thick_line(d, [(96, 32), (32, 96)], 15)))
icon("icon_check", lambda d: thick_line(d, [(26, 68), (52, 94), (102, 36)], 17))


def _lock(d):
    thick_line(d, [(42, 62), (42, 44), (50, 28), (64, 22), (78, 28), (86, 44), (86, 62)], 12)
    rrect(d, (28, 58, 100, 110), 12)
    circle(d, 64, 80, 8, fill=0)
    rrect(d, (60, 82, 68, 98), 3, fill=0)


icon("icon_lock", _lock)


def _star(d):
    star_pts(d, 64, 68, 54, 24)


icon("icon_star", _star)


def _star_outline(d):
    star_pts(d, 64, 68, 54, 24)
    # cut an inset star out of the middle
    star_pts(d, 64, 68, 34, 15, fill=0)


icon("icon_star_outline", _star_outline)


def _coin(d):
    circle(d, 64, 64, 54)
    d.ellipse((S(24), S(24), S(104), S(104)), outline=0, width=S(7))
    star_pts(d, 64, 66, 24, 11, fill=0)


icon("icon_coin", _coin)


def _heart(d):
    circle(d, 42, 48, 24)
    circle(d, 86, 48, 24)
    rounded_poly(d, [(20, 56), (108, 56), (64, 108)], 6)


icon("icon_heart", _heart)


def _gear(d):
    for i in range(8):
        a = i * math.pi / 4
        cx, cy = 64 + 44 * math.cos(a), 64 + 44 * math.sin(a)
        r = 11
        p = [(cx + r * math.cos(a + t), cy + r * math.sin(a + t)) for t in (0.8, 2.34, 3.94, 5.48)]
        # a small rotated square for each tooth
        ux, uy = math.cos(a), math.sin(a)
        vx, vy = -uy, ux
        q = [(cx + ux * 12 + vx * 11, cy + uy * 12 + vy * 11), (cx + ux * 12 - vx * 11, cy + uy * 12 - vy * 11),
             (cx - ux * 14 - vx * 11, cy - uy * 14 - vy * 11), (cx - ux * 14 + vx * 11, cy - uy * 14 + vy * 11)]
        d.polygon(pts(q), fill=255)
    circle(d, 64, 64, 36)
    circle(d, 64, 64, 15, fill=0)


icon("icon_gear", _gear)


def _bag(d):
    thick_line(d, [(44, 44), (44, 30), (52, 22), (76, 22), (84, 30), (84, 44)], 10)
    rrect(d, (20, 42, 108, 108), 14)
    circle(d, 46, 64, 6, fill=0)
    circle(d, 82, 64, 6, fill=0)


icon("icon_bag", _bag)


def _bolt(d):
    rounded_poly(d, [(76, 10), (30, 72), (58, 72), (48, 118), (98, 52), (68, 52)], 3)


icon("icon_bolt", _bolt)


def _shield(d):
    p = [(64, 10), (104, 24), (104, 62)]
    d.polygon(pts([(64, 10), (106, 26), (106, 62), (98, 84), (64, 118), (30, 84), (22, 62), (22, 26)]), fill=255)
    thick_line(d, [(64, 10), (106, 26), (106, 62), (98, 84), (64, 118), (30, 84), (22, 62), (22, 26), (64, 10)], 8)
    thick_line(d, [(44, 62), (58, 76), (86, 46)], 10, fill=0)


icon("icon_shield", _shield)


def _restart(d):
    # 300 degree arc + arrow head
    cx, cy, r = 64, 66, 38
    steps = 60
    arc = []
    for i in range(steps + 1):
        a = math.radians(-60 + 300 * i / steps)
        arc.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    thick_line(d, arc, 15)
    ex, ey = arc[0]
    rounded_poly(d, [(ex - 6, ey - 26), (ex + 30, ey + 6), (ex - 26, ey + 14)], 3)


icon("icon_restart", _restart)


def _home(d):
    rounded_poly(d, [(64, 14), (116, 62), (12, 62)], 5)
    rrect(d, (26, 58, 102, 112), 8)
    rrect(d, (52, 76, 76, 112), 6, fill=0)


icon("icon_home", _home)


def _speaker(d, on=True):
    rounded_poly(d, [(24, 50), (44, 50), (68, 28), (68, 100), (44, 78), (24, 78)], 4)
    if on:
        for r, w in ((22, 9), (38, 9)):
            arc = [(70 + r * math.cos(math.radians(a)), 64 + r * math.sin(math.radians(a))) for a in range(-42, 43, 6)]
            thick_line(d, arc, w)
    else:
        thick_line(d, [(84, 48), (116, 80)], 10)
        thick_line(d, [(116, 48), (84, 80)], 10)


icon("icon_sound", lambda d: _speaker(d, True))
icon("icon_sound_off", lambda d: _speaker(d, False))


def _music(d):
    thick_line(d, [(50, 94), (50, 26), (96, 16), (96, 80)], 10)
    circle(d, 38, 96, 17)
    circle(d, 84, 84, 17)


icon("icon_music", _music)


def _vibrate(d):
    rrect(d, (42, 14, 86, 114), 10)
    rrect(d, (50, 26, 78, 90), 4, fill=0)
    circle(d, 64, 102, 4, fill=0)
    for x0, sign in ((22, -1), (106, 1)):
        thick_line(d, [(x0 + sign * 2, 42), (x0 - sign * 8, 52), (x0 - sign * 8, 76), (x0 + sign * 2, 86)], 8)


icon("icon_vibrate", _vibrate)


def _info(d):
    circle(d, 64, 64, 54)
    circle(d, 64, 38, 8, fill=0)
    rrect(d, (57, 54, 71, 94), 6, fill=0)


icon("icon_info", _info)


def _hand(d):  # joystick side / controls
    circle(d, 64, 64, 54)
    circle(d, 64, 64, 22, fill=0)
    circle(d, 64, 64, 10)


icon("icon_stick", _hand)


def _clock(d):
    ring(d, 64, 66, 52, 11)
    thick_line(d, [(64, 66), (64, 38)], 10)
    thick_line(d, [(64, 66), (84, 78)], 10)
    rrect(d, (52, 4, 76, 16), 4)


icon("icon_clock", _clock)


def _trophy(d):
    rrect(d, (34, 14, 94, 66), 14)
    d.rectangle((S(34), S(14), S(94), S(36)), fill=255)
    thick_line(d, [(34, 24), (18, 24), (18, 40), (34, 56)], 8)
    thick_line(d, [(94, 24), (110, 24), (110, 40), (94, 56)], 8)
    rrect(d, (56, 62, 72, 92), 3)
    rrect(d, (38, 92, 90, 108), 6)


icon("icon_trophy", _trophy)


def _warn(d):  # guard: triangle with exclamation cut-out (a shape cue, not just red)
    rounded_poly(d, [(64, 14), (116, 108), (12, 108)], 8)
    rrect(d, (58, 44, 70, 80), 5, fill=0)
    circle(d, 64, 94, 7, fill=0)


icon("icon_warn", _warn)


def _plus(d):
    thick_line(d, [(24, 64), (104, 64)], 15)
    thick_line(d, [(64, 24), (64, 104)], 15)


icon("icon_plus", _plus)
icon("icon_minus", lambda d: thick_line(d, [(26, 64), (102, 64)], 15))


def _hit(d):  # little burst used on the "hit" simulation button
    pts_ = []
    for i in range(16):
        a = i * math.pi / 8
        r = 56 if i % 2 == 0 else 28
        pts_.append((64 + r * math.cos(a), 64 + r * math.sin(a)))
    d.polygon(pts(pts_), fill=255)


icon("icon_burst", _hit)

print("sprites written to", os.path.abspath(OUT), len(os.listdir(OUT)), "files")
