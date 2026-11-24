"""
videokit.py - turns a session script (JSON) into a narrated MP4 lesson.

Pipeline:  script.json -> narration (TTS, one clip per beat) -> animated scenes
           drawn with Pillow -> one MP4 per scene (ffmpeg) -> concat + audio.

Every element on screen appears exactly when the narrator starts talking about
it, because each "beat" of narration is synthesised separately and timed.
"""
import asyncio, hashlib, json, math, os, re, shutil, subprocess, sys
from PIL import Image, ImageDraw, ImageFont

# ----------------------------------------------------------------- settings
W, H, FPS = 1920, 1080, 30
SR = 24000                      # audio sample rate (mono, 16-bit)
GAP = 0.35                      # pause after each beat (s)
HEAD, TAIL = 0.45, 0.7          # silence before first / after last beat (s)
XFADE = 0.4                     # cross-dissolve from previous scene (s)
REVEAL = 0.55                   # duration of an element's entrance (s)
STAGGER = 0.3                   # delay between elements shown in one beat (s)

# Course palette (taken from the session slides)
NAVY = (31, 26, 61); AMBER = (242, 169, 59); CREAM = (255, 245, 230)
DARK_AMBER = (184, 110, 0); INK = (74, 69, 102); WHITE = (255, 255, 255)
LAVENDER = (217, 214, 236); MUTED = (150, 146, 170); PAPER = (250, 249, 252)
RULE = (230, 228, 238)

# ----------------------------------------------------------------- fonts
_FONT_CANDIDATES = {
    "regular": ["fonts/Lato-Regular.ttf",
                "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
                "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"],
    "bold": ["fonts/Lato-Bold.ttf",
             "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
             "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"],
    "italic": ["fonts/Lato-Italic.ttf",
               "/usr/share/fonts/truetype/liberation/LiberationSans-Italic.ttf",
               "/usr/share/fonts/truetype/dejavu/DejaVuSans-Oblique.ttf"],
}
_font_cache = {}

def font(style, size):
    key = (style, size)
    if key not in _font_cache:
        for path in _FONT_CANDIDATES[style]:
            if os.path.exists(path):
                _font_cache[key] = ImageFont.truetype(path, size)
                break
        else:
            _font_cache[key] = ImageFont.load_default(size)
    return _font_cache[key]

# ----------------------------------------------------------------- helpers
def ease(x):
    x = max(0.0, min(1.0, x))
    return 1 - (1 - x) ** 3

def mix(c, bg, a):
    return tuple(int(bg[i] + (c[i] - bg[i]) * a) for i in range(3))

def wrap(text, f, maxw):
    lines = []
    for para in str(text).split("\n"):
        words, cur = para.split(), ""
        for w in words:
            test = (cur + " " + w).strip()
            if f.getlength(test) <= maxw or not cur:
                cur = test
            else:
                lines.append(cur); cur = w
        lines.append(cur)
    return lines

def text_block(d, xy, text, f, color, maxw, bg, a=1.0, lh=1.28, anchor_x="l"):
    """Draw wrapped text; returns the height used."""
    x, y = xy
    step = int(f.size * lh)
    for i, line in enumerate(wrap(text, f, maxw)):
        lx = x if anchor_x == "l" else x - f.getlength(line) / 2
        d.text((lx, y + i * step), line, font=f, fill=mix(color, bg, a))
    return step * len(wrap(text, f, maxw))

def text_height(text, f, maxw, lh=1.28):
    return int(f.size * lh) * len(wrap(text, f, maxw))

def pill(d, x, y, text, a=1.0, bg=WHITE, fill=AMBER, color=NAVY, size=20):
    f = font("bold", size)
    spaced = " ".join(text.upper()) if len(text) < 26 else text.upper()
    w = f.getlength(spaced) + 44
    d.rounded_rectangle([x, y, x + w, y + size + 20], radius=(size + 20) // 2,
                        fill=mix(fill, bg, a))
    d.text((x + 22, y + 9), spaced, font=f, fill=mix(color, mix(fill, bg, a), a))
    return w

# ----------------------------------------------------------------- the canvas
BLOCKS = {  # key: (name, question, grid cell as (col0, col1, row0, row1) in a 10x3 grid)
    "kp":   ("Key Partners", "Who helps us?",                (0, 2, 0, 2)),
    "ka":   ("Key Activities", "What do we do?",             (2, 4, 0, 1)),
    "kr":   ("Key Resources", "What do we need?",            (2, 4, 1, 2)),
    "vp":   ("Value Propositions", "Which problem do we solve?", (4, 6, 0, 2)),
    "cr":   ("Customer Relationships", "How do we interact?", (6, 8, 0, 1)),
    "ch":   ("Channels", "How do we reach them?",            (6, 8, 1, 2)),
    "cs":   ("Customer Segments", "For whom?",               (8, 10, 0, 2)),
    "cost": ("Cost Structure", "What does it cost?",         (0, 5, 2, 3)),
    "rev":  ("Revenue Streams", "How do we earn money?",     (5, 10, 2, 3)),
}
BLOCK_ORDER = ["cs", "vp", "ch", "cr", "rev", "ka", "kr", "kp", "cost"]

def block_rect(key, x, y, w, h, gap):
    c0, c1, r0, r1 = BLOCKS[key][2]
    rows = [0, 0.37, 0.74, 1.0]
    return (x + w * c0 / 10 + gap / 2, y + h * rows[r0] + gap / 2,
            x + w * c1 / 10 - gap / 2, y + h * rows[r1] - gap / 2)

def draw_canvas(d, x, y, w, h, alphas, focus=None, mini=False, bg=WHITE, labels=None):
    """alphas: key -> 0..1 visibility.  focus: highlighted block key.
    labels: optional {key: [name, question]} to reuse the grid (e.g. Lean Canvas)."""
    labels = labels or {}
    gap = 8 if mini else 12
    fn = font("bold", 17 if mini else 27)
    fq = font("italic", 22)
    for key in BLOCKS:
        a = alphas.get(key, 1.0)
        if a <= 0: continue
        x0, y0, x1, y1 = block_rect(key, x, y, w, h, gap)
        if focus:
            fill = AMBER if key == focus else PAPER
            edge = DARK_AMBER if key == focus else RULE
            tc = NAVY if key == focus else MUTED
        else:
            fill, edge, tc = CREAM, AMBER, NAVY
            if key == "vp": fill = AMBER
        oy = (1 - a) * 18
        d.rounded_rectangle([x0, y0 + oy, x1, y1 + oy], radius=10 if mini else 14,
                            fill=mix(fill, bg, a), outline=mix(edge, bg, a),
                            width=3 if key == focus else 2)
        name, q = labels.get(key, BLOCKS[key][:2])
        pad = 12 if mini else 20
        used = text_block(d, (x0 + pad, y0 + pad + oy), name, fn, tc, x1 - x0 - 2 * pad,
                          mix(fill, bg, a), a, lh=1.15)
        if not mini:
            text_block(d, (x0 + pad, y0 + pad + used + 8 + oy), q, fq,
                       DARK_AMBER if key != "vp" else NAVY, x1 - x0 - 2 * pad,
                       mix(fill, bg, a), a, lh=1.2)

# ----------------------------------------------------------------- scenes
class Scene:
    """A scene = layout + list of beats. Each beat says something and can
    reveal elements (ids) of the layout. Unreferenced elements appear at t=0."""
    dark = False

    def __init__(self, spec, meta):
        self.s, self.meta = spec, meta
        self.reveal = {}          # element id -> time it starts appearing

    def element_ids(self):
        return []

    def schedule(self, beat_starts):
        shown = set()
        for b, t0 in zip(self.s["beats"], beat_starts):
            ids = b.get("show", [])
            ids = [ids] if isinstance(ids, str) else ids
            for i, e in enumerate(ids):
                self.reveal[e] = max(0.05, t0 - 0.15 + i * STAGGER)
                shown.add(e)
        for e in self.element_ids():
            if e not in shown:
                self.reveal.setdefault(e, 0.15)

    def a(self, eid, t):
        return ease((t - self.reveal.get(eid, 0.15)) / REVEAL)

    def state_key(self, t):
        """Frames with the same key are identical, so they are drawn once."""
        if any(r <= t < r + REVEAL + 1.0 / FPS for r in self.reveal.values()):
            return None
        return tuple(sorted(e for e, r in self.reveal.items() if t >= r))

    # chrome shared by light scenes
    def base(self):
        bg = NAVY if self.dark else WHITE
        im = Image.new("RGB", (W, H), bg)
        return im, ImageDraw.Draw(im), bg

    def header(self, d, t, bg):
        a = self.a("_header", t)
        if self.s.get("label"):
            pill(d, 90, 70, self.s["label"], a, bg=bg)
        if self.s.get("title"):
            text_block(d, (90, 128 + (1 - a) * 14), self.s["title"], font("bold", 58),
                       WHITE if self.dark else NAVY, 1740, bg, a, lh=1.12)

    def footer(self, d, bg):
        f = font("regular", 19)
        txt = f'{self.meta.get("course", "")}  ·  {self.meta.get("session", "")}'
        d.text((90, H - 52), txt, font=f, fill=LAVENDER if self.dark else MUTED)

    def draw(self, t):
        raise NotImplementedError


class TitleScene(Scene):
    dark = True
    def element_ids(self): return ["_header", "subtitle", "author"]
    def draw(self, t):
        im, d, bg = self.base()
        # decorative circles, as on the slides
        d.ellipse([1380, -260, 2060, 420], fill=(92, 62, 72))
        d.ellipse([1560, 640, 2020, 1100], fill=(43, 72, 93))
        a = self.a("_header", t)
        pill(d, 120, 290, self.s.get("label", ""), a, bg=bg)
        th = text_block(d, (120, 380 + (1 - a) * 20), self.s["title"], font("bold", 96),
                        WHITE, 1250, bg, a, lh=1.08)
        a2 = self.a("subtitle", t)
        text_block(d, (120, 380 + th + 30 + (1 - a2) * 20), self.s.get("subtitle", ""),
                   font("regular", 40), LAVENDER, 1200, bg, a2)
        a3 = self.a("author", t)
        text_block(d, (120, 860), self.meta.get("author", ""), font("bold", 26), WHITE, 1200, bg, a3)
        text_block(d, (120, 900), self.meta.get("course", ""), font("regular", 24), LAVENDER, 1200, bg, a3)
        return im


class StatementScene(Scene):
    dark = True
    def element_ids(self): return ["_header", "text", "sub"]
    def draw(self, t):
        im, d, bg = self.base()
        d.ellipse([1500, 700, 2100, 1300], fill=(43, 38, 80))
        a = self.a("_header", t)
        if self.s.get("label"):
            pill(d, 120, 250, self.s["label"], a, bg=bg)
        a1 = self.a("text", t)
        hgt = text_block(d, (120, 340 + (1 - a1) * 20), self.s["text"], font("bold", 76),
                         WHITE, 1550, bg, a1, lh=1.15)
        a2 = self.a("sub", t)
        text_block(d, (120, 340 + hgt + 50 + (1 - a2) * 20), self.s.get("sub", ""),
                   font("regular", 40), AMBER, 1450, bg, a2, lh=1.35)
        self.footer(d, bg)
        return im


class CardsScene(Scene):
    def element_ids(self):
        return ["_header"] + [f"card{i}" for i in range(len(self.s["cards"]))] + \
               (["banner"] if self.s.get("banner") else [])
    def draw(self, t):
        im, d, bg = self.base()
        self.header(d, t, bg)
        cards = self.s["cards"]; n = len(cards)
        gap, x0, top = 36, 90, 300
        cw = (1740 - gap * (n - 1)) / n
        ch = 430 if self.s.get("banner") else 560
        need = 0
        for c in cards:
            th = text_height(c["title"], font("bold", 38), cw - 68, 1.15)
            need = max(need, 190 + th + text_height(c.get("text", ""), font("regular", 31), cw - 68, 1.32))
        ch = int(min(ch, max(need + 20, 300)))
        for i, c in enumerate(cards):
            a = self.a(f"card{i}", t)
            if a <= 0: continue
            x = x0 + i * (cw + gap); oy = (1 - a) * 24
            fill = mix(CREAM, bg, a)
            d.rounded_rectangle([x, top + oy, x + cw, top + ch + oy], radius=18, fill=fill)
            num = c.get("tag", str(i + 1))
            fnum = font("bold", 28)
            bw = max(60, fnum.getlength(num) + 36)
            d.rounded_rectangle([x + 34, top + 34 + oy, x + 34 + bw, top + 94 + oy], radius=30,
                                fill=mix(AMBER, fill, a))
            d.text((x + 34 + bw / 2 - fnum.getlength(num) / 2, top + 47 + oy), num, font=fnum,
                   fill=mix(WHITE, mix(AMBER, fill, a), a))
            hh = text_block(d, (x + 34, top + 125 + oy), c["title"], font("bold", 38),
                            NAVY, cw - 68, fill, a, lh=1.15)
            body = c.get("text", "")
            room = ch - 170 - hh
            fs = 31
            while fs > 20 and text_height(body, font("regular", fs), cw - 68, 1.32) > room:
                fs -= 1
            text_block(d, (x + 34, top + 145 + hh + oy), body, font("regular", fs),
                       INK, cw - 68, fill, a, lh=1.32)
        if self.s.get("banner"):
            a = self.a("banner", t)
            if a > 0:
                y = top + ch + 40 + (1 - a) * 18
                bh = text_height(self.s["banner"], font("bold", 31), 1660, 1.2) + 50
                d.rounded_rectangle([90, y, 1830, y + bh], radius=14, fill=mix(AMBER, bg, a))
                text_block(d, (124, y + 27), self.s["banner"], font("bold", 31), NAVY, 1660,
                           mix(AMBER, bg, a), a, lh=1.2)
        self.footer(d, bg)
        return im


class CanvasScene(Scene):
    def element_ids(self): return ["_header", "sides"] + list(BLOCKS)
    def draw(self, t):
        im, d, bg = self.base()
        self.header(d, t, bg)
        x, y, w, h = 90, 300, 1740, 680
        alphas = {k: self.a(k, t) for k in BLOCKS}
        draw_canvas(d, x, y, w, h, alphas, labels=self.s.get("labels"))
        a = self.a("sides", t)
        if a > 0 and not self.s.get("labels"):
            f = font("bold", 22)
            for (x0, x1, txt) in [(x, x + w * 0.4, "HOW WE MAKE IT HAPPEN  ·  EFFICIENCY"),
                                  (x + w * 0.6, x + w, "CUSTOMERS AND VALUE")]:
                d.line([x0 + 6, 270, x1 - 6, 270], fill=mix(DARK_AMBER, bg, a), width=3)
                tw = f.getlength(txt)
                d.rectangle([(x0 + x1) / 2 - tw / 2 - 12, 255, (x0 + x1) / 2 + tw / 2 + 12, 285], fill=bg)
                d.text(((x0 + x1) / 2 - tw / 2, 258), txt, font=f, fill=mix(DARK_AMBER, bg, a))
        self.footer(d, bg)
        return im


class BlockScene(Scene):
    """One canvas block: mini-canvas map on the left, guidance on the right."""
    def element_ids(self):
        return ["_header"] + [f"q{i}" for i in range(len(self.s["questions"]))] + ["mistake", "example"]
    def draw(self, t):
        im, d, bg = self.base()
        key = self.s["block"]
        n = BLOCK_ORDER.index(key) + 1 if key in BLOCK_ORDER else 0
        self.s.setdefault("label", f"Block {n} of 9")
        self.s.setdefault("title", BLOCKS[key][0])
        self.header(d, t, bg)
        # left: map of the canvas with the current block highlighted
        draw_canvas(d, 90, 300, 720, 380, {}, focus=key, mini=True)
        fq = font("italic", 34)
        text_block(d, (90, 720), "“" + BLOCKS[key][1] + "”", fq, DARK_AMBER, 720, bg)
        # right: questions, mistake, example
        X, R = 880, 1830
        y = 300
        d.text((X, y), "ASK YOURSELF", font=font("bold", 22), fill=DARK_AMBER)
        y += 46
        fqs = font("regular", 31)
        for i, q in enumerate(self.s["questions"]):
            a = self.a(f"q{i}", t); oy = (1 - a) * 16
            hq = text_height(q, fqs, R - X - 70)
            if a > 0:
                d.ellipse([X, y + 2 + oy, X + 40, y + 42 + oy], fill=mix(AMBER, bg, a))
                fn = font("bold", 22)
                d.text((X + 20 - fn.getlength(str(i + 1)) / 2, y + 9 + oy), str(i + 1), font=fn,
                       fill=mix(NAVY, mix(AMBER, bg, a), a))
                text_block(d, (X + 62, y + 3 + oy), q, fqs, NAVY, R - X - 70, bg, a)
            y += max(hq, 44) + 22
        y += 14
        for eid, head, fill, hc, tc in [("mistake", "TYPICAL MISTAKE", NAVY, AMBER, WHITE),
                                         ("example", "EXAMPLE", CREAM, DARK_AMBER, NAVY)]:
            txt = self.s.get(eid)
            if not txt: continue
            a = self.a(eid, t); oy = (1 - a) * 16
            f = font("regular", 28)
            hgt = text_height(txt, f, R - X - 60) + 70
            if a > 0:
                fl = mix(fill, bg, a)
                d.rounded_rectangle([X, y + oy, R, y + hgt + oy], radius=14, fill=fl)
                d.text((X + 30, y + 18 + oy), head, font=font("bold", 20), fill=mix(hc, fl, a))
                text_block(d, (X + 30, y + 52 + oy), txt, f, tc, R - X - 60, fl, a, lh=1.25)
            y += hgt + 20
        self.footer(d, bg)
        return im


class SplitScene(Scene):
    def element_ids(self):
        L, Rr = self.s["left"]["items"], self.s["right"]["items"]
        return ["_header", "lhead", "rhead"] + [f"l{i}" for i in range(len(L))] + \
               [f"r{i}" for i in range(len(Rr))] + (["banner"] if self.s.get("banner") else [])
    def draw(self, t):
        im, d, bg = self.base()
        self.header(d, t, bg)
        top = 300 if len(wrap(self.s["title"], font("bold", 58), 1740)) == 1 else 360
        for side, x, fill, head_c, item_c, dot in [("left", 90, CREAM, DARK_AMBER, NAVY, AMBER),
                                                    ("right", 980, PAPER, MUTED, MUTED, LAVENDER)]:
            spec = self.s[side]; p = side[0]
            ah = max(self.a(f"{p}head", t), self.a(f"{p}0", t))
            if ah <= 0: continue
            fl = mix(fill, bg, ah)
            d.rounded_rectangle([x, top, x + 850, top + 430], radius=18, fill=fl)
            d.text((x + 40, top + 32), spec["head"].upper(), font=font("bold", 24), fill=mix(head_c, fl, ah))
            for i, it in enumerate(spec["items"]):
                a = self.a(f"{p}{i}", t)
                if a <= 0: continue
                yy = top + 92 + i * 80 + (1 - a) * 14
                d.ellipse([x + 40, yy + 12, x + 60, yy + 32], fill=mix(dot, fl, a))
                txt = it
                d.text((x + 82, yy), txt, font=font("bold" if p == "l" else "regular", 33),
                       fill=mix(item_c, fl, a))
                if p == "r":  # strike-through: needed, but not key
                    lw = font("regular", 33).getlength(txt)
                    d.line([x + 80, yy + 22, x + 86 + lw * a, yy + 22], fill=mix(MUTED, fl, a), width=3)
        if self.s.get("banner"):
            a = self.a("banner", t)
            if a > 0:
                y = top + 460 + (1 - a) * 16
                d.rounded_rectangle([90, y, 1830, y + 130], radius=14, fill=mix(AMBER, bg, a))
                text_block(d, (124, y + 24), self.s["banner"], font("bold", 31), NAVY, 1670,
                           mix(AMBER, bg, a), a, lh=1.22)
        self.footer(d, bg)
        return im


class StrategyScene(Scene):
    """Blue Ocean strategy canvas: value curves drawn progressively."""
    CURVE_TIME = 1.8
    def element_ids(self):
        return ["_header", "axes"] + [f"curve{i}" for i in range(len(self.s["curves"]))]
    def state_key(self, t):
        if any(r <= t < r + self.CURVE_TIME + 0.1 for e, r in self.reveal.items() if e.startswith("curve")):
            return None
        return super().state_key(t)
    def draw(self, t):
        im, d, bg = self.base()
        self.header(d, t, bg)
        factors = self.s["factors"]; n = len(factors)
        x0, x1, y0, y1 = 200, 1800, 380, 790
        a = self.a("axes", t)
        d.line([x0, y1, x1, y1], fill=mix(INK, bg, a), width=3)
        d.line([x0, y0, x0, y1], fill=mix(INK, bg, a), width=3)
        fl = font("bold", 20)
        for lbl, yy in [("HIGH", y0), ("LOW", y1 - 22)]:
            d.text((x0 - 20 - fl.getlength(lbl), yy), lbl, font=fl, fill=mix(MUTED, bg, a))
        step = (x1 - x0) / n
        ff = font("regular", 21)
        xs = [x0 + step * (i + 0.5) for i in range(n)]
        for i, f_ in enumerate(factors):
            d.line([xs[i], y1, xs[i], y1 + 10], fill=mix(INK, bg, a), width=2)
            for j, line in enumerate(wrap(f_, ff, step - 10)):
                d.text((xs[i] - ff.getlength(line) / 2, y1 + 22 + j * 26), line, font=ff,
                       fill=mix(INK, bg, a))
        vmax = self.s.get("max", 5)
        lx = x0
        for k, c in enumerate(self.s["curves"]):
            r = self.reveal.get(f"curve{k}", 0.15)
            p = max(0.0, min(1.0, (t - r) / self.CURVE_TIME))
            if p <= 0: continue
            col = AMBER if c.get("color") == "amber" else INK
            pts = [(xs[i], y1 - (y1 - y0) * v / vmax) for i, v in enumerate(c["values"])]
            # progressive polyline
            total = (n - 1) * p
            k_full = int(total)
            seg = pts[:k_full + 1]
            if k_full < n - 1:
                fr = total - k_full
                (ax, ay), (bx, by) = pts[k_full], pts[k_full + 1]
                seg.append((ax + (bx - ax) * fr, ay + (by - ay) * fr))
            d.line(seg, fill=col, width=7, joint="curve")
            for i, (px, py) in enumerate(pts):
                if i <= total + 1e-6:
                    d.ellipse([px - 11, py - 11, px + 11, py + 11], fill=col, outline=WHITE, width=3)
            # legend
            la = ease(p * 3)
            d.line([lx, 300, lx + 50, 300], fill=mix(col, bg, la), width=7)
            d.text((lx + 66, 285), c["name"], font=font("bold", 26), fill=mix(NAVY, bg, la))
            lx += 66 + font("bold", 26).getlength(c["name"]) + 60
        if self.s.get("note"):
            d.text((x0, 960), self.s["note"], font=font("italic", 20), fill=MUTED)
        self.footer(d, bg)
        return im


class ERRCScene(Scene):
    HEADS = [("ELIMINATE", NAVY, WHITE), ("REDUCE", INK, WHITE),
             ("RAISE", AMBER, NAVY), ("CREATE", DARK_AMBER, WHITE)]
    def element_ids(self):
        return ["_header", "q0", "q1", "q2", "q3"] + (["banner"] if self.s.get("banner") else [])
    def draw(self, t):
        im, d, bg = self.base()
        self.header(d, t, bg)
        quads = self.s["quads"]  # list of 4 {"question":..,"items":[..]}
        gw, gh, top = 855, 255, 290
        for i, q in enumerate(quads):
            a = self.a(f"q{i}", t)
            if a <= 0: continue
            col, row = i % 2, i // 2
            x = 90 + col * (gw + 30); y = top + row * (gh + 24) + (1 - a) * 16
            head, hc, htc = self.HEADS[i]
            fl = mix(CREAM, bg, a)
            d.rounded_rectangle([x, y, x + gw, y + gh], radius=16, fill=fl)
            d.rounded_rectangle([x, y, x + 210, y + gh], radius=16, fill=mix(hc, bg, a))
            d.rectangle([x + 190, y, x + 210, y + gh], fill=mix(hc, bg, a))
            d.text((x + 24, y + 26), head, font=font("bold", 27), fill=mix(htc, mix(hc, bg, a), a))
            text_block(d, (x + 24, y + 70), q.get("question", ""), font("italic", 20),
                       htc, 170, mix(hc, bg, a), a * 0.9, lh=1.25)
            fi = font("regular", 29)
            for j, it in enumerate(q["items"]):
                d.text((x + 245, y + 26 + j * 52), "•  " + it, font=fi, fill=mix(NAVY, fl, a))
        if self.s.get("banner"):
            a = self.a("banner", t)
            if a > 0:
                y = top + 2 * (gh + 24) + 6 + (1 - a) * 16
                d.rounded_rectangle([90, y, 1830, y + 96], radius=14, fill=mix(AMBER, bg, a))
                text_block(d, (124, y + 28), self.s["banner"], font("bold", 31), NAVY, 1670,
                           mix(AMBER, bg, a), a)
        if self.s.get("note"):
            d.text((90, H - 90), self.s["note"], font=font("italic", 20), fill=MUTED)
        self.footer(d, bg)
        return im


SCENES = {"title": TitleScene, "statement": StatementScene, "cards": CardsScene,
          "canvas": CanvasScene, "block": BlockScene, "split": SplitScene,
          "strategy": StrategyScene, "errc": ERRCScene}

# ----------------------------------------------------------------- narration
def _run(cmd):
    r = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if r.returncode != 0:
        raise RuntimeError(r.stderr.decode()[-2000:])
    return r.stdout

def _to_pcm(path):
    return _run(["ffmpeg", "-v", "error", "-i", path, "-f", "s16le", "-ac", "1", "-ar", str(SR), "-"])

def tts_edge(text, voice, out, rate="+0%"):
    import edge_tts
    async def go():
        await edge_tts.Communicate(text, voice, rate=rate).save(out)
    try:
        asyncio.get_running_loop()
        import nest_asyncio; nest_asyncio.apply()
        asyncio.get_event_loop().run_until_complete(go())
    except RuntimeError:
        asyncio.run(go())

_gemini_last = [0.0]

def tts_gemini(text, voice, out, model="gemini-2.5-flash-preview-tts", style="", min_interval=6.5):
    """Gemini TTS. Spaces calls (the API allows ~10 requests/minute) and retries on 429."""
    import time
    from google import genai
    from google.genai import types
    client = genai.Client()  # reads GEMINI_API_KEY / GOOGLE_API_KEY
    for attempt in range(8):
        wait = min_interval - (time.time() - _gemini_last[0])
        if wait > 0:
            time.sleep(wait)
        _gemini_last[0] = time.time()
        try:
            resp = client.models.generate_content(
                model=model, contents=(style + " " + text).strip(),
                config=types.GenerateContentConfig(
                    response_modalities=["AUDIO"],
                    speech_config=types.SpeechConfig(voice_config=types.VoiceConfig(
                        prebuilt_voice_config=types.PrebuiltVoiceConfig(voice_name=voice)))))
            break
        except Exception as e:
            if "429" not in str(e):
                raise
            m = re.search(r"retry in ([\d.]+)s", str(e))
            secs = float(m.group(1)) + 2 if m else 60
            print(f"  Gemini rate limit, waiting {secs:.0f}s...")
            time.sleep(secs)
    else:
        raise RuntimeError("Gemini TTS kept hitting the rate limit")
    pcm = resp.candidates[0].content.parts[0].inline_data.data  # 24 kHz s16le mono
    raw = out + ".pcm"
    open(raw, "wb").write(pcm)
    _run(["ffmpeg", "-v", "error", "-y", "-f", "s16le", "-ar", "24000", "-ac", "1", "-i", raw, out])
    os.remove(raw)

def narrate(text, cfg, cache="tts_cache"):
    """Returns 16-bit mono PCM bytes at SR for one beat."""
    engine = cfg.get("tts", "edge")
    if engine == "none" or not text.strip():   # silent preview: ~150 words/min
        secs = max(1.2, len(text.split()) / 2.5) if text.strip() else 0.8
        return b"\x00\x00" * int(secs * SR)
    os.makedirs(cache, exist_ok=True)
    voice = cfg.get("voice", "en-GB-RyanNeural")
    h = hashlib.sha1(f"{engine}|{voice}|{cfg.get('rate','')}|{text}".encode()).hexdigest()[:16]
    path = os.path.join(cache, f"{h}.{'mp3' if engine == 'edge' else 'wav'}")
    if not os.path.exists(path):
        if engine == "edge":
            tts_edge(text, voice, path, cfg.get("rate", "+0%"))
        elif engine == "gemini":
            tts_gemini(text, voice, path, cfg.get("gemini_model", "gemini-2.5-flash-preview-tts"),
                       cfg.get("style", ""), cfg.get("gemini_min_interval", 6.5))
        else:
            raise ValueError(f"unknown tts engine {engine}")
    return _to_pcm(path)

# ----------------------------------------------------------------- render
def render(script_path, out_path, tts=None, voice=None, only=None, workdir="build", cache_dir="tts_cache"):
    """only: list of scene indexes to (re)render; the rest are reused from workdir.
    cache_dir: where narration clips are kept (put it on Drive to reuse them between runs)."""
    spec = json.load(open(script_path, encoding="utf-8"))
    meta = spec["meta"]
    if tts: meta["tts"] = tts
    if voice: meta["voice"] = voice
    os.makedirs(workdir, exist_ok=True)

    # 1. narration and timing
    plan = []
    for si, sc in enumerate(spec["scenes"]):
        t, starts, pcm = HEAD, [], bytearray(b"\x00\x00" * int(HEAD * SR))
        for b in sc["beats"]:
            clip = narrate(b.get("say", ""), meta, cache_dir)
            starts.append(t)
            pcm += clip + b"\x00\x00" * int(GAP * SR)
            t += len(clip) / 2 / SR + GAP
        t += TAIL
        frames = int(round(t * FPS))
        pcm += b"\x00\x00" * int(TAIL * SR)
        need = int(frames / FPS * SR) * 2          # audio exactly as long as video
        pcm = pcm[:need] + b"\x00" * max(0, need - len(pcm))
        plan.append((sc, starts, frames, bytes(pcm)))
        print(f"scene {si:02d} {sc['type']:<9} {frames / FPS:6.1f}s")
    total = sum(p[2] for p in plan)
    print(f"total {total / FPS / 60:.1f} min")

    # 2. pictures, one mp4 per scene
    prev_last, done = None, 0
    files = []
    for si, (sc, starts, frames, _) in enumerate(plan):
        fn = os.path.join(workdir, f"scene_{si:02d}.mp4")
        files.append(fn)
        scene = SCENES[sc["type"]](sc, meta)
        scene.schedule(starts)
        if only is not None and si not in only and os.path.exists(fn):
            prev_last = scene.draw(frames / FPS); done += frames
            continue
        tmp = fn[:-4] + ".tmp.mp4"
        p = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24",
                              "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-c:v", "libx264",
                              "-preset", "veryfast", "-crf", "18", "-pix_fmt", "yuv420p", tmp],
                             stdin=subprocess.PIPE)
        cache_key, cache_img = object(), None
        xf = int(XFADE * FPS) if prev_last is not None else 0
        for fi in range(frames):
            t = fi / FPS
            k = scene.state_key(t)
            if k is None or k != cache_key:
                cache_img = scene.draw(t); cache_key = k if k is not None else object()
            if fi < xf:
                img = Image.blend(prev_last, cache_img, ease((fi + 1) / xf))
            else:
                img = cache_img.copy()
            # progress bar through the whole video
            dd = ImageDraw.Draw(img)
            dd.rectangle([0, H - 8, int(W * (done + fi) / total), H], fill=AMBER)
            p.stdin.write(img.tobytes())
        p.stdin.close(); p.wait()
        if p.returncode != 0:
            raise RuntimeError(f"ffmpeg failed on scene {si}")
        os.replace(tmp, fn)
        prev_last = cache_img
        done += frames
        print(f"  rendered scene {si:02d}")

    # 3. join pictures, add sound
    lst = os.path.join(workdir, "list.txt")
    with open(lst, "w") as f:
        for fn in files: f.write(f"file '{os.path.abspath(fn)}'\n")
    raw = os.path.join(workdir, "audio.pcm")
    with open(raw, "wb") as f:
        for _, _, _, pcm in plan: f.write(pcm)
    silent = os.path.join(workdir, "video_only.mp4")
    if os.path.dirname(out_path):
        os.makedirs(os.path.dirname(out_path), exist_ok=True)
    _run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", lst, "-c", "copy", silent])
    _run(["ffmpeg", "-v", "error", "-y", "-i", silent, "-f", "s16le", "-ar", str(SR), "-ac", "1",
          "-i", raw, "-map", "0:v", "-map", "1:a", "-c:v", "copy", "-c:a", "aac", "-b:a", "160k",
          "-shortest", "-movflags", "+faststart", out_path])
    print("done ->", out_path)
    return out_path

def still(script_path, scene_index, t=None, out="frame.png"):
    """Quick look at one scene without rendering video (t defaults to end of scene)."""
    spec = json.load(open(script_path, encoding="utf-8"))
    sc = spec["scenes"][scene_index]
    meta = dict(spec["meta"], tts="none")
    starts, tt = [], HEAD
    for b in sc["beats"]:
        starts.append(tt); tt += len(narrate(b.get("say", ""), meta)) / 2 / SR + GAP
    scene = SCENES[sc["type"]](sc, spec["meta"]); scene.schedule(starts)
    scene.draw(tt + 5 if t is None else t).save(out)
    return out

