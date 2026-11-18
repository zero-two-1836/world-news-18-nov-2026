#!/usr/bin/env python3
"""Sum up 18 November 2026 world news in one image.

make.fun bounty: "Sum up 18 November's world news in one image" ($250).
Entry: a deterministic program that writes ONE image summarising the
world news of Wednesday, 18 November 2026.

This program is stdlib-only (no third-party imports, no network access)
and fully deterministic: same input -> byte-identical PNG every run.
It renders a 1600x1160 news infographic (6 top stories + an
"also today" strip) with a hand-built 5x7 bitmap font and a pure-Python
PNG encoder (zlib + struct), then writes it to:

    /output/entry.png          (primary, when /output is writable)
    output/entry.png           (fallback, next to this script)

Run:  python3 main.py
"""

import os
import struct
import zlib

# ---------------------------------------------------------------- canvas
W, H = 1600, 1160

PAPER = (244, 241, 234)      # off-white paper background
NAVY = (11, 31, 58)          # header / footer band
RED = (198, 32, 32)          # accent
INK = (20, 28, 40)           # headline text
BODY = (58, 64, 78)          # summary text
MUTED = (96, 102, 116)       # secondary text
CARD = (255, 255, 255)       # card background
CARD_LINE = (214, 210, 202)  # card border
STRIP = (228, 234, 242)      # "also today" strip background
WHITE = (255, 255, 255)
LIGHT = (178, 190, 208)      # light text on navy

# ---------------------------------------------------------------- 5x7 font
# Each glyph: 7 rows of 5 cells, '#' = ink, '.' = empty.
FONT = {
    'A': (".###.", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    'B': ("####.", "#...#", "#...#", "####.", "#...#", "#...#", "####."),
    'C': (".####", "#....", "#....", "#....", "#....", "#....", ".####"),
    'D': ("####.", "#...#", "#...#", "#...#", "#...#", "#...#", "####."),
    'E': ("#####", "#....", "#....", "####.", "#....", "#....", "#####"),
    'F': ("#####", "#....", "#....", "####.", "#....", "#....", "#...."),
    'G': (".####", "#....", "#....", "#.###", "#...#", "#...#", ".###."),
    'H': ("#...#", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    'I': ("#####", "..#..", "..#..", "..#..", "..#..", "..#..", "#####"),
    'J': ("..###", "...#.", "...#.", "...#.", "...#.", "#..#.", ".##.."),
    'K': ("#...#", "#..#.", "#.#..", "##...", "#.#..", "#..#.", "#...#"),
    'L': ("#....", "#....", "#....", "#....", "#....", "#....", "#####"),
    'M': ("#...#", "##.##", "#.#.#", "#.#.#", "#...#", "#...#", "#...#"),
    'N': ("#...#", "##..#", "##..#", "#.#.#", "#..##", "#..##", "#...#"),
    'O': (".###.", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    'P': ("####.", "#...#", "#...#", "####.", "#....", "#....", "#...."),
    'Q': (".###.", "#...#", "#...#", "#...#", "#.#.#", "#..#.", ".##.#"),
    'R': ("####.", "#...#", "#...#", "####.", "#.#..", "#..#.", "#...#"),
    'S': (".####", "#....", "#....", ".###.", "....#", "....#", "####."),
    'T': ("#####", "..#..", "..#..", "..#..", "..#..", "..#..", "..#.."),
    'U': ("#...#", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    'V': ("#...#", "#...#", "#...#", "#...#", "#...#", ".#.#.", "..#.."),
    'W': ("#...#", "#...#", "#...#", "#.#.#", "#.#.#", "##.##", "#...#"),
    'X': ("#...#", "#...#", ".#.#.", "..#..", ".#.#.", "#...#", "#...#"),
    'Y': ("#...#", "#...#", ".#.#.", "..#..", "..#..", "..#..", "..#.."),
    'Z': ("#####", "....#", "...#.", "..#..", ".#...", "#....", "#####"),
    '0': (".###.", "#..##", "#.#.#", "##..#", "#...#", "#...#", ".###."),
    '1': ("..#..", ".##..", "..#..", "..#..", "..#..", "..#..", ".###."),
    '2': (".###.", "#...#", "....#", "...#.", "..#..", ".#...", "#####"),
    '3': ("####.", "....#", "....#", ".###.", "....#", "....#", "####."),
    '4': ("...#.", "..##.", ".#.#.", "#..#.", "#####", "...#.", "...#."),
    '5': ("#####", "#....", "####.", "....#", "....#", "#...#", ".###."),
    '6': (".###.", "#....", "#....", "####.", "#...#", "#...#", ".###."),
    '7': ("#####", "....#", "...#.", "...#.", "..#..", "..#..", "..#.."),
    '8': (".###.", "#...#", "#...#", ".###.", "#...#", "#...#", ".###."),
    '9': (".###.", "#...#", "#...#", ".####", "....#", "....#", ".###."),
    'a': (".....", ".....", ".###.", "....#", ".####", "#...#", ".####"),
    'b': ("#....", "#....", "####.", "#...#", "#...#", "#...#", "####."),
    'c': (".....", ".....", ".####", "#....", "#....", "#....", ".####"),
    'd': ("....#", "....#", ".####", "#...#", "#...#", "#...#", ".####"),
    'e': (".....", ".....", ".###.", "#...#", "#####", "#....", ".###."),
    'f': ("..##.", ".#..#", ".#...", "###..", ".#...", ".#...", ".#..."),
    'g': (".....", ".####", "#...#", "#...#", ".####", "....#", ".###."),
    'h': ("#....", "#....", "####.", "#...#", "#...#", "#...#", "#...#"),
    'i': ("..#..", ".....", ".##..", "..#..", "..#..", "..#..", ".###."),
    'j': ("...#.", ".....", "..##.", "...#.", "...#.", "...#.", "...#."),
    'k': ("#....", "#....", "#..#.", "#.#..", "##...", "#.#..", "#..#."),
    'l': (".##..", "..#..", "..#..", "..#..", "..#..", "..#..", ".###."),
    'm': (".....", ".....", "##.#.", "#.#.#", "#.#.#", "#.#.#", "#.#.#"),
    'n': (".....", ".....", "####.", "#...#", "#...#", "#...#", "#...#"),
    'o': (".....", ".....", ".###.", "#...#", "#...#", "#...#", ".###."),
    'p': (".....", ".....", "####.", "#...#", "#...#", "####.", "#...."),
    'q': (".....", ".....", ".####", "#...#", "#...#", ".####", "....#"),
    'r': (".....", ".....", "#.##.", "##..#", "#....", "#....", "#...."),
    's': (".....", ".....", ".####", "#....", ".###.", "....#", "####."),
    't': (".#...", ".#...", "###..", ".#...", ".#...", ".#...", "..##."),
    'u': (".....", ".....", "#...#", "#...#", "#...#", "#..##", ".##.#"),
    'v': (".....", ".....", "#...#", "#...#", "#...#", ".#.#.", "..#.."),
    'w': (".....", ".....", "#...#", "#.#.#", "#.#.#", "#.#.#", ".#.#."),
    'x': (".....", ".....", "#...#", ".#.#.", "..#..", ".#.#.", "#...#"),
    'y': (".....", "#...#", "#...#", "#...#", ".####", "....#", ".###."),
    'z': (".....", ".....", "#####", "...#.", "..#..", ".#...", "#####"),
    ' ': (".....", ".....", ".....", ".....", ".....", ".....", "....."),
    '.': (".....", ".....", ".....", ".....", ".....", ".##..", ".##.."),
    ',': (".....", ".....", ".....", ".....", ".##..", ".##..", ".#..."),
    ':': (".....", ".##..", ".##..", ".....", ".##..", ".##..", "....."),
    ';': (".....", ".##..", ".##..", ".....", ".##..", ".##..", ".#..."),
    '!': ("..#..", "..#..", "..#..", "..#..", "..#..", ".....", "..#.."),
    '?': (".###.", "#...#", "....#", "...#.", "..#..", ".....", "..#.."),
    "'": ("..#..", "..#..", ".#...", ".....", ".....", ".....", "....."),
    '"': (".#.#.", ".#.#.", ".#.#.", ".....", ".....", ".....", "....."),
    '-': (".....", ".....", ".....", "#####", ".....", ".....", "....."),
    '(': ("...#.", "..#..", ".#...", ".#...", ".#...", "..#..", "...#."),
    ')': (".#...", "..#..", "...#.", "...#.", "...#.", "..#..", ".#..."),
    '/': ("....#", "....#", "...#.", "..#..", ".#...", "#....", "#...."),
    '%': ("#...#", "#..#.", "...#.", "..#..", ".#...", "#..#.", "#...#"),
    '$': ("..#..", ".####", "#.#..", ".###.", "..#.#", "####.", "..#.."),
    '&': (".##..", "#..#.", "#..#.", ".#...", "#.#.#", "#..#.", ".##.#"),
    '+': (".....", "..#..", "..#..", "#####", "..#..", "..#..", "....."),
    '=': (".....", ".....", "#####", ".....", "#####", ".....", "....."),
    '#': (".#.#.", ".#.#.", "#####", ".#.#.", "#####", ".#.#.", ".#.#."),
    '@': (".###.", "#...#", "#.###", "#.#.#", "#.##.", "#....", ".###."),
    '*': (".....", ".#.#.", "..#..", "#####", "..#..", ".#.#.", "....."),
    '_': (".....", ".....", ".....", ".....", ".....", ".....", "#####"),
    '•': (".....", ".....", ".###.", ".###.", ".###.", ".....", "....."),
}

_NORMALISE = {
    "\u2014": "-", "\u2013": "-", "\u2019": "'", "\u2018": "'",
    "\u201c": '"', "\u201d": '"', "\u2026": "...",
}


def _norm(text):
    return "".join(_NORMALISE.get(ch, ch) for ch in text)


def text_width(text, scale):
    """Pixel width of text at the given scale (6 units per glyph)."""
    if not text:
        return 0
    return len(text) * 6 * scale - scale


def wrap_text(text, max_w, scale):
    """Greedy word wrap; returns a list of lines fitting max_w pixels."""
    unit = 6 * scale
    lines, cur = [], ""
    for word in text.split(" "):
        trial = word if not cur else cur + " " + word
        if len(trial) * unit - scale <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


# ---------------------------------------------------------------- drawing
def fill_rect(buf, x, y, w, h, color):
    x0, y0 = max(0, x), max(0, y)
    x1, y1 = min(W, x + w), min(H, y + h)
    if x1 <= x0 or y1 <= y0:
        return
    row = bytes(color) * (x1 - x0)
    for yy in range(y0, y1):
        i = (yy * W + x0) * 3
        buf[i:i + (x1 - x0) * 3] = row


def fill_circle(buf, cx, cy, r, color):
    for dy in range(-r, r + 1):
        dx = int((r * r - dy * dy) ** 0.5)
        fill_rect(buf, cx - dx, cy + dy, 2 * dx + 1, 1, color)


def draw_text(buf, x, y, text, scale, color):
    """Draw text with the 5x7 bitmap font; returns pixel width drawn."""
    text = _norm(text)
    cx = x
    for ch in text:
        rows = FONT.get(ch, FONT['?'])
        for gy, row in enumerate(rows):
            for gx, cell in enumerate(row):
                if cell == '#':
                    fill_rect(buf, cx + gx * scale, y + gy * scale,
                              scale, scale, color)
        cx += 6 * scale
    return cx - x - scale


# ---------------------------------------------------------------- png out
def _chunk(kind, data):
    out = struct.pack(">I", len(data)) + kind + data
    out += struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)
    return out


def png_bytes(buf):
    raw = bytearray()
    for y in range(H):
        raw.append(0)  # filter: none
        raw += buf[y * W * 3:(y + 1) * W * 3]
    ihdr = struct.pack(">IIBBBBB", W, H, 8, 2, 0, 0, 0)
    return (b"\x89PNG\r\n\x1a\n"
            + _chunk(b"IHDR", ihdr)
            + _chunk(b"IDAT", zlib.compress(bytes(raw), 9))
            + _chunk(b"IEND", b""))


# ---------------------------------------------------------------- content
# World news of Wednesday, 18 November 2026, as reported by wire reports
# and major outlets on the day (US-Iran escalation, Kerch Bridge,
# Gaza winter crisis, COP31 Antalya, Trump in Manila, Pattinson as Bond).
STORIES = [
    ("1", "CONFLICT", RED, "US-IRAN WAR ESCALATES",
     "US sinks five Iranian tankers; Iran strikes ships near Hormuz "
     "and fires missiles at a US base in Jordan."),
    ("2", "WAR", (196, 88, 16), "UKRAINE HITS KERCH BRIDGE AGAIN",
     "Second night of strikes on the Crimea link as Russia hits "
     "bridges ahead of Thursday's summit."),
    ("3", "CRISIS", (0, 122, 122), "GAZA FACES A FREEZING WINTER",
     "UN warns of more deaths from cold; 1.7M displaced, 1.4M face "
     "acute hunger as aid access is urged."),
    ("4", "CLIMATE", (28, 128, 64), "COP31 TALKS ENTER FINAL DAYS",
     "Negotiators in Antalya work through 144 disputed items before "
     "the summit ends on Friday."),
    ("5", "POLITICS", (32, 84, 180), "TRUMP LANDS IN MANILA FOR QUAD",
     "Trump arrives for Quad talks ahead of a China visit; a "
     "would-be assassin is jailed for 27 years."),
    ("6", "CULTURE", (118, 62, 158), "PATTINSON IS THE NEW JAMES BOND",
     "Robert Pattinson is named the next 007, taking over the role "
     "from Daniel Craig."),
]

ALSO_LINES = [
    "ALSO TODAY: North Korea fires a missile into the sea  \u2022  "
    "Romania hit by a 5.3-magnitude quake",
    "Waymo pulls its robotaxis from US freeways  \u2022  US measles "
    "cases hit a 40-year high  \u2022  Eisenkot tapped to lead Israel",
]


def build():
    buf = bytearray(bytes(PAPER) * (W * H))

    # ---- header band
    fill_rect(buf, 0, 0, W, 150, NAVY)
    fill_rect(buf, 0, 150, W, 6, RED)
    draw_text(buf, 48, 42, "WORLD NEWS", 6, WHITE)
    draw_text(buf, 48, 104, "THE WORLD IN ONE IMAGE", 2, LIGHT)
    date = "WEDNESDAY, 18 NOVEMBER 2026"
    draw_text(buf, W - 48 - text_width(date, 3), 44, date, 3, WHITE)
    sub = "6 STORIES IN ONE IMAGE"
    draw_text(buf, W - 48 - text_width(sub, 2), 104, sub, 2, LIGHT)

    # ---- subhead
    draw_text(buf, 48, 168,
              "Six stories shaping the world today - from the Gulf to Gaza, "
              "Kyiv to Antalya.", 2, MUTED)

    # ---- story cards: 2 columns x 3 rows
    card_w, card_h, gap = 736, 250, 32
    for i, (num, tag, color, head, summ) in enumerate(STORIES):
        cx = 48 + (i % 2) * (card_w + gap)
        cy = 208 + (i // 2) * (card_h + 28)
        fill_rect(buf, cx, cy, card_w, card_h, CARD)
        # border
        fill_rect(buf, cx, cy, card_w, 2, CARD_LINE)
        fill_rect(buf, cx, cy + card_h - 2, card_w, 2, CARD_LINE)
        fill_rect(buf, cx, cy, 2, card_h, CARD_LINE)
        fill_rect(buf, cx + card_w - 2, cy, 2, card_h, CARD_LINE)
        # category colour bar
        fill_rect(buf, cx, cy, card_w, 10, color)
        # number badge
        bx, by = cx + 52, cy + 56
        fill_circle(buf, bx, by, 26, color)
        nw = text_width(num, 3)
        draw_text(buf, bx - nw // 2, by - 10, num, 3, WHITE)
        # category tag, right aligned
        draw_text(buf, cx + card_w - 28 - text_width(tag, 2), cy + 46,
                  tag, 2, color)
        # headline (max 2 lines)
        lines = wrap_text(head, card_w - 56, 3)[:2]
        hy = cy + 100
        for ln in lines:
            draw_text(buf, cx + 28, hy, ln, 3, INK)
            hy += 30
        # summary (max 3 lines)
        sy = hy + 12
        for ln in wrap_text(summ, card_w - 56, 2)[:3]:
            draw_text(buf, cx + 28, sy, ln, 2, BODY)
            sy += 20

    # ---- "also today" strip
    fill_rect(buf, 48, 1028, W - 96, 68, STRIP)
    draw_text(buf, 72, 1040, ALSO_LINES[0], 2, INK)
    draw_text(buf, 72, 1066, ALSO_LINES[1], 2, INK)

    # ---- footer band
    fill_rect(buf, 0, 1108, W, 52, NAVY)
    foot = ("Sources: wire reports and major outlets, 18 November 2026   "
            "\u2022   One image, six stories   \u2022   Deterministic build - no network")
    draw_text(buf, (W - text_width(foot, 2)) // 2, 1128, foot, 2, LIGHT)

    return png_bytes(buf)


def main():
    data = build()
    here = os.path.dirname(os.path.abspath(__file__))
    targets = ["/output/entry.png",
               os.path.join(here, "output", "entry.png")]
    written = []
    for path in targets:
        try:
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, "wb") as fh:
                fh.write(data)
            written.append(path)
        except OSError:
            pass
    if not written:
        raise SystemExit("could not write entry.png to any output path")
    print("wrote %s (%dx%d, %d bytes)" % (", ".join(written), W, H, len(data)))


if __name__ == "__main__":
    main()
