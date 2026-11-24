"""Additional scene layouts: steps, cycle, quad, vpc, template, stats, table, list."""
import math
from PIL import Image, ImageDraw
from .engine import (Scene, W, H, NAVY, AMBER, CREAM, DARK_AMBER, INK, WHITE, LAVENDER,
                     MUTED, PAPER, RULE, font, ease, mix, wrap, text_block, text_height)


def fit_font(text, style, maxw, maxh, big, small=20, lh=1.28):
    """Largest font size (big..small) whose wrapped text fits in maxw x maxh."""
    for size in range(big, small - 1, -1):
        f = font(style, size)
        if text_height(text, f, maxw, lh) <= maxh and \
                all(f.getlength(line) <= maxw for line in wrap(text, f, maxw)):
            return f
    return font(style, small)


def card(d, box, fill, a, bg, radius=18):
    x0, y0, x1, y1 = box
    fl = mix(fill, bg, a)
    d.rounded_rectangle([x0, y0, x1, y1], radius=radius, fill=fl)
    return fl


def num_badge(d, cx, cy, r, label, a, bg, fill=AMBER, color=WHITE, size=None):
    fl = mix(fill, bg, a)
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=fl)
    f = font("bold", size or int(r * 0.95))
    d.text((cx - f.getlength(label) / 2, cy - f.size * 0.58), label, font=f, fill=mix(color, fl, a))


class _Content(Scene):
    """Light scene with header, footer and an optional banner at the bottom."""

    def top(self):
        return 300 if len(wrap(self.s.get("title", ""), font("bold", 58), 1740)) <= 1 else 370

    def bottom(self):
        return 840 if self.s.get("banner") else 990

    def banner(self, d, t, bg):
        if not self.s.get("banner"):
            return
        a = self.a("banner", t)
        if a <= 0:
            return
        f = fit_font(self.s["banner"], "bold", 1660, 84, 31, 22, 1.2)
        bh = text_height(self.s["banner"], f, 1660, 1.2) + 46
        y = 870 + (100 - bh) / 2 + (1 - a) * 16
        fl = card(d, (90, y, 1830, y + bh), AMBER, a, bg, 14)
        text_block(d, (124, y + 23), self.s["banner"], f, NAVY, 1660, fl, a, lh=1.2)

    def frame(self, t):
        im, d, bg = self.base()
        self.header(d, t, bg)
        return im, d, bg

    def finish(self, d, t, bg):
        self.banner(d, t, bg)
        self.footer(d, bg)


class StepsScene(_Content):
    """A process: 2-8 numbered steps, in one row (<=5) or two rows."""

    def element_ids(self):
        n = len(self.s["steps"])
        return ["_header"] + [f"s{i}" for i in range(n)] + (["banner"] if self.s.get("banner") else [])

    def draw(self, t):
        im, d, bg = self.frame(t)
        steps = self.s["steps"]
        n = len(steps)
        rows = 1 if n <= 5 else 2
        per = math.ceil(n / rows)
        gap = 28
        top, bot = self.top(), self.bottom()
        cw = (1740 - gap * (per - 1)) / per
        rh = (bot - top - (rows - 1) * 30) / rows
        if rows == 1 and rh > 430:
            top += (rh - 430) / 2
            rh = 430
        for i, st in enumerate(steps):
            r, c = divmod(i, per)
            x = 90 + c * (cw + gap)
            y = top + r * (rh + 30)
            a = self.a(f"s{i}", t)
            # connector line behind the badges
            if c < per - 1 and i + 1 < n:
                a2 = self.a(f"s{i + 1}", t)
                if a2 > 0:
                    d.line([x + 64, y + 40, x + 64 + (cw + gap) * a2, y + 40], fill=mix(AMBER, bg, a2), width=4)
            if a <= 0:
                continue
            oy = (1 - a) * 18
            fl = card(d, (x, y + 40 + oy, x + cw, y + rh + oy), CREAM, a, bg)
            num_badge(d, x + 64, y + 40 + oy, 34, st.get("num", str(i + 1)), a, bg, size=30)
            yy = y + 98 + oy
            if st.get("tag"):
                d.text((x + 30, yy), st["tag"], font=font("bold", 20), fill=mix(DARK_AMBER, fl, a))
                yy += 34
            big = (34 if rows == 1 else 30) if st.get("text") else 40
            ft = fit_font(st["title"], "bold", cw - 60, 90 if st.get("text") else rh - 130, big, 20, 1.12)
            yy += text_block(d, (x + 30, yy), st["title"], ft, NAVY, cw - 60, fl, a, lh=1.12) + 10
            if st.get("text"):
                room = y + rh + oy - 24 - yy
                fx = fit_font(st["text"], "regular", cw - 60, room, 30 if rows == 1 else 26, 18)
                text_block(d, (x + 30, yy), st["text"], fx, INK, cw - 60, fl, a)
        self.finish(d, t, bg)
        return im


class CycleScene(_Content):
    """A loop (3-6 nodes) drawn as a circle, with descriptions on the right."""

    def element_ids(self):
        n = len(self.s["nodes"])
        return ["_header", "center"] + [f"n{i}" for i in range(n)] + (["banner"] if self.s.get("banner") else [])

    def draw(self, t):
        im, d, bg = self.frame(t)
        nodes = self.s["nodes"]
        n = len(nodes)
        top, bot = self.top(), self.bottom()
        cy = (top + bot) / 2 + 10
        R = min(250, (bot - top) / 2 - 70)
        cx = 120 + R + 90
        ang = [(-90 + 360 * i / n) for i in range(n)]
        pts = [(cx + R * math.cos(math.radians(g)), cy + R * math.sin(math.radians(g))) for g in ang]
        d.ellipse([cx - R, cy - R, cx + R, cy + R], outline=LAVENDER, width=6)
        # arrowheads half-way between nodes, for revealed arcs
        for i in range(n):
            a = self.a(f"n{(i + 1) % n}", t) if i + 1 < n else self.a(f"n{n - 1}", t)
            if a <= 0:
                continue
            gm = math.radians(ang[i] + 180 / n)
            mx, my = cx + R * math.cos(gm), cy + R * math.sin(gm)
            tx, ty = -math.sin(gm), math.cos(gm)       # tangent, clockwise
            nx, ny = math.cos(gm), math.sin(gm)
            s = 18
            tip = (mx + tx * s, my + ty * s)
            d.polygon([tip, (mx - tx * s + nx * s, my - ty * s + ny * s), (mx - tx * s - nx * s, my - ty * s - ny * s)],
                      fill=mix(DARK_AMBER, bg, a))
        ac = self.a("center", t)
        if self.s.get("center") and ac > 0:
            fc = fit_font(self.s["center"], "bold", R * 1.1, R * 0.9, 34, 20, 1.15)
            hh = text_height(self.s["center"], fc, R * 1.1, 1.15)
            text_block(d, (cx, cy - hh / 2), self.s["center"], fc, INK, R * 1.1, bg, ac, lh=1.15, anchor_x="c")
        nr = 92 if n <= 4 else 78
        for i, (px, py) in enumerate(pts):
            a = self.a(f"n{i}", t)
            if a <= 0:
                continue
            fill = AMBER if i % 2 == 0 else NAVY
            col = NAVY if i % 2 == 0 else WHITE
            fl = mix(fill, bg, a)
            d.ellipse([px - nr, py - nr, px + nr, py + nr], fill=fl, outline=WHITE, width=6)
            ft = fit_font(nodes[i]["title"], "bold", nr * 1.6, nr * 1.2, 30, 16, 1.1)
            hh = text_height(nodes[i]["title"], ft, nr * 1.6, 1.1)
            text_block(d, (px, py - hh / 2 - 3), nodes[i]["title"], ft, col, nr * 1.6, fl, a, lh=1.1, anchor_x="c")
        # descriptions
        X, Rr = 980, 1830
        slot = (bot - top) / n
        for i, nd in enumerate(nodes):
            a = self.a(f"n{i}", t)
            if a <= 0:
                continue
            y = top + i * slot + (1 - a) * 14
            num_badge(d, X + 24, y + 26, 24, str(i + 1), a, bg, fill=AMBER if i % 2 == 0 else NAVY,
                      color=NAVY if i % 2 == 0 else WHITE, size=22)
            ft = font("bold", 32)
            d.text((X + 66, y + 6), nd["title"], font=ft, fill=mix(NAVY, bg, a))
            if nd.get("text"):
                fx = fit_font(nd["text"], "regular", Rr - X - 66, slot - 62, 28, 18)
                text_block(d, (X + 66, y + 52), nd["text"], fx, INK, Rr - X - 66, bg, a)
        self.finish(d, t, bg)
        return im


def _rotated_text(text, f, color, bg):
    w = int(f.getlength(text)) + 8
    im = Image.new("RGB", (w, f.size + 12), bg)
    ImageDraw.Draw(im).text((4, 2), text, font=f, fill=color)
    return im.rotate(90, expand=True)


class QuadScene(_Content):
    """2x2 matrix. Optional x_axis / y_axis labels, a highlighted quadrant and a centre label.
    Quadrant order: top-left, top-right, bottom-left, bottom-right."""

    def element_ids(self):
        return ["_header", "axes", "center"] + [f"q{i}" for i in range(4)] + \
               (["banner"] if self.s.get("banner") else [])

    def draw(self, t):
        im, d, bg = self.frame(t)
        top, bot = self.top(), self.bottom()
        has_y, has_x = bool(self.s.get("y_axis")), bool(self.s.get("x_axis"))
        x0 = 170 if has_y else 90
        y1 = bot - (50 if has_x else 0)
        gap = 22
        gw = (1830 - x0 - gap) / 2
        gh = (y1 - top - gap) / 2
        aa = self.a("axes", t)
        if has_y and aa > 0:
            col = mix(MUTED, bg, aa)
            d.line([120, y1, 120, top + 10], fill=col, width=3)
            d.polygon([(120, top), (110, top + 20), (130, top + 20)], fill=col)
            rt = _rotated_text(self.s["y_axis"].upper(), font("bold", 20), col, bg)
            im.paste(rt, (82, int((top + y1) / 2 - rt.height / 2)))
        if has_x and aa > 0:
            col = mix(MUTED, bg, aa)
            d.line([x0, y1 + 26, 1820, y1 + 26], fill=col, width=3)
            d.polygon([(1830, y1 + 26), (1810, y1 + 16), (1810, y1 + 36)], fill=col)
            f = font("bold", 20)
            lbl = self.s["x_axis"].upper()
            d.rectangle([(x0 + 1830) / 2 - f.getlength(lbl) / 2 - 12, y1 + 14,
                         (x0 + 1830) / 2 + f.getlength(lbl) / 2 + 12, y1 + 40], fill=bg)
            d.text(((x0 + 1830) / 2 - f.getlength(lbl) / 2, y1 + 15), lbl, font=f, fill=col)
        hl = self.s.get("highlight")
        for i, q in enumerate(self.s["quads"][:4]):
            a = self.a(f"q{i}", t)
            if a <= 0:
                continue
            r, c = divmod(i, 2)
            x_card = x0 + c * (gw + gap)
            y = top + r * (gh + gap) + (1 - a) * 14
            fill = AMBER if hl == i else CREAM
            fl = card(d, (x_card, y, x_card + gw, y + gh), fill, a, bg, 16)
            cut = 110 if self.s.get("center") else 0
            x = x_card + (cut if c == 1 else 0)
            gw_c = gw - cut
            yy = y + 26
            if q.get("tag"):
                tf = font("bold", 46)
                d.text((x + 30, yy - 6), q["tag"], font=tf, fill=mix(DARK_AMBER if hl != i else NAVY, fl, a))
                tx = x + 30 + tf.getlength(q["tag"]) + 20
            else:
                tx = x + 30
            ft = fit_font(q["title"], "bold", x + gw_c - 30 - tx, 80, 34, 22, 1.12)
            hh = text_block(d, (tx, yy), q["title"], ft, NAVY, x + gw_c - 30 - tx, fl, a, lh=1.12)
            yy += max(hh, 50) + 12
            body = q.get("text", "")
            if q.get("items"):
                body = "\n".join("•  " + it for it in q["items"])
            if body:
                room = y + gh - 20 - yy
                fx = fit_font(body, "regular", gw_c - 60, room, 30, 17)
                text_block(d, (x + 30, yy), body, fx, INK if hl != i else NAVY, gw_c - 60, fl, a)
        ac = self.a("center", t)
        if self.s.get("center") and ac > 0:
            cx, cy = x0 + gw + gap / 2, top + gh + gap / 2
            r = 88
            fl = mix(NAVY, bg, ac)
            d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=fl, outline=WHITE, width=8)
            fc = fit_font(self.s["center"], "bold", r * 1.5, r * 1.2, 28, 16, 1.1)
            hh = text_height(self.s["center"], fc, r * 1.5, 1.1)
            text_block(d, (cx, cy - hh / 2 - 2), self.s["center"], fc, WHITE, r * 1.5, fl, ac, lh=1.1, anchor_x="c")
        self.finish(d, t, bg)
        return im


class VPCScene(_Content):
    """Value Proposition Canvas: value map (square) and customer profile (circle)."""
    SQ = ["products", "gain_creators", "pain_relievers"]
    CI = ["jobs", "gains", "pains"]
    NAMES = {"products": "Products & services", "gain_creators": "Gain creators",
             "pain_relievers": "Pain relievers", "jobs": "Customer jobs", "gains": "Gains", "pains": "Pains"}

    def element_ids(self):
        return ["_header", "shape", "fit"] + self.SQ + self.CI + (["banner"] if self.s.get("banner") else [])

    def _seg(self, d, key, cx, cy, w, t, bg, fill_on):
        a = self.a(key, t)
        if a <= 0:
            return
        items = self.s.get("items", {}).get(key, [])
        name = self.s.get("names", {}).get(key, self.NAMES[key])
        f = font("bold", 30)
        body = "\n".join(items)
        fb = fit_font(body, "regular", w, 0.28 * self._size, 26, 16, 1.2) if body else None
        hb = text_height(body, fb, w, 1.2) if body else 0
        hh = text_height(name, f, w, 1.1)
        y = cy - (hh + 8 + hb) / 2 + (1 - a) * 10
        text_block(d, (cx, y), name, f, NAVY, w, fill_on, a, lh=1.1, anchor_x="c")
        if body:
            text_block(d, (cx, y + hh + 8), body, fb, INK, w, fill_on, a, lh=1.2, anchor_x="c")

    def draw(self, t):
        im, d, bg = self.frame(t)
        top, bot = self.top(), self.bottom()
        self._size = min(620, bot - top - 60)
        size = min(620, bot - top - 60)
        sy = top + 40 + (bot - top - 40 - size) / 2
        sx = 120
        R = size / 2 + 30
        cx, cyy = 1810 - R, sy + size / 2
        a0 = self.a("shape", t)
        lf = font("bold", 22)
        d.text((sx, cyy - R - 36), "VALUE MAP", font=lf, fill=mix(DARK_AMBER, bg, a0))
        d.text((cx - R, cyy - R - 36), "CUSTOMER PROFILE", font=lf, fill=mix(DARK_AMBER, bg, a0))
        # square: products (left half), gain creators (top right), pain relievers (bottom right)
        boxes = {"products": (sx, sy, sx + size / 2, sy + size),
                 "gain_creators": (sx + size / 2, sy, sx + size, sy + size / 2),
                 "pain_relievers": (sx + size / 2, sy + size / 2, sx + size, sy + size)}
        for k, (x0, y0, x1, y1) in boxes.items():
            a = self.a(k, t)
            d.rectangle([x0, y0, x1, y1], fill=mix(CREAM, bg, a), outline=mix(NAVY, bg, a0), width=4)
        # circle: jobs (right third), pains (bottom left), gains (top left)
        wedges = {"jobs": (-60, 60), "pains": (60, 180), "gains": (180, 300)}
        for k, (g0, g1) in wedges.items():
            a = self.a(k, t)
            d.pieslice([cx - R, cyy - R, cx + R, cyy + R], g0, g1, fill=mix(CREAM, bg, a),
                       outline=mix(NAVY, bg, a0), width=4)
        for k in self.SQ:
            x0, y0, x1, y1 = boxes[k]
            self._seg(d, k, (x0 + x1) / 2, (y0 + y1) / 2, x1 - x0 - 30, t, bg, CREAM)
        for k, (g0, g1) in wedges.items():
            gm = math.radians((g0 + g1) / 2)
            rr = 0.52 * R
            self._seg(d, k, cx + rr * math.cos(gm), cyy + rr * math.sin(gm), R * 0.72, t, bg, CREAM)
        af = self.a("fit", t)
        if af > 0:
            x0, x1, y = sx + size + 50, cx - R - 50, cyy
            col = mix(AMBER, bg, af)
            for yy, flip in [(y - 22, False), (y + 22, True)]:
                d.line([x0, yy, x1, yy], fill=col, width=8)
                if not flip:
                    d.polygon([(x1 + 14, yy), (x1 - 12, yy - 18), (x1 - 12, yy + 18)], fill=col)
                else:
                    d.polygon([(x0 - 14, yy), (x0 + 12, yy - 18), (x0 + 12, yy + 18)], fill=col)
            f = font("bold", 30)
            lbl = self.s.get("fit_label", "FIT")
            d.text(((x0 + x1) / 2 - f.getlength(lbl) / 2, y - 80), lbl, font=f, fill=mix(DARK_AMBER, bg, af))
        self.finish(d, t, bg)
        return im


class TemplateScene(_Content):
    """Fill-in templates (POV, test card, user story...): 1 or 2 cards of lead/fill rows,
    plus an optional example."""

    def element_ids(self):
        ids = ["_header"] + [f"card{i}" for i in range(len(self.s["cards"]))]
        return ids + (["example"] if self.s.get("example") else []) + (["banner"] if self.s.get("banner") else [])

    def schedule(self, starts):
        super().schedule(starts)
        for i, c in enumerate(self.s["cards"]):
            for j in range(len(c["rows"])):
                self.reveal[f"card{i}_r{j}"] = self.reveal[f"card{i}"] + 0.25 * j

    def draw(self, t):
        im, d, bg = self.frame(t)
        top, bot = self.top(), self.bottom()
        cards = self.s["cards"]
        n = len(cards)
        ex_h = 0
        if self.s.get("example"):
            ex_h = text_height(self.s["example"], font("regular", 28), 1660) + 80
        avail = bot - top - (ex_h + 24 if ex_h else 0)
        gap = 36
        cw = (1740 - gap * (n - 1)) / n
        for i, c in enumerate(cards):
            a = self.a(f"card{i}", t)
            if a <= 0:
                continue
            x = 90 + i * (cw + gap)
            rows = c["rows"]
            wide = n == 1
            fl = card(d, (x, top, x + cw, top + avail), CREAM if not c.get("dark") else NAVY, a, bg)
            hc = DARK_AMBER if not c.get("dark") else AMBER
            tc = NAVY if not c.get("dark") else WHITE
            yy = top + 28
            if c.get("head"):
                d.text((x + 36, yy), c["head"].upper(), font=font("bold", 22), fill=mix(hc, fl, a))
                yy += 50
            slot = (top + avail - 24 - yy) / len(rows)
            for j, r in enumerate(rows):
                ar = self.a(f"card{i}_r{j}", t)
                if ar <= 0:
                    continue
                y = yy + j * slot + (1 - ar) * 10
                if wide:
                    fl_ = font("bold", 30)
                    d.text((x + 36, y + 6), r["lead"].upper(), font=fl_, fill=mix(hc, fl, ar))
                    ff = fit_font(r.get("fill", ""), "regular", cw - 520, slot - 10, 38, 22, 1.2)
                    text_block(d, (x + 480, y), r.get("fill", ""), ff, tc, cw - 520, fl, ar, lh=1.2)
                    if j < len(rows) - 1:
                        d.line([x + 36, y + slot - 8, x + cw - 36, y + slot - 8], fill=mix(RULE, fl, ar), width=2)
                else:
                    fl_ = font("bold", 26)
                    d.text((x + 36, y), r["lead"], font=fl_, fill=mix(hc, fl, ar))
                    ff = fit_font(r.get("fill", ""), "regular", cw - 72, slot - 50, 30, 18, 1.2)
                    text_block(d, (x + 36, y + 38), r.get("fill", ""), ff, tc, cw - 72, fl, ar, lh=1.2)
        if self.s.get("example"):
            a = self.a("example", t)
            if a > 0:
                y = top + avail + 24 + (1 - a) * 14
                fl = card(d, (90, y, 1830, y + ex_h), NAVY, a, bg, 14)
                d.text((124, y + 18), self.s.get("example_label", "EXAMPLE"), font=font("bold", 20), fill=mix(AMBER, fl, a))
                text_block(d, (124, y + 52), self.s["example"], font("regular", 28), WHITE, 1660, fl, a, lh=1.25)
        self.finish(d, t, bg)
        return im


class StatsScene(_Content):
    """2-4 big numbers with a label each, and an optional note."""

    def element_ids(self):
        return ["_header"] + [f"st{i}" for i in range(len(self.s["stats"]))] + \
               (["banner"] if self.s.get("banner") else [])

    def draw(self, t):
        im, d, bg = self.frame(t)
        top, bot = self.top(), self.bottom()
        st = self.s["stats"]
        n = len(st)
        gap = 36
        cw = (1740 - gap * (n - 1)) / n
        ch = min(440, bot - top - 20)
        y0 = top + (bot - top - ch) / 2
        for i, s_ in enumerate(st):
            a = self.a(f"st{i}", t)
            if a <= 0:
                continue
            x = 90 + i * (cw + gap)
            y = y0 + (1 - a) * 18
            hl = s_.get("highlight")
            fl = card(d, (x, y, x + cw, y + ch), NAVY if hl else CREAM, a, bg)
            vc = AMBER if hl else DARK_AMBER
            size = 120
            while size > 40 and font("bold", size).getlength(s_["value"]) > cw - 70:
                size -= 4
            fv = font("bold", size)
            d.text((x + 36, y + 50), s_["value"], font=fv, fill=mix(vc, fl, a))
            d.rectangle([x + 38, y + 70 + size, x + 118, y + 76 + size], fill=mix(AMBER, fl, a))
            fx = fit_font(s_["label"], "regular", cw - 72, ch - size - 130, 32, 20)
            text_block(d, (x + 36, y + 100 + size), s_["label"], fx, WHITE if hl else INK, cw - 72, fl, a)
        self.finish(d, t, bg)
        return im


class TableScene(_Content):
    """Comparison table. headers: 2 or 3 column titles; rows: lists of cells."""

    def element_ids(self):
        return ["_header"] + [f"r{i}" for i in range(len(self.s["rows"]))] + \
               (["banner"] if self.s.get("banner") else [])

    def draw(self, t):
        im, d, bg = self.frame(t)
        top, bot = self.top(), self.bottom()
        heads = self.s["headers"]
        rows = self.s["rows"]
        nc = len(heads)
        widths = [400, 670, 670] if nc == 3 else [870, 870]
        xs = [90]
        for w_ in widths[:-1]:
            xs.append(xs[-1] + w_)
        hh = 76
        a = self.a("_header", t)
        head_fill = [PAPER, NAVY, AMBER] if nc == 3 else [NAVY, AMBER]
        head_col = [MUTED, WHITE, NAVY] if nc == 3 else [WHITE, NAVY]
        for c in range(nc):
            if not heads[c]:
                continue
            fl = mix(head_fill[c], bg, a)
            d.rounded_rectangle([xs[c] + 4, top, xs[c] + widths[c] - 4, top + hh], radius=12, fill=fl)
            fh = fit_font(heads[c], "bold", widths[c] - 50, hh - 20, 28, 18, 1.1)
            text_block(d, (xs[c] + 26, top + (hh - text_height(heads[c], fh, widths[c] - 50, 1.1)) / 2),
                       heads[c], fh, head_col[c], widths[c] - 50, fl, a, lh=1.1)
        rh = (bot - top - hh - 16) / len(rows)
        for i, row in enumerate(rows):
            ar = self.a(f"r{i}", t)
            if ar <= 0:
                continue
            y = top + hh + 12 + i * rh + (1 - ar) * 10
            fl = mix(CREAM if i % 2 == 0 else WHITE, bg, ar)
            d.rounded_rectangle([90, y, 1830, y + rh - 6], radius=10, fill=fl)
            for c in range(nc):
                bold = nc == 3 and c == 0
                fc = fit_font(row[c], "bold" if bold else "regular", widths[c] - 50, rh - 22,
                              30 if not bold else 27, 17, 1.2)
                th = text_height(row[c], fc, widths[c] - 50, 1.2)
                text_block(d, (xs[c] + 26, y + (rh - 6 - th) / 2), row[c], fc,
                           DARK_AMBER if bold else NAVY, widths[c] - 50, fl, ar, lh=1.2)
        self.finish(d, t, bg)
        return im


class ListScene(_Content):
    """Up to 10 items (title + optional text) in one or two columns."""

    def element_ids(self):
        return ["_header"] + [f"i{i}" for i in range(len(self.s["items"]))] + \
               (["banner"] if self.s.get("banner") else [])

    def draw(self, t):
        im, d, bg = self.frame(t)
        top, bot = self.top(), self.bottom()
        items = self.s["items"]
        n = len(items)
        cols = 1 if n <= 4 else 2
        per = math.ceil(n / cols)
        gap = 30
        cw = (1740 - gap * (cols - 1)) / cols
        rh = (bot - top - 14 * (per - 1)) / per
        for i, it in enumerate(items):
            a = self.a(f"i{i}", t)
            if a <= 0:
                continue
            c, r = divmod(i, per)
            x = 90 + c * (cw + gap)
            y = top + r * (rh + 14) + (1 - a) * 12
            fl = card(d, (x, y, x + cw, y + rh), CREAM, a, bg, 14)
            br = min(26, rh / 2 - 8)
            if self.s.get("style", "number") == "number":
                num_badge(d, x + 22 + br, y + rh / 2, br, str(i + 1), a, bg, size=int(br * 0.9))
            else:
                cx_, cy_ = x + 22 + br, y + rh / 2
                d.ellipse([cx_ - br, cy_ - br, cx_ + br, cy_ + br], fill=mix(AMBER, bg, a))
                k = br * 0.45
                d.line([(cx_ - k, cy_), (cx_ - k * 0.25, cy_ + k * 0.75), (cx_ + k, cy_ - k * 0.6)],
                       fill=mix(WHITE, mix(AMBER, bg, a), a), width=max(3, int(br / 6)), joint="curve")
            tx = x + 44 + 2 * br
            title, body = it["title"], it.get("text", "")
            if body and cols == 2:
                ft = fit_font(title, "bold", cw - (tx - x) - 24, rh * 0.42, 29, 18, 1.1)
                th = text_height(title, ft, cw - (tx - x) - 24, 1.1)
                fb = fit_font(body, "regular", cw - (tx - x) - 24, rh - th - 26, 25, 16, 1.2)
                bh = text_height(body, fb, cw - (tx - x) - 24, 1.2)
                yy = y + (rh - th - bh - 6) / 2
                text_block(d, (tx, yy), title, ft, NAVY, cw - (tx - x) - 24, fl, a, lh=1.1)
                text_block(d, (tx, yy + th + 6), body, fb, INK, cw - (tx - x) - 24, fl, a, lh=1.2)
            elif body:
                tw = 560
                ft = fit_font(title, "bold", tw - 30, rh - 20, 32, 18, 1.1)
                th = text_height(title, ft, tw - 30, 1.1)
                text_block(d, (tx, y + (rh - th) / 2), title, ft, NAVY, tw - 30, fl, a, lh=1.1)
                fb = fit_font(body, "regular", cw - (tx - x) - tw - 24, rh - 20, 29, 17, 1.2)
                bh = text_height(body, fb, cw - (tx - x) - tw - 24, 1.2)
                text_block(d, (tx + tw, y + (rh - bh) / 2), body, fb, INK, cw - (tx - x) - tw - 24, fl, a, lh=1.2)
            else:
                ft = fit_font(title, "bold", cw - (tx - x) - 24, rh - 20, 32, 18, 1.15)
                th = text_height(title, ft, cw - (tx - x) - 24, 1.15)
                text_block(d, (tx, y + (rh - th) / 2), title, ft, NAVY, cw - (tx - x) - 24, fl, a, lh=1.15)
        self.finish(d, t, bg)
        return im


EXTRA_SCENES = {"steps": StepsScene, "cycle": CycleScene, "quad": QuadScene, "vpc": VPCScene,
                "template": TemplateScene, "stats": StatsScene, "table": TableScene, "list": ListScene}
