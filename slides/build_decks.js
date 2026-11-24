// Builds the course decks in the house format (navy + session accent, Arial, 16:9).
//   node slides/build_decks.js            -> slides/*.pptx
// Deck content lives in slides/decks.js.
const path = require("path");
const pptxgen = require("pptxgenjs");
const DECKS = require("./decks.js");

const NAVY = "1F1A3D", INK = "4A4566", LAV = "D9D6EC", MUTED = "B9B4D6", WHITE = "FFFFFF", PAPER = "F6F5FA";
const COURSE = "Designing Innovative Products &amp; Business";   // escaped: written raw into the layout XML
const COURSE_TXT = "Designing Innovative Products & Business";

function build(deck) {
  const A = deck.accent;               // {main, dark, light}
  const pres = new pptxgen();
  pres.layout = "LAYOUT_16x9";         // 10 x 5.625 in
  pres.author = "Jordi Cusidó Roura";
  pres.title = deck.title;
  pres.theme = { headFontFace: "Arial", bodyFontFace: "Arial" };

  pres.defineSlideMaster({
    title: "COVER", background: { color: NAVY },
    objects: [
      { placeholder: { options: { name: "title", type: "title", x: 0.6, y: 1.75, w: 8.2, h: 1.3, fontSize: 44, bold: true,
        color: WHITE, fontFace: "Arial", valign: "bottom", align: "left", margin: 0 }, text: "" } },
      { placeholder: { options: { name: "body", type: "body", x: 0.6, y: 3.2, w: 7.6, h: 0.8, fontSize: 18,
        color: LAV, fontFace: "Arial", valign: "top", align: "left", margin: 0 }, text: "" } },
    ],
  });
  pres.defineSlideMaster({
    title: "SECTION", background: { color: NAVY },
    objects: [
      { placeholder: { options: { name: "title", type: "title", x: 3.3, y: 1.9, w: 6.2, h: 1.0, fontSize: 36, bold: true,
        color: WHITE, fontFace: "Arial", valign: "bottom", align: "left", margin: 0 }, text: "" } },
      { placeholder: { options: { name: "body", type: "body", x: 3.3, y: 3.0, w: 6.0, h: 0.9, fontSize: 16,
        color: LAV, fontFace: "Arial", valign: "top", align: "left", margin: 0 }, text: "" } },
    ],
    slideNumber: { x: 9.2, y: 5.2, w: 0.4, h: 0.3, fontSize: 9, color: MUTED, align: "right" },
  });
  pres.defineSlideMaster({
    title: "CONTENT", background: { color: WHITE },
    objects: [
      { placeholder: { options: { name: "title", type: "title", x: 0.5, y: 0.6, w: 9.0, h: 0.65, fontSize: 28, bold: true,
        color: NAVY, fontFace: "Arial", valign: "top", align: "left", margin: 0 }, text: "" } },
      { text: { text: `${COURSE_TXT}  ·  ${deck.footer}`, options: { x: 0.5, y: 5.2, w: 7.5, h: 0.3, fontSize: 9,
        color: MUTED, fontFace: "Arial", margin: 0, valign: "middle" } } },
    ],
    slideNumber: { x: 9.2, y: 5.2, w: 0.4, h: 0.3, fontSize: 9, color: MUTED, align: "right" },
  });

  const S = pres.shapes;
  const tx = (slide, text, o) => slide.addText(text, Object.assign({ isTextBox: true, margin: 0, fontFace: "Arial", valign: "top" }, o));
  const rrect = (slide, x, y, w, h, color, r = 0.08, name) =>
    slide.addShape(S.ROUNDED_RECTANGLE, { x, y, w, h, fill: { color }, line: { color, width: 1 }, rectRadius: r, objectName: name });

  function kicker(slide, text) {
    const t = text.toUpperCase();
    const w = Math.min(6.0, 0.088 * t.length + 0.5);
    slide.addText(t, { shape: S.ROUNDED_RECTANGLE, rectRadius: 0.13, x: 0.5, y: 0.25, w, h: 0.26, fill: { color: A.main },
      line: { color: A.main, width: 1 }, fontSize: 9, bold: true, color: NAVY, align: "center", valign: "middle",
      charSpacing: 1.5, margin: 0, fontFace: "Arial", objectName: "kicker" });
  }
  function callout(slide, text, y = 4.45, h = 0.5) {
    rrect(slide, 0.5, y, 9.0, h, A.main, 0.1, "callout");
    tx(slide, text, { x: 0.7, y, w: 8.6, h, fontSize: 13, bold: true, color: NAVY, valign: "middle" });
  }
  function content(sp, section) {
    const slide = pres.addSlide({ masterName: "CONTENT", sectionTitle: section });
    if (sp.kicker) kicker(slide, sp.kicker);
    slide.addText(sp.title, { placeholder: "title" });
    if (sp.notes) slide.addNotes(sp.notes);
    return slide;
  }
  // card row: [{num,title,text}], highlight index fills with accent
  function cardRow(slide, cards, y, h, opt = {}) {
    const n = cards.length, gap = 0.18, w = (9.0 - gap * (n - 1)) / n;
    cards.forEach((c, i) => {
      const x = 0.5 + i * (w + gap), hl = opt.highlight === i;
      rrect(slide, x, y, w, h, hl ? A.main : A.light, 0.08, "card");
      const num = c.num !== undefined ? c.num : String(i + 1).padStart(2, "0");
      const big = num.length <= 3;
      tx(slide, num, { x: x + 0.18, y: y + 0.14, w: w - 0.36, h: 0.48, fontSize: big ? 24 : 18, bold: true,
        color: hl ? NAVY : A.dark, valign: "middle" });
      tx(slide, c.title, { x: x + 0.18, y: y + 0.68, w: w - 0.36, h: 0.62, fontSize: 12.5, bold: true, color: NAVY });
      if (c.text) tx(slide, c.text, { x: x + 0.18, y: y + 1.3, w: w - 0.36, h: h - 1.42, fontSize: 11, color: hl ? NAVY : INK });
    });
  }

  const B = {
    cover(sp) {
      const s = pres.addSlide({ masterName: "COVER", sectionTitle: "Introduction" });
      s.addShape(S.OVAL, { x: 7.6, y: -1.2, w: 4.2, h: 4.2, fill: { color: A.main, transparency: 80 }, line: { color: A.main, transparency: 80 }, objectName: "deco" });
      s.addShape(S.OVAL, { x: 8.5, y: 3.4, w: 2.6, h: 2.6, fill: { color: A.main, transparency: 80 }, line: { color: A.main, transparency: 80 }, objectName: "deco" });
      s.addText(sp.label.toUpperCase(), { shape: S.ROUNDED_RECTANGLE, rectRadius: 0.16, x: 0.6, y: 1.2, w: 0.11 * sp.label.length + 0.6, h: 0.32,
        fill: { color: A.main }, line: { color: A.main, width: 1 }, fontSize: 11, bold: true, color: NAVY, align: "center",
        valign: "middle", charSpacing: 2, margin: 0, fontFace: "Arial", objectName: "kicker" });
      s.addText(sp.title, { placeholder: "title" });
      s.addText(sp.subtitle, { placeholder: "body" });
      tx(s, [{ text: "Jordi Cusidó Roura", options: { bold: true, breakLine: true } },
             { text: `${COURSE_TXT}  ·  ESEIAAT – UPC` }], { x: 0.6, y: 4.5, w: 7, h: 0.6, fontSize: 11, color: WHITE });
      if (sp.notes) s.addNotes(sp.notes);
    },
    section(sp) {
      const s = pres.addSlide({ masterName: "SECTION", sectionTitle: sp.title });
      tx(s, sp.num, { x: 0.4, y: 1.3, w: 2.8, h: 2.6, fontSize: 130, bold: true, color: A.main, align: "right", valign: "middle" });
      s.addText(sp.title, { placeholder: "title" });
      s.addText(sp.sub || "", { placeholder: "body" });
      if (sp.notes) s.addNotes(sp.notes);
      return sp.title;
    },
    agenda(sp, sec) {
      const s = content(sp, sec);
      cardRow(s, sp.items, 1.5, 3.1, { highlight: 0 });
    },
    cards(sp, sec) {
      const s = content(sp, sec);
      cardRow(s, sp.cards, 1.45, sp.callout ? 2.8 : 3.4);
      if (sp.callout) callout(s, sp.callout);
    },
    table(sp, sec) {
      const s = content(sp, sec);
      const nc = sp.headers.length;
      const colW = sp.colW || (nc === 3 ? [2.0, 3.5, 3.5] : [4.5, 4.5]);
      const head = sp.headers.map((h, i) => ({ text: h, options: { bold: true, fontSize: 12, color: i === nc - 1 ? NAVY : WHITE,
        fill: { color: i === nc - 1 ? A.main : (i === 0 && nc === 3 ? PAPER : NAVY) } } }));
      if (nc === 3 && !sp.headers[0]) head[0].options.fill = { color: WHITE };
      if (nc === 3 && sp.headers[0]) head[0].options.color = INK;
      const rows = sp.rows.map((r, ri) => r.map((c, ci) => ({ text: c, options: {
        fontSize: 11, color: nc === 3 && ci === 0 ? A.dark : NAVY, bold: nc === 3 && ci === 0,
        fill: { color: ri % 2 === 0 ? A.light : WHITE } } })));
      const y = 1.45, maxH = sp.callout ? 2.85 : 3.5;
      const rh = Math.min(0.55, maxH / (rows.length + 1));
      s.addTable([head, ...rows], { x: 0.5, y, w: 9.0, colW, rowH: rh, fontFace: "Arial", valign: "middle",
        margin: [0.04, 0.12, 0.04, 0.12], border: { type: "solid", color: WHITE, pt: 2 } });
      if (sp.callout) callout(s, sp.callout);
    },
    steps(sp, sec) {
      const s = content(sp, sec);
      const n = sp.steps.length, rows = n > 5 ? 2 : 1, per = Math.ceil(n / rows);
      const gap = 0.16, w = (9.0 - gap * (per - 1)) / per;
      const top = 1.45, avail = (sp.callout ? 4.3 : 4.95) - top;
      const rh = (avail - (rows - 1) * 0.15) / rows;
      sp.steps.forEach((st, i) => {
        const r = Math.floor(i / per), c = i % per;
        const x = 0.5 + c * (w + gap), y = top + r * (rh + 0.15);
        if (c < per - 1 && i + 1 < n)
          s.addShape(S.LINE, { x: x + 0.42, y: y + 0.2, w: w + gap, h: 0, line: { color: A.main, width: 2 } });
        rrect(s, x, y + 0.2, w, rh - 0.2, A.light, 0.08, "step");
        s.addText(String(i + 1), { shape: S.OVAL, x: x + 0.22, y: y, w: 0.4, h: 0.4, fill: { color: A.main },
          line: { color: WHITE, width: 1.5 }, fontSize: 12, bold: true, color: WHITE, align: "center", valign: "middle",
          margin: 0, fontFace: "Arial", objectName: "step-num" });
        let yy = y + 0.52;
        if (st.tag) { tx(s, st.tag, { x: x + 0.16, y: yy, w: w - 0.3, h: 0.22, fontSize: 9, bold: true, color: A.dark }); yy += 0.24; }
        tx(s, st.title, { x: x + 0.16, y: yy, w: w - 0.3, h: 0.5, fontSize: rows === 2 ? 11.5 : 12.5, bold: true, color: NAVY });
        if (st.text) tx(s, st.text, { x: x + 0.16, y: yy + 0.5, w: w - 0.3, h: y + rh - yy - 0.6, fontSize: rows === 2 ? 10 : 11, color: INK });
      });
      if (sp.callout) callout(s, sp.callout);
    },
    cycle(sp, sec) {
      const s = content(sp, sec);
      const n = sp.nodes.length, cx = 2.55, cy = 3.2, R = 1.35, nr = n > 4 ? 0.42 : 0.5;
      s.addShape(S.OVAL, { x: cx - R, y: cy - R, w: 2 * R, h: 2 * R, fill: { color: WHITE }, line: { color: LAV, width: 2.5 }, objectName: "loop" });
      tx(s, sp.center || "", { x: cx - 0.85, y: cy - 0.45, w: 1.7, h: 0.9, fontSize: 11, bold: true, color: INK, align: "center", valign: "middle" });
      sp.nodes.forEach((nd, i) => {
        const g = (-90 + 360 * i / n) * Math.PI / 180;
        const x = cx + R * Math.cos(g), y = cy + R * Math.sin(g), dark = i % 2 === 1;
        s.addText(nd.title, { shape: S.OVAL, x: x - nr, y: y - nr, w: 2 * nr, h: 2 * nr, fill: { color: dark ? NAVY : A.main },
          line: { color: WHITE, width: 2 }, fontSize: n > 4 ? 9.5 : 11, bold: true, color: dark ? WHITE : NAVY, align: "center",
          valign: "middle", margin: 0, fontFace: "Arial", objectName: "node" });
      });
      const X = 4.9, slot = 3.5 / n;
      sp.nodes.forEach((nd, i) => {
        const y = 1.5 + i * slot;
        s.addText(String(i + 1), { shape: S.OVAL, x: X, y: y + 0.02, w: 0.32, h: 0.32, fill: { color: i % 2 ? NAVY : A.main },
          line: { color: WHITE, width: 1 }, fontSize: 10, bold: true, color: i % 2 ? WHITE : NAVY, align: "center", valign: "middle", margin: 0, fontFace: "Arial" });
        tx(s, nd.title, { x: X + 0.45, y, w: 4.1, h: 0.3, fontSize: 12.5, bold: true, color: NAVY, valign: "middle" });
        tx(s, nd.text, { x: X + 0.45, y: y + 0.32, w: 4.1, h: slot - 0.38, fontSize: 11, color: INK });
      });
    },
    template(sp, sec) {
      const s = content(sp, sec);
      const n = sp.cards.length, gap = 0.2, w = (9.0 - gap * (n - 1)) / n;
      const top = 1.45, h = sp.example ? 2.25 : 3.4;
      sp.cards.forEach((c, i) => {
        const x = 0.5 + i * (w + gap), dark = !!c.dark;
        rrect(s, x, top, w, h, dark ? NAVY : A.light, 0.06, "template");
        tx(s, c.head.toUpperCase(), { x: x + 0.22, y: top + 0.15, w: w - 0.44, h: 0.25, fontSize: 9, bold: true, color: dark ? A.main : A.dark, charSpacing: 1.5 });
        const slot = (h - 0.55) / c.rows.length;
        c.rows.forEach((r, j) => {
          const y = top + 0.48 + j * slot;
          if (n === 1) {
            tx(s, r.lead.toUpperCase(), { x: x + 0.22, y, w: 2.4, h: slot, fontSize: 12, bold: true, color: A.dark, valign: "middle" });
            tx(s, r.fill, { x: x + 2.7, y, w: w - 2.95, h: slot, fontSize: 13, color: NAVY, valign: "middle" });
          } else {
            tx(s, r.lead, { x: x + 0.22, y, w: w - 0.44, h: 0.24, fontSize: 11, bold: true, color: dark ? A.main : A.dark });
            tx(s, r.fill, { x: x + 0.22, y: y + 0.24, w: w - 0.44, h: slot - 0.26, fontSize: 11, color: dark ? WHITE : NAVY });
          }
        });
      });
      if (sp.example) {
        const y = top + h + 0.2;
        rrect(s, 0.5, y, 9.0, 4.95 - y, PAPER, 0.06, "example");
        tx(s, (sp.exampleLabel || "Example").toUpperCase(), { x: 0.72, y: y + 0.12, w: 8.5, h: 0.22, fontSize: 9, bold: true, color: A.dark, charSpacing: 1.5 });
        tx(s, sp.example, { x: 0.72, y: y + 0.38, w: 8.56, h: 4.95 - y - 0.48, fontSize: 12, color: NAVY });
      }
    },
    rows(sp, sec) {   // emphasised list: bold lead + text, one per row
      const s = content(sp, sec);
      const n = sp.items.length, top = 1.45, bottom = sp.callout ? 4.3 : 4.95, gap = 0.1;
      const h = (bottom - top - gap * (n - 1)) / n;
      sp.items.forEach((it, i) => {
        const y = top + i * (h + gap);
        rrect(s, 0.5, y, 9.0, h, A.light, 0.08, "row");
        s.addText(sp.check ? "✓" : String(i + 1), { shape: S.OVAL, x: 0.68, y: y + h / 2 - 0.17, w: 0.34, h: 0.34, fill: { color: A.main },
          line: { color: A.main }, fontSize: 11, bold: true, color: sp.check ? WHITE : NAVY, align: "center", valign: "middle", margin: 0, fontFace: "Arial" });
        tx(s, it.title, { x: 1.2, y, w: it.text ? 3.3 : 8.1, h, fontSize: 13, bold: true, color: NAVY, valign: "middle" });
        if (it.text) tx(s, it.text, { x: 4.6, y, w: 4.7, h, fontSize: 12, color: INK, valign: "middle" });
      });
      if (sp.callout) callout(s, sp.callout);
    },
    stats(sp, sec) {
      const s = content(sp, sec);
      const n = sp.stats.length, gap = 0.2, w = (9.0 - gap * (n - 1)) / n, top = 1.5, h = sp.callout ? 2.7 : 3.3;
      sp.stats.forEach((st, i) => {
        const x = 0.5 + i * (w + gap), hl = !!st.highlight;
        rrect(s, x, top, w, h, hl ? NAVY : A.light, 0.08, "stat");
        tx(s, st.value, { x: x + 0.25, y: top + 0.3, w: w - 0.5, h: 1.0, fontSize: 44, bold: true, color: hl ? A.main : A.dark, valign: "middle" });
        tx(s, st.label, { x: x + 0.25, y: top + 1.45, w: w - 0.5, h: h - 1.6, fontSize: 13, color: hl ? WHITE : INK });
      });
      if (sp.callout) callout(s, sp.callout, 4.4);
    },
    quote(sp) {
      const s = pres.addSlide({ masterName: "SECTION", sectionTitle: sp.section });
      tx(s, "“", { x: 0.4, y: 1.1, w: 2.8, h: 2.6, fontSize: 160, bold: true, color: A.main, align: "right", valign: "middle" });
      s.addText(sp.text, { placeholder: "title", fontSize: 28 });
      s.addText(sp.by, { placeholder: "body" });
      if (sp.notes) s.addNotes(sp.notes);
    },
    board(sp, sec) {
      const s = content(sp, sec);
      const n = sp.columns.length, gap = 0.15, w = (9.0 - gap * (n - 1)) / n, top = 1.45, bottom = sp.callout ? 4.3 : 4.95;
      sp.columns.forEach((c, i) => {
        const x = 0.5 + i * (w + gap);
        rrect(s, x, top, w, bottom - top, c.highlight ? A.main : A.light, 0.06, "column");
        tx(s, c.name.toUpperCase(), { x: x + 0.15, y: top + 0.12, w: w - 0.9, h: 0.25, fontSize: 10, bold: true, color: NAVY, charSpacing: 1 });
        if (c.wip) s.addText(`WIP ${c.wip}`, { shape: S.ROUNDED_RECTANGLE, rectRadius: 0.1, x: x + w - 0.72, y: top + 0.1, w: 0.58, h: 0.24,
          fill: { color: NAVY }, line: { color: NAVY }, fontSize: 8, bold: true, color: WHITE, align: "center", valign: "middle", margin: 0, fontFace: "Arial" });
        (c.cards || []).forEach((cd, j) => {
          const y = top + 0.5 + j * 0.62;
          s.addShape(S.ROUNDED_RECTANGLE, { x: x + 0.12, y, w: w - 0.24, h: 0.52, fill: { color: WHITE }, line: { color: "E6E4EE", width: 1 },
            rectRadius: 0.06, shadow: { type: "outer", color: "000000", opacity: 0.12, blur: 3, offset: 1, angle: 90 }, objectName: "card" });
          tx(s, cd, { x: x + 0.22, y, w: w - 0.44, h: 0.52, fontSize: 10, bold: true, color: NAVY, valign: "middle" });
        });
      });
      if (sp.callout) callout(s, sp.callout);
    },
    images(sp, sec) {   // pictures on the left, numbered points on the right
      const s = content(sp, sec);
      const imgs = sp.images, top = 1.45;
      const ih = (3.5 - 0.15 * (imgs.length - 1)) / imgs.length;
      imgs.forEach((im, i) => {
        const y = top + i * (ih + 0.15);
        rrect(s, 0.5, y, 4.2, ih, PAPER, 0.04, "imgcard");
        s.addImage({ path: path.join(__dirname, im.path), x: 0.6, y: y + 0.08, w: 4.0, h: ih - 0.16,
          sizing: { type: "contain", w: 4.0, h: ih - 0.16 }, altText: im.alt });
      });
      const n = sp.points.length, slot = 3.5 / n;
      sp.points.forEach((p, i) => {
        const y = top + i * slot;
        tx(s, p.tag.toUpperCase(), { x: 5.0, y, w: 4.5, h: 0.22, fontSize: 9, bold: true, color: A.dark, charSpacing: 1.5 });
        tx(s, p.title, { x: 5.0, y: y + 0.24, w: 4.5, h: 0.3, fontSize: 12.5, bold: true, color: NAVY });
        tx(s, p.text, { x: 5.0, y: y + 0.54, w: 4.5, h: slot - 0.6, fontSize: 11, color: INK });
      });
    },
    closing(sp) {
      const s = pres.addSlide({ masterName: "COVER", sectionTitle: "Takeaway" });
      s.addShape(S.OVAL, { x: 7.6, y: -1.2, w: 4.2, h: 4.2, fill: { color: A.main, transparency: 80 }, line: { color: A.main, transparency: 80 }, objectName: "deco" });
      s.addText("TAKEAWAY", { shape: S.ROUNDED_RECTANGLE, rectRadius: 0.16, x: 0.6, y: 1.2, w: 1.5, h: 0.32, fill: { color: A.main },
        line: { color: A.main, width: 1 }, fontSize: 11, bold: true, color: NAVY, align: "center", valign: "middle", charSpacing: 2, margin: 0, fontFace: "Arial" });
      s.addText(sp.title, { placeholder: "title", fontSize: 36 });
      s.addText(sp.text, { placeholder: "body", fontSize: 16 });
      if (sp.notes) s.addNotes(sp.notes);
    },
  };

  let section = "Introduction";
  for (const sp of deck.slides) {
    if (sp.type === "section") { pres.addSection({ title: sp.title }); section = B.section(sp); continue; }
    if (sp.type === "cover") { pres.addSection({ title: "Introduction" }); B.cover(sp); continue; }
    if (sp.type === "closing") { pres.addSection({ title: "Takeaway" }); B.closing(sp); continue; }
    if (sp.type === "quote") { B.quote(Object.assign({ section }, sp)); continue; }
    B[sp.type](sp, section);
  }
  const out = path.join(__dirname, deck.file);
  return pres.writeFile({ fileName: out }).then(() => {
    // drop folder entries from the zip: some cloud services refuse files that have them
    try { require("child_process").execSync(`zip -dq "${out}" '*/'`); } catch (e) { /* none present */ }
    console.log("wrote", out);
  });
}

(async () => { for (const d of DECKS) await build(d); })();
