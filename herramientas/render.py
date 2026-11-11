"""Convierte caps/*.txt (salida real con códigos ANSI) en PNG con aspecto de ventana de Terminal."""
import re, sys, textwrap
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

S = Path(__file__).resolve().parent
FONT = "/System/Library/Fonts/Menlo.ttc"
SIZE, COLS, PAD, BAR, MAXROWS = 26, 100, 28, 56, 52
f_reg = ImageFont.truetype(FONT, SIZE, index=0)
f_bold = ImageFont.truetype(FONT, SIZE, index=1)
CW = f_reg.getlength("M")
LH = int(SIZE * 1.42)
BG, FG = (30, 32, 40), (225, 228, 235)
PAL = {30: (90, 90, 100), 31: (255, 107, 107), 32: (110, 220, 140), 33: (240, 200, 90), 34: (110, 160, 255),
       35: (200, 140, 255), 36: (90, 210, 220), 37: (225, 228, 235)}
for k in range(30, 38):
    PAL[k + 60] = tuple(min(255, v + 30) for v in PAL[k])
SGR = re.compile(r"\x1b\[([0-9;]*)m")
OTHER = re.compile(r"\x1b\[[0-9;?]*[A-Za-ln-z]|\r")


def parse(line, st):
    """Devuelve lista de (texto, color, bold) y el estado final."""
    segs, pos = [], 0
    for m in SGR.finditer(line):
        if m.start() > pos:
            segs.append((line[pos:m.start()], st[0], st[1]))
        for c in (m.group(1) or "0").split(";"):
            c = int(c or 0)
            if c == 0: st = (FG, False)
            elif c == 1: st = (st[0], True)
            elif c == 22: st = (st[0], False)
            elif c == 39: st = (FG, st[1])
            elif c in PAL: st = (PAL[c], st[1])
        pos = m.end()
    if pos < len(line):
        segs.append((line[pos:], st[0], st[1]))
    return segs, st


def wrap(segs):
    rows, cur, n = [], [], 0
    for t, col, b in segs:
        t = t.replace("\t", "    ")
        while t:
            room = COLS - n
            if room <= 0:
                rows.append(cur); cur, n = [], 0; room = COLS
            part, t = t[:room], t[room:]
            cur.append((part, col, b)); n += len(part)
    rows.append(cur)
    return rows


def render(txt, png, title):
    raw = open(txt, encoding="utf-8", errors="replace", newline="").read().rstrip("\n").split("\n")
    # \r: como en una terminal real, lo que va después sobrescribe la línea
    raw = [OTHER.sub("", [p for p in l.split("\r") if p.strip()][-1] if l.strip() else l) for l in raw]
    rows, st = [], (FG, False)
    for line in raw:
        segs, st = parse(line, st)
        rows += wrap(segs)
    if len(rows) > MAXROWS:
        parts = [rows[i:i + MAXROWS] for i in range(0, len(rows), MAXROWS)]
        for k, part in enumerate(parts):
            draw(part, png.with_name(f"{png.stem}-{'abcdefgh'[k]}.png"), title)
        return
    draw(rows, png, title)


def draw(rows, png, title):
    w = int(PAD * 2 + CW * COLS)
    h = BAR + PAD * 2 + LH * len(rows)
    img = Image.new("RGB", (w + 40, h + 40), (236, 238, 243))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle((20, 20, 20 + w, 20 + h), 18, fill=BG, outline=(70, 72, 82), width=2)
    d.rounded_rectangle((20, 20, 20 + w, 20 + BAR), 18, fill=(54, 56, 66))
    d.rectangle((20, 20 + BAR - 18, 20 + w, 20 + BAR), fill=(54, 56, 66))
    for i, c in enumerate([(255, 95, 87), (254, 188, 46), (40, 200, 64)]):
        cx = 20 + 32 + i * 34
        d.ellipse((cx - 11, 20 + BAR / 2 - 11, cx + 11, 20 + BAR / 2 + 11), fill=c)
    tw = f_reg.getlength(title)
    d.text((20 + (w - tw) / 2, 20 + BAR / 2), title, font=f_reg, fill=(200, 202, 210), anchor="lm")
    y = 20 + BAR + PAD
    for r in rows:
        x = 20 + PAD
        for t, col, b in r:
            d.text((x, y), t, font=f_bold if b else f_reg, fill=col)
            x += CW * len(t)
        y += LH
    img.save(png)


if __name__ == "__main__":
    out = S / "capturas"; out.mkdir(exist_ok=True)
    names = sys.argv[1:] or [p.stem for p in sorted((S / "evidencias").glob("*.txt"))]
    for n in names:
        render(S / "evidencias" / f"{n}.txt", out / f"{n}.png", f"{S.parent.name} — zsh")
        print("ok", n)
