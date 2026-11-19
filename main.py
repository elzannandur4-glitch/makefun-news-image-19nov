#!/usr/bin/env python3
"""Sum up 19 November 2026 world news in one image (make.fun bounty).

Renders a 1024x1024 newspaper-style summary image: masthead with the date,
then 8 top stories of Thursday 19 November 2026 (politics, tech, games,
conflict, law, science, culture), each with a category chip, a headline and
one summary line, plus a sources footer.

Standard library only. No network access, no randomness, no clock: the same
input always produces byte-identical output. Writes entry.png to
$MAKEFUN_OUTPUT_DIR (default /output).

News facts (verified 19 Nov 2026 from Reuters, BBC, CNN, Polygon,
Popular Science, Artnet): Trump/Xi/Putin trilateral at APEC Shenzhen;
Anthropic IPO $81.3B at $83/share; GTA VI global launch; Israeli tanks
cross Gaza Yellow Line; Crimean Bridge attacked a third time in a week;
ICJ verdict in the Rohingya case; Voyager 1 one light-day out;
Van Gogh $190.4M auction record. No outcome is invented for the
Shenzhen summit or the ICJ verdict, both of which were still
pending when the news was researched.
"""

import base64
import os
import struct
import zlib

FONTS = {
    'title': (' 01269BEMNORV', 81, [24, 48, 48, 48, 48, 48, 52, 47, 68, 57, 58, 53, 53],
        'eNrtWVGOHCkMpVQr8ckROApHo6Q9yBwlRPnIZ44QpL1ARftDtAhiP0NNwXRPensTrXqSUus99zQF2BhjM0r9fv7jYxPBUiuhrjUo'
        'ZWqNSrla6Qdfa+5Yay3ckJouNbmq1hpN3Qh13XQN+NDXIH8cURrTi9Ey7j8WpedL407TC+P0WAvRSLQb9BULiDXEMmIl5fZHXWtW'
        'kfQqUOVmtIyBkbzl8ZDXN/xrfMSHdgLWt2LtSAlyW/JexgTMwHLCqnRht9Y7eb3Sgd7eNBmubn8AFe+A19BiSwi68ow+w+EkuDCu'
        'mJzm3UTNAybKHXg05w03NDS3NoQW2334mLt4xcQdtMcWXRHBNNAALdABfYtvysN6Bm6ycMBEX4Lh6FcPuBZGXgZTPb1n4EsGvmTg'
        'RQZeBNw6JsthlgIvoYTcICF3GVFfwbVhOD74iTCxT8ra+a5dgaYZWkvE3mGTCPts/Yx7sAenzIqIbaCF7efyjpiWgBk7PcMFCu8I'
        '3sU1WEZaiE3QtK8KK/IKxo4blk+QeiOkniOP0hHnZlSCHuiAtn5F0PnCTlX/bK4VLrpZjyTkj4rP4sC7fMlryzREuwTcgbFFtkW2'
        'LxafRkxHvw//rKLZKkss6wqiv65yNskCDLQ/E61VYloGUq/Q0bK9vg9dh/PofS7q0lzae+hs7SNkkG9UQO775AeCb1Of4ugTpWH0'
        'cdYyzywU1Ft6RL978Rz8b0cJMvfhfSOOo3PSfg/+CoUc7w4le79wTB2EKlHyLGwUca8IFIYngQP9JCxN2JvwmQQPIa2T8CnrMgof'
        's8kilCZ8KCaJUO0kvK/v9lEINP4kePpcESh/nAQ6HyfBlKuCzrPA2ehPEH4/hyvvsIocImfOE5fGdeZt4jBxnHifOAl/7pyFP3Uu'
        'wh8bf6gjv0fi88yBfhnY/9X4b2HX+R9h21mOMkrPRtYTrxMvE6uZfWM3sZ3YvLFj81YPjHI7hgQTqfbWzqDYis5dSZ2VpeZGQy85'
        'B7JiyU835oUauebHBhnKjkpYn2ThgOrMgJOkxxcY5TalVD+Lr43b59XnOc//WRY9FzKKQxkgdjjs0u3U7dbt2O3a7dztTg1zW5fw'
        'i/gf7LPWXsz2HLZeLAZe1gRUw52y+Sir01P8myjKe1F6CdLnUAzUoT5JR5J9+pbVi7Iherwe7bnPqPtA8TTdY9ZjJZOHyqJcqiwk'
        'xbWd+MZXmU5v14XY7LSAHhR9FnsLOVBwuNHpZHFltI3E291W1YgrdVuw591BODHG0i7jSsknRAZcT+wKdxVpOZFPuHjyeT2Rw6lK'
        '/eoT2aLl2gPRxxCpEz3JPyyeikSNE60SShohOZ1JSZSZyEvIGcmJt7j/0Wm+AX5QFfQ='
    ),
    'subtitle': (' ADEGHILMNORTWY', 32, [10, 21, 22, 18, 22, 22, 10, 17, 26, 22, 23, 21, 18, 29, 19],
        'eNqtlL1OxDAMx111yJgX4JTXQAI5vBMDA1Uvpw6MPAKvwQRBN9xrWLqBkUgMdKganA961XHoUgn3919i100dOwD/bVUPNTMExJiR'
        'HuRTQD0aJY32NtEKaurAULvC/LoH7RmD0qIgrAkrd0ztwjp7JX/FhPi+dP96zCAc0ENmvphdP/Gl9fEgvJXeqo3VcMMZmoSiTCwI'
        '71/XpDqSnoQn8KX5Mb57hPaZk97E+cxFz/ksy1ha33yK0II2Y9LbQbh/Sfpi3WESznSx/I+OvhwPTneRbWRPyHwS3hLeE15FVERG'
        'RKC0f3igvAn980ChzyvXQP+bNAUcw5EcXxXXL/T5GEYMFY/YDBXX+zgaevLaOIa2fP/emwR33CIWWSM3rpWdQ9kRrraT1Gpn1fW7'
        'VZdZzx9W9lxPt54k3BoE6UnLbBDU8q2jDKNeQTJ8YkOA78XK/clJ+wYs+iQk'
    ),
    'chip': ('ACEFGHILMNOPRSTUW', 23, [15, 14, 13, 13, 16, 16, 8, 13, 19, 16, 17, 14, 15, 14, 13, 16, 21],
        'eNqFkj1uwzAMhQl4UCbrAFWrHoNGhOgqPQJHD0GjqblEbtGxiw8Q5AQdCHTtIKCLBgMplQT1f8rvDbT0ZJCiAK6hGtVoLgVDhlyN'
        '6NOuldRwCZNQUSe3QqAeCG6lk4pTt48+Ilzx7Pkvl/V/3L08M1eJ7SrZClIxGmdsO1cJmg7f+rb/PXIOYri1wHw7OZwKoo3O8jas'
        'H8L6I1TvofoJ+HVRcRMs/EA62ghroTpUB/wUtoJDN39CMdgEzknLQOVYsihbYhDbQsigIta3/mvpje+NYeCmy9hIMicX+zR1W3kE'
        '9JxH9gq+sVzEPL0X2rFvpu5zOicF89wfcYdBm5Z6pRpFWBN+Ex6zzJHNiR/fsuye9b7RRdbo4C9N0JO2'
    ),
    'headline': (" $',-.013489ABCGILOPRSTVWXYabcdefghiklmnoprstuwyz", 36, [11, 21, 10, 12, 13, 12, 21, 21, 21, 21, 21, 21, 24, 23, 23, 25, 12, 20, 26, 22, 24, 22, 21, 24, 34, 24, 22, 21, 22, 18, 22, 21, 14, 22, 22, 11, 20, 11, 32, 22, 21, 22, 15, 18, 15, 22, 28, 20, 18],
        'eNq1V7Fu5DYQHR2D8KpjyhTGjT8hpQMsRH+KARfXprxCkHRw4dJ/EH9HqhBx4TKfYAJXpDwGKULglGXekNq9tb17J+2uyUdhVyIp'
        'cTjz5pHoxcrFCLUkkxwnZy9dfXFeXxBgPbHc73Vy1Hl65+nSn176xTtv0TP1ZvllBsGOcvKkvlThdX2LukA9mzHa+lJf4nt4Qu8q'
        'khZrE6feGldrQaP8VpSn6IbOGIKBGD69qIHMCm8aomkwya8x/V06ihdxXteP3JNZgcXr8CUqAfjrSAtOtTtj8S4AA/WcdVGXkagC'
        'Hkg9kL4lzWTgEkwnTAum90y/MHXJryHbs8bkUg2kk0QHooZvHOuMG5fjRR7JfWwTNmsFqz3nKEMfLHzGuzZ8I8/5fFrZFJ28+sfD'
        'hj9od8K9dE6yxSrMseFSUGUbYl/UJ4H+5PS9wNx7c+UZqAKnYFMsaGloqAEGamdESLFSwvcHVkHmLMDv5L88qiLTCvidotyUR/2c'
        'AHdViipFnaLxZ9y/xm5bovoZbPGF/jW66TwEAzF8NgGATKokDi6ugmDzC8z6XfYyvENeVVq1fNQs7rK0vsaYGmMRJ2mZ56KZBMUz'
        '6pTZ9oLs1IjZNuwc1h2w/jjaEFzS2/y9tlhoa5NneVX4JWMM7CfjZS7q+n3YfPTVkH11wyEBtXZIJ9122OEIcSGhUSxZohsM46WD'
        'yjEiYTJkzIjBapX6JfuDWOh8jAJQ8kA5vzgFAcAgFk/Knyq/0EUACEvrOTyWkl+jCrQHphcQUWEkUFNNEbBiIrGhuQI8qKxwGsit'
        'sBzorvBe4cD9CrIzU6MDoliH+tEFH8HmfSuXZvNyu4Bj/7qIm5elhcMPHJ5eFMhr47J/aam1cJUPke+iuQv6L6/yRlcg1UQFlRgE'
        'ZnF4CqCb9P8QMbCd42NDFVsVxlR1k7Pkw5gloQGQSQGKX8UBxQ5kE9D/ZERg6OLqybXQVwXGtSI5HP+LBOcmU+s2gHK6HLliq/CI'
        'JQpw8y5zBbpxf8i6RMUtRVzZ76l+tUWy4SYeiYbPQmvyvP451EdvPgvzWGQkvVWRyiPRIZ+9/niQioYzbMrgMv9arcm66BxMlXUU'
        'PHbKiqJBXeW5FKQekge3vGGOfdAZJhWRlgU82H6Xyt3hY/0jH6u+gTkqYYpm2CsuEPhGHJ6RmducWXAuCPk65Ds2r8uMGe24yobp'
        '0MLyWd0NAvch8n0c+Co0SMWT21HOk0ff969zy7MYfHICXR8/Z51ltq1rHmfOVVb8llteov4xasIj+IbBgWApaN5Q8yqfO/MdkK2k'
        'TqZzHDMtdUvqBvHzuWo9RalbfRlMpvdKiN90GJGR18GkoP8L6u9ARyqNUb7la1/ztVs1/vlPaX1uvz30JuCkutG0b9ftGGUAJ2vJ'
        '+DX8GccDeAJMeUvmd0mOOFxDx6qCKMftojbBQ5C9DPE7J1F3aYS4RZY3mFMHkc8mzwZp3W1221H+B5hTt3k='
    ),
    'summary': (" $',-.13689ABCEFGHIJMNOPRSTYZabcdefghijklmnoprstuvwyz", 27, [7, 14, 7, 7, 8, 7, 14, 14, 14, 14, 14, 16, 16, 16, 14, 13, 18, 17, 7, 7, 19, 17, 18, 14, 16, 14, 14, 14, 16, 14, 14, 13, 14, 14, 8, 14, 14, 7, 7, 13, 7, 22, 14, 14, 14, 10, 12, 9, 14, 14, 18, 14, 12],
        'eNqNVc1u1DAQnihVcgnrHoMI6/AGjiK1Rgo1vIk5ceFgbj2gxg/Ay/AGlrjyEK54AMJtD6uWGWfbbjZ/O98n7Tr2eOzx+DPAqkUB'
        'zPPu/WUFFXwA7tIuklEe5e+k6pjrRxyZCLY+dZ7nohx/vrtb8zr9xEBBDfEkVKe66YkUtE570AGOWebwVxA+mtYrO+2VOu7zkoZp'
        '+GJbf6uNIAghNfdsxotZ5Y3RgiA0d9wJ3beMUUteTnittSEI3AnrA+vSKcdnEhTb2CYucRuf6UzngqB2amcKbGYumcmGUz5sgwzX'
        'hC0hemc8ZeVmYnVsV2TyQhzS2EOAvCgytovnMo87EfCEEOulNX9ew3GYgZcWYcFiD2wHRQbiggbqnneBCVEkIBMoNsD2MLfqQYln'
        'E1R74mTX3DQnttAljB+fQZPanleviNdvbf2aWP0M/GfFfWB04Oq+ZAZN4E0GVxnUgdUPovgd+BXEdxBNYLGeqEPmC5AbSrKOT0mZ'
        '39AAHIaDl2xQon2RuvUCGBU2Xim6hYfynjkbhl6m7Mv5FpRlHkwfRqM48JlMPu4f9zHMY9p8YSQuRhc+c6lN7Xle7b7dQ44rMuAj'
        'F6FXCpjI8Cn0LRpHaSlR/DheKoMKo/03/LfVk1X6jBqz0hgpD8KQS9lgRmu3HIuhZMrSPMuDAVmiVE57PQdjgneyexJNEkrZcRLA'
        '5VgWY6FWatF2bRdiXaLXqLAYx/N/eJi8esOBc8vAxJdYTMelMEyUNKM7LCYEYHjVF7rQvJ+IhcXtK1dbBQ3cwDXUtqISN2tis/5C'
        '17+c+uvl7cRGzp+E5jkzG6OjdNIPMu+5Y3Y91lSJLssEZs9KkCDg7DeFLhEKg7FUZApXCw7cJ9fiOczKfUCLOI2jgK+9OCOTZv06'
        '4PPfK53O8eknkMCkFs6zz/cWWf0BZF1DfQ1vrojbLXFTEM+xfhnSPC2jXwRpW4JoEJMK51sPpGz2SNno25H9BzJIcPw='
    ),
    'footer': (' -:ABCNPRSacegilnoprstuy', 19, [6, 6, 6, 11, 11, 12, 12, 10, 12, 11, 10, 9, 10, 11, 5, 5, 11, 10, 11, 7, 9, 7, 11, 10],
        'eNp9kU1uwjAQhR9qFxWqFCp1iaIxXIJFC2PEgiUHQCgRF+iyKzxH6VFyrC77QvPnKOZ9UmQ7byYvY+CBvkd7kf75r2cyJ29ETGxn'
        'SpnEdQFa1edaBWtWNIVR98wWlUAHCBZVZrGrkBM5yoHsxRP9IUXsusFDrcZz3XdMu0K7pmJXjmtTvUGGmYGu0raTE8uxxgw7lOzm'
        'WfeZcLlBJsf9lJZY3buEh67cnGmHs5z5Oi9/RVuhPdLxUacLc6sNSabvv5jIFfcquY9v4FwkQmzri0CBDzxxlB7xoFV/m7rNuDBO'
        'fp/EhMzqmTrOdoV38ooX8sU3fxCVWyc='
    ),
}


# ---------------------------------------------------------------- fonts

def _decode_font(entry):
    """Decode one embedded bitmap font.

    Entry: (charset, height, widths, b64(zlib(packed bits))).
    Packed bits: glyphs in charset order; each glyph is `height` rows,
    each row ceil(width/8) bytes, MSB-first, 1 = ink.
    Returns (height, {char: (width, [(dx, dy), ...ink pixels...])}).
    """
    charset, height, widths, b64 = entry
    raw = zlib.decompress(base64.b64decode(b64))
    glyphs = {}
    off = 0
    for ch, w in zip(charset, widths):
        rb = (w + 7) // 8
        ink = []
        for y in range(height):
            base = off + y * rb
            for x in range(w):
                if (raw[base + x // 8] >> (7 - x % 8)) & 1:
                    ink.append((x, y))
        glyphs[ch] = (w, ink)
        off += height * rb
    return height, glyphs


_FONTS = {name: _decode_font(e) for name, e in FONTS.items()}


def text_width(font, text, tracking=1):
    """Pixel width of `text` in `font` (unknown chars count as a space)."""
    _, glyphs = _FONTS[font]
    space_w = glyphs.get(" ", (10, ()))[0]
    w = 0
    for ch in text:
        g = glyphs.get(ch)
        w += (g[0] if g is not None else space_w) + tracking
    return max(0, w - tracking)


def draw_text(canvas, W, H, x, y, text, font, color, tracking=1):
    """Blit `text` with its top at (x, y). Returns the x after the text."""
    _, glyphs = _FONTS[font]
    space_w = glyphs.get(" ", (10, ()))[0]
    cx = x
    r, g, b = color
    for ch in text:
        ent = glyphs.get(ch)
        if ent is None:
            cx += space_w + tracking
            continue
        w, ink = ent
        for dx, dy in ink:
            px, py = cx + dx, y + dy
            if 0 <= px < W and 0 <= py < H:
                i = (py * W + px) * 3
                canvas[i] = r
                canvas[i + 1] = g
                canvas[i + 2] = b
        cx += w + tracking
    return cx


# ---------------------------------------------------------------- canvas

def fill_rect(canvas, W, H, x0, y0, x1, y1, color):
    """Fill an axis-aligned rectangle (clipped to the canvas)."""
    x0 = max(0, x0)
    y0 = max(0, y0)
    x1 = min(W, x1)
    y1 = min(H, y1)
    if x1 <= x0 or y1 <= y0:
        return
    row = bytes(color) * (x1 - x0)
    for y in range(y0, y1):
        base = (y * W + x0) * 3
        canvas[base:base + len(row)] = row


def fill_round_rect(canvas, W, H, x0, y0, x1, y1, radius, color):
    """Fill a rectangle with rounded corners."""
    fill_rect(canvas, W, H, x0, y0, x1, y1, color)
    bg = (255, 255, 255)
    for cx, cy, sx, sy in ((x0 + radius, y0 + radius, -1, -1),
                           (x1 - radius - 1, y0 + radius, 1, -1),
                           (x0 + radius, y1 - radius - 1, -1, 1),
                           (x1 - radius - 1, y1 - radius - 1, 1, 1)):
        for dy in range(radius):
            for dx in range(radius):
                if (dx + 0.5) * (dx + 0.5) + (dy + 0.5) * (dy + 0.5) > radius * radius:
                    px, py = cx + sx * dx, cy + sy * dy
                    if 0 <= px < W and 0 <= py < H:
                        i = (py * W + px) * 3
                        canvas[i] = bg[0]
                        canvas[i + 1] = bg[1]
                        canvas[i + 2] = bg[2]


def hline(canvas, W, H, x0, x1, y, color):
    """1px horizontal line."""
    fill_rect(canvas, W, H, x0, y, x1, y + 1, color)


# ---------------------------------------------------------------- PNG

def _chunk(typ, data):
    out = struct.pack(">I", len(data)) + typ + data
    out += struct.pack(">I", zlib.crc32(typ + data) & 0xFFFFFFFF)
    return out


def encode_png(w, h, rgb):
    """Encode RGB bytes (w*h*3) as a PNG (color type 2, 8-bit, filter 0)."""
    raw = bytearray()
    stride = w * 3
    for y in range(h):
        raw.append(0)
        raw += rgb[y * stride:(y + 1) * stride]
    comp = zlib.compress(bytes(raw), 9)
    ihdr = struct.pack(">IIBBBBB", w, h, 8, 2, 0, 0, 0)
    return (b"\x89PNG\r\n\x1a\n"
            + _chunk(b"IHDR", ihdr)
            + _chunk(b"IDAT", comp)
            + _chunk(b"IEND", b""))


# ---------------------------------------------------------------- content

NAVY = (15, 42, 67)
GOLD = (242, 193, 78)
WHITE = (255, 255, 255)
INK = (17, 17, 17)
GRAY = (68, 68, 68)
LINE = (229, 224, 216)
FOOT = (119, 119, 119)

TITLE = "19 NOVEMBER 2026"
SUBTITLE = "THE WORLD TODAY IN ONE IMAGE"
FOOTER = "Sources: Reuters - BBC - CNN - Polygon - Popular Science - Artnet"

# (category, chip color, headline, summary)
NEWS = [
    ("POLITICS", (31, 78, 121),
     "Trump, Xi and Putin meet in Shenzhen",
     "Three leaders hold rare trilateral talks at the APEC summit."),
    ("TECH", (14, 124, 107),
     "Anthropic IPO raises $81.3 billion",
     "Claude maker prices shares at $83 - the biggest IPO ever."),
    ("GAMES", (122, 63, 160),
     "GTA VI launches worldwide today",
     "Rockstar's most awaited game arrives, starting in New Zealand."),
    ("CONFLICT", (176, 58, 46),
     "Israeli tanks cross Gaza's Yellow Line",
     "First ground operation in central Gaza since the ceasefire."),
    ("CONFLICT", (176, 58, 46),
     "Crimean Bridge hit for a third time",
     "Traffic halted after a new attack on the 19 km bridge."),
    ("LAW", (93, 109, 126),
     "World Court rules on Rohingya case",
     "ICJ delivers its final verdict on Myanmar at The Hague."),
    ("SCIENCE", (40, 114, 51),
     "Voyager 1 reaches one light-day out",
     "NASA probe is the first human object 16.1 billion miles away."),
    ("CULTURE", (183, 149, 11),
     "Van Gogh sells for $190.4 million",
     "Blossoming Chestnut Trees sets a new auction record in New York."),
]


def render():
    W, H = 1024, 1024
    canvas = bytearray(b"\xff" * (W * H * 3))

    # Masthead.
    fill_rect(canvas, W, H, 0, 0, W, 148, NAVY)
    fill_rect(canvas, W, H, 0, 148, W, 152, GOLD)
    tw = text_width("title", TITLE)
    draw_text(canvas, W, H, (W - tw) // 2, 16, TITLE, "title", WHITE)
    sw = text_width("subtitle", SUBTITLE)
    draw_text(canvas, W, H, (W - sw) // 2, 104, SUBTITLE, "subtitle", GOLD)

    # News rows.
    for i, (cat, chip_color, headline, summary) in enumerate(NEWS):
        y0 = 168 + i * 100
        chip_w = text_width("chip", cat) + 20
        fill_round_rect(canvas, W, H, 48, y0 + 2, 48 + chip_w, y0 + 32, 5,
                        chip_color)
        draw_text(canvas, W, H, 48 + 10, y0 + 5, cat, "chip", WHITE)
        draw_text(canvas, W, H, 48 + chip_w + 16, y0, headline, "headline", INK)
        draw_text(canvas, W, H, 48, y0 + 46, summary, "summary", GRAY)
        if i < len(NEWS) - 1:
            hline(canvas, W, H, 48, 976, y0 + 88, LINE)

    # Footer: a rule above the sources line, mirroring the dividers
    # between rows, so the footer is anchored instead of floating in
    # the whitespace below the last story.
    hline(canvas, W, H, 48, 976, 962, LINE)
    fw = text_width("footer", FOOTER)
    draw_text(canvas, W, H, (W - fw) // 2, 980, FOOTER, "footer", FOOT)

    return W, H, bytes(canvas)


def main():
    outdir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(outdir, exist_ok=True)
    w, h, rgb = render()
    data = encode_png(w, h, rgb)
    path = os.path.join(outdir, "entry.png")
    with open(path, "wb") as f:
        f.write(data)
    print("wrote %s (%d bytes, %dx%d)" % (path, len(data), w, h))


if __name__ == "__main__":
    main()
