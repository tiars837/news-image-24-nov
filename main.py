#!/usr/bin/env python3
"""The World in One Day -- Tuesday, 24 November 2026.

Draws a one-page newspaper poster of the day's world news and writes it
to /output/entry.png (or $MAKEFUN_OUTPUT_DIR/entry.png when testing).
Python 3.13 standard library only, no network, deterministic output.
"""

import os
import shutil
import struct
import zlib

W, H = 1024, 1024

PAPER = (247, 243, 234)
INK = (16, 22, 34)
NAVY = (16, 35, 63)
GOLD = (196, 158, 46)
RED = (176, 32, 32)
GREEN = (26, 118, 68)
GREY = (96, 102, 110)
PALE = (232, 227, 214)
WHITE = (255, 255, 255)

# 5x7 bitmap font. Each glyph is 7 rows of 5 cells; '#' is ink, '.' blank.
FONT = {
    "A": ("..#..", ".#.#.", "#...#", "#...#", "#####", "#...#", "#...#"),
    "B": ("####.", "#...#", "#...#", "####.", "#...#", "#...#", "####."),
    "C": (".####", "#....", "#....", "#....", "#....", "#....", ".####"),
    "D": ("####.", "#...#", "#...#", "#...#", "#...#", "#...#", "####."),
    "E": ("#####", "#....", "#....", "####.", "#....", "#....", "#####"),
    "F": ("#####", "#....", "#....", "####.", "#....", "#....", "#...."),
    "G": (".####", "#....", "#....", "#.###", "#...#", "#...#", ".###."),
    "H": ("#...#", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    "I": (".###.", "..#..", "..#..", "..#..", "..#..", "..#..", ".###."),
    "J": ("..###", "...#.", "...#.", "...#.", "...#.", "#..#.", ".##.."),
    "K": ("#...#", "#..#.", "#.#..", "##...", "#.#..", "#..#.", "#...#"),
    "L": ("#....", "#....", "#....", "#....", "#....", "#....", "#####"),
    "M": ("#...#", "##.##", "#.#.#", "#.#.#", "#...#", "#...#", "#...#"),
    "N": ("#...#", "##..#", "#.#.#", "#..##", "#...#", "#...#", "#...#"),
    "O": (".###.", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    "P": ("####.", "#...#", "#...#", "####.", "#....", "#....", "#...."),
    "Q": (".###.", "#...#", "#...#", "#...#", "#.#.#", "#..#.", ".##.#"),
    "R": ("####.", "#...#", "#...#", "####.", "#.#..", "#..#.", "#...#"),
    "S": (".####", "#....", "#....", ".###.", "....#", "....#", "####."),
    "T": ("#####", "..#..", "..#..", "..#..", "..#..", "..#..", "..#.."),
    "U": ("#...#", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    "V": ("#...#", "#...#", "#...#", "#...#", "#...#", ".#.#.", "..#.."),
    "W": ("#...#", "#...#", "#...#", "#.#.#", "#.#.#", "##.##", "#...#"),
    "X": ("#...#", "#...#", ".#.#.", "..#..", ".#.#.", "#...#", "#...#"),
    "Y": ("#...#", "#...#", ".#.#.", "..#..", "..#..", "..#..", "..#.."),
    "Z": ("#####", "....#", "...#.", "..#..", ".#...", "#....", "#####"),
    "0": (".###.", "#...#", "#..##", "#.#.#", "##..#", "#...#", ".###."),
    "1": ("..#..", ".##..", "..#..", "..#..", "..#..", "..#..", ".###."),
    "2": (".###.", "#...#", "....#", "...#.", "..#..", ".#...", "#####"),
    "3": ("####.", "....#", "....#", ".###.", "....#", "....#", "####."),
    "4": ("...#.", "..##.", ".#.#.", "#..#.", "#####", "...#.", "...#."),
    "5": ("#####", "#....", "####.", "....#", "....#", "#...#", ".###."),
    "6": (".###.", "#....", "####.", "#...#", "#...#", "#...#", ".###."),
    "7": ("#####", "....#", "...#.", "..#..", ".#...", ".#...", ".#..."),
    "8": (".###.", "#...#", "#...#", ".###.", "#...#", "#...#", ".###."),
    "9": (".###.", "#...#", "#...#", ".####", "....#", "....#", ".###."),
    ".": (".....", ".....", ".....", ".....", ".....", ".##..", ".##.."),
    ",": (".....", ".....", ".....", ".....", ".##..", ".##..", ".#..."),
    ":": (".....", ".##..", ".##..", ".....", ".##..", ".##..", "....."),
    ";": (".....", ".##..", ".##..", ".....", ".##..", ".##..", ".#..."),
    "!": ("..#..", "..#..", "..#..", "..#..", "..#..", ".....", "..#.."),
    "?": (".###.", "#...#", "....#", "...#.", "..#..", ".....", "..#.."),
    "%": ("##..#", "##.#.", "...#.", "..#..", ".#...", "#.##.", "#..##"),
    "+": (".....", "..#..", "..#..", ".###.", "..#..", "..#..", "....."),
    "-": (".....", ".....", ".....", ".###.", ".....", ".....", "....."),
    "(": ("...#.", "..#..", ".#...", ".#...", ".#...", "..#..", "...#."),
    ")": (".#...", "..#..", "...#.", "...#.", "...#.", "..#..", ".#..."),
    "/": ("....#", "...#.", "...#.", "..#..", ".#...", "#....", "#...."),
    "&": (".##..", "#..#.", "#..#.", ".#...", "#.#.#", "#..#.", ".##.#"),
    "$": ("..#..", ".####", "#.#..", ".###.", "..#.#", "####.", "..#.."),
    "'": ("..#..", "..#..", ".#...", ".....", ".....", ".....", "....."),
    '"': (".#.#.", ".#.#.", ".....", ".....", ".....", ".....", "....."),
    "=": (".....", ".....", "#####", ".....", "#####", ".....", "....."),
    "*": (".....", ".#.#.", "..#..", "#####", "..#..", ".#.#.", "....."),
    "<": ("...#.", "..#..", ".#...", "#....", ".#...", "..#..", "...#."),
    ">": (".#...", "..#..", "...#.", "....#", "...#.", "..#..", ".#..."),
    "_": (".....", ".....", ".....", ".....", ".....", ".....", "#####"),
    " ": (".....", ".....", ".....", ".....", ".....", ".....", "....."),
}


def text_width(s, scale):
    return len(s) * 6 * scale - scale


def wrap(text, scale, max_w):
    """Greedy word wrap; returns a list of lines that fit max_w pixels."""
    lines = []
    for chunk in text.split("\n"):
        words = chunk.split(" ")
        cur = ""
        for word in words:
            trial = word if not cur else cur + " " + word
            if text_width(trial, scale) <= max_w or not cur:
                cur = trial
            else:
                lines.append(cur)
                cur = word
        if cur:
            lines.append(cur)
    return lines


class Canvas:
    def __init__(self, w, h, bg):
        self.w, self.h = w, h
        self.px = bytearray(bg * (w * h))

    def rect(self, x, y, w, h, color):
        x0, y0 = max(0, x), max(0, y)
        x1, y1 = min(self.w, x + w), min(self.h, y + h)
        if x1 <= x0 or y1 <= y0:
            return
        row = bytes(color) * (x1 - x0)
        for yy in range(y0, y1):
            off = (yy * self.w + x0) * 3
            self.px[off:off + len(row)] = row

    def hline(self, x, y, w, color, thick=2):
        self.rect(x, y, w, thick, color)

    def text(self, x, y, s, scale, color):
        s = s.upper()
        cx = x
        for ch in s:
            glyph = FONT.get(ch, FONT[" "])
            for r in range(7):
                row = glyph[r]
                for c in range(5):
                    if row[c] == "#":
                        self.rect(cx + c * scale, y + r * scale, scale, scale, color)
            cx += 6 * scale

    def text_center(self, y, s, scale, color):
        self.text((self.w - text_width(s, scale)) // 2, y, s, scale, color)


def png_bytes(w, h, rgb):
    raw = b"".join(b"\x00" + rgb[y * w * 3:(y + 1) * w * 3] for y in range(h))

    def chunk(kind, data):
        out = struct.pack(">I", len(data)) + kind + data
        out += struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)
        return out

    ihdr = struct.pack(">IIBBBBB", w, h, 8, 2, 0, 0, 0)
    return (
        b"\x89PNG\r\n\x1a\n"
        + chunk(b"IHDR", ihdr)
        + chunk(b"IDAT", zlib.compress(raw, 9))
        + chunk(b"IEND", b"")
    )


LEAD = {
    "kicker": "LEAD - MARKETS",
    "headline": "ASIA RALLIES AS NVIDIA COMEBACK REVIVES THE AI TRADE",
    "body": (
        "Nvidia jumped 31.5% on Monday, its best day in 23 years, adding back "
        "nearly $1 trillion in value. On Tuesday the rally rolled into Asia. "
        "The S&P 500 rose 4.7% and the Nasdaq 6.5% on Monday, their best day "
        "since April 2025."
    ),
    "chart_title": "TUESDAY GAINS, %",
    "bars": [("TAIWAN", 9.1), ("KOSPI", 7.5), ("MSCI AP", 4.6), ("NIKKEI", 4.5)],
}

STORIES = [
    {
        "kicker": "UNITED STATES",
        "headline": "TWO STATES SUE MUSK'S SPACEX OVER GROK DEEPFAKES",
        "body": (
            "Virginia and Oregon filed the first state lawsuits over Grok's "
            "'spicy mode', saying it turns photos into sexual images of real "
            "people, including children. They cite a study counting about "
            "3 million such images."
        ),
    },
    {
        "kicker": "INDONESIA",
        "headline": "24 DEAD, 30 STILL MISSING AS FACTORY SEARCH GOES ON",
        "body": (
            "Rescuers kept digging through the burned Milkita candy factory "
            "in Cikande, Banten, after officials confirmed 24 dead. DNA tests "
            "to identify the victims could take weeks."
        ),
    },
    {
        "kicker": "JAPAN",
        "headline": "JAPAN'S FACTORIES PICK UP SPEED",
        "body": (
            "Manufacturing activity grew faster in November, the flash PMI "
            "rising to 53.7 on stronger output and export orders, though "
            "services eased to 50.5."
        ),
    },
    {
        "kicker": "UNITED STATES",
        "headline": "COURT CLEARS WAY FOR IOWA BLAST; TRUMP SAYS WAIT",
        "body": (
            "An appeals court lifted the hold on the Army's plan to detonate "
            "9,500 pounds of unstable lead azide on Wednesday. Trump ordered "
            "the Army to wait for the court and the governor-elect."
        ),
    },
    {
        "kicker": "SOUTH KOREA",
        "headline": "SOUTH KOREA SET TO RAISE RATES ON THURSDAY",
        "body": (
            "The central bank is expected to lift its key rate to 3.25% as a "
            "chip-led export boom fuels growth, with one more hike likely "
            "early next year."
        ),
    },
]

ALSO = [
    "FIFA NAMES 2031 WOMEN'S WORLD CUP HOSTS: US, MEXICO, COSTA RICA, JAMAICA; UK GETS 2035.",
    "DON TOLIVER'S LONDON SHOW POSTPONED TO DEC. 15 AFTER 12,000 EVACUATED IN MANCHESTER.",
    "TWO BUS DRIVERS KILLED, NINE HURT IN COLUMBUS, OHIO, CRASH.",
    "FLORIDA STATE HIRES GEORGIA'S GLENN SCHUMANN AS HEAD COACH.",
]


def draw_chart(cv, x, y, w, h):
    cv.text(x, y, LEAD["chart_title"], 1, GREY)
    base = y + h - 26
    top = y + 22
    avail = base - top
    top_val = 10.0
    bw = 52
    gap = (w - 4 * bw) // 5
    for i, (label, val) in enumerate(LEAD["bars"]):
        bx = x + gap + i * (bw + gap)
        bh = int(avail * val / top_val)
        cv.rect(bx, base - bh, bw, bh, GREEN)
        cv.text(bx + (bw - text_width("+%.1f%%" % val, 1)) // 2, base - bh - 12, "+%.1f%%" % val, 1, INK)
        cv.text(bx + (bw - text_width(label, 1)) // 2, base + 6, label, 1, INK)
    cv.hline(x, base, w, INK, 2)


def render():
    cv = Canvas(W, H, PAPER)
    mx = 36
    cw = W - 2 * mx

    # Masthead.
    cv.rect(0, 0, W, 152, NAVY)
    cv.text_center(26, "THE WORLD IN ONE DAY", 3, GOLD)
    cv.text_center(74, "TUESDAY, 24 NOVEMBER 2026", 5, WHITE)
    cv.hline(0, 152, W, GOLD, 4)

    # Lead story: text on the left, bar chart on the right.
    ly = 176
    cv.text(mx, ly, LEAD["kicker"], 2, RED)
    head_lines = wrap(LEAD["headline"], 3, 600)
    hy = ly + 28
    for line in head_lines:
        cv.text(mx, hy, line, 3, INK)
        hy += 27
    by = hy + 10
    for line in wrap(LEAD["body"], 2, 600):
        cv.text(mx, by, line, 2, INK)
        by += 17
    draw_chart(cv, 676, ly, W - mx - 676, 250)
    cv.hline(mx, 448, cw, INK, 3)

    # Stories 2-6, one row each with a number badge.
    sy = 470
    pitch = 76
    for i, st in enumerate(STORIES):
        y = sy + i * pitch
        cv.rect(mx, y + 2, 30, 30, NAVY)
        cv.text(mx + 9, y + 8, str(i + 2), 2, WHITE)
        tx = mx + 44
        cv.text(tx, y, st["kicker"], 1, RED)
        cv.text(tx, y + 12, st["headline"], 2, INK)
        blines = wrap(st["body"], 1, W - mx - tx)
        byy = y + 32
        for line in blines[:2]:
            cv.text(tx, byy, line, 1, INK)
            byy += 10
        if i < len(STORIES) - 1:
            cv.hline(mx, y + pitch - 8, cw, PALE, 2)

    # Also-today strip.
    ay = sy + len(STORIES) * pitch + 6
    cv.rect(0, ay - 8, W, 2, RED)
    cv.text(mx, ay, "ALSO TODAY", 2, RED)
    iy = ay + 26
    for item in ALSO:
        cv.text(mx, iy, "- " + item, 1, INK)
        iy += 12

    # Footer.
    fy = iy + 12
    cv.hline(mx, fy, cw, INK, 2)
    cv.text_center(fy + 10, "SOURCES: REUTERS - AP - CNN - LE MONDE", 1, GREY)
    assert fy + 24 < H, "layout overflow"
    return cv.px


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    # Empty only the contents of the output directory, never the dir itself.
    for name in os.listdir(out_dir):
        path = os.path.join(out_dir, name)
        if os.path.isdir(path) and not os.path.islink(path):
            shutil.rmtree(path)
        else:
            os.remove(path)
    data = png_bytes(W, H, bytes(render()))
    with open(os.path.join(out_dir, "entry.png"), "wb") as f:
        f.write(data)


if __name__ == "__main__":
    main()
